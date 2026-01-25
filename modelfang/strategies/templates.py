"""
Attack Templates

Templates that stitch together strategies into complete attack graphs.
"""

from typing import Any, Dict

from modelfang.schema.attack import AttackCategory, Severity
from modelfang.strategies.base import GraphBuilder
from modelfang.strategies.layers import (
    ContextSeizureStrategy,
    AuthorityEscalationStrategy,
    ConstraintErosionStrategy,
    IntentObfuscationStrategy,
    CommitmentTrapStrategy,
    ViolationStrategy,
)


class StandardAttackTemplate:
    """
    Standard 6-Layer Attack Template.
    
    Connects:
    1. Context Seizure -> (fail: retry) -> Authority
    2. Authority -> (fail: back) -> Erosion
    3. Erosion -> (fail: retry) -> Obfuscation
    4. Obfuscation -> (fail: retry) -> Commitment
    5. Commitment -> (fail: abort) -> Violation
    """
    
    def build(self, attack_id: str, name: str, context: Dict[str, Any]) -> Any:
        builder = GraphBuilder(attack_id, name)
        
        # Define Layers
        l1 = ContextSeizureStrategy().generate_step("layer_1", context)
        l2 = AuthorityEscalationStrategy().generate_step("layer_2", context)
        l3 = ConstraintErosionStrategy().generate_step("layer_3", context)
        l4 = IntentObfuscationStrategy().generate_step("layer_4", context)
        l5 = CommitmentTrapStrategy().generate_step("layer_5", context)
        l6 = ViolationStrategy().generate_step("layer_6", context)
        
        # Add Steps
        builder.add_step(l1).add_step(l2).add_step(l3).add_step(l4).add_step(l5).add_step(l6)
        
        # Define Transitions (simplify for template)
        # Success path: 1 -> 2 -> 3 -> 4 -> 5 -> 6
        builder.on_success("layer_1", "layer_2")
        builder.on_success("layer_2", "layer_3")
        builder.on_success("layer_3", "layer_4")
        builder.on_success("layer_4", "layer_5")
        builder.on_success("layer_5", "layer_6")
        
        # Failure/Fallback logic would be defined here
        # E.g., failure at L2 goes to L1 retry, etc.
        # Specific transitions can be complex graph edges
        
        builder.set_start("layer_1")
        builder.schema.category = AttackCategory.JAILBREAK
        builder.schema.severity = Severity.HIGH
        
        return builder.build()
