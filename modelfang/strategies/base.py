"""
Strategy Base Classes

Defines abstract base classes for attack strategies and utilities
for building attack graphs.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from modelfang.schema.attack import AttackSchema, AttackStep, SuccessCondition


class AttackStrategy(ABC):
    """
    Abstract base class for attack strategies.
    
    Strategies define how to generate specific layers or types of advice.
    """
    
    def __init__(self, **kwargs: Any):
        """Initialize the strategy."""
        self.config = kwargs
    
    @abstractmethod
    def generate_step(self, step_id: str, context: Dict[str, Any]) -> AttackStep:
        """
        Generate a single attack step.
        
        Args:
            step_id: ID to assign to the step
            context: Context variables for generation
            
        Returns:
            Generated AttackStep
        """
        pass


class GraphBuilder:
    """
    Utility for building complex attack graphs.
    """
    
    def __init__(self, attack_id: str, name: str):
        """Initialize the builder."""
        self.schema = AttackSchema(
            attack_id=attack_id,
            name=name,
            category=None,  # Set later
            severity=None,  # Set later
        )
        self.steps: Dict[str, AttackStep] = {}
    
    def add_step(self, step: AttackStep) -> "GraphBuilder":
        """Add a step to the graph."""
        self.steps[step.step_id] = step
        return self
    
    def connect(
        self, 
        source_id: str, 
        target_id: str, 
        condition: str
    ) -> "GraphBuilder":
        """Connect two steps with a transition condition."""
        if source_id not in self.steps:
            raise ValueError(f"Source step {source_id} not found")
        
        self.steps[source_id].transitions[condition] = target_id
        return self
    
    def on_success(self, source_id: str, target_id: str) -> "GraphBuilder":
        """Set success transition."""
        if source_id not in self.steps:
            raise ValueError(f"Source step {source_id} not found")
        
        self.steps[source_id].on_success = target_id
        return self
    
    def on_failure(self, source_id: str, target_id: str) -> "GraphBuilder":
        """Set failure transition."""
        if source_id not in self.steps:
            raise ValueError(f"Source step {source_id} not found")
        
        self.steps[source_id].on_failure = target_id
        return self
    
    def set_start(self, step_id: str) -> "GraphBuilder":
        """Set the starting step."""
        if step_id not in self.steps:
            raise ValueError(f"Step {step_id} not found")
        
        self.schema.start_step_id = step_id
        return self
    
    def build(self) -> AttackSchema:
        """Build and return the final schema."""
        self.schema.steps = list(self.steps.values())
        return self.schema
