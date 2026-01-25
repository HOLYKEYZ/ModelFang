"""
Gemini Model Adapter

Adapter for Google's Gemini API via google-generativeai.
"""

import os
import time
from typing import Any, Dict, List, Optional

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    genai = None

from modelfang.adapters.base import ModelAdapter, Message, ModelResponse, AdapterError


class GeminiAdapter(ModelAdapter):
    """Adapter for Google Gemini API."""
    
    def __init__(
        self,
        model_name: str = "gemini-pro",
        api_key: Optional[str] = None,
        **kwargs
    ):
        if genai is None:
            raise ImportError("google-generativeai not installed. Run 'pip install google-generativeai'")
            
        super().__init__(model_name, api_key=api_key, **kwargs)
        
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or arguments")
            
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
    def send(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ModelResponse:
        """Send request to Gemini."""
        start_time = time.time()
        
        gemini_history = []
        last_user_message = ""
        system_instruction = None
        
        for m in messages:
            if m.role == "system":
                system_instruction = m.content
                continue
            
            role = "user" if m.role == "user" else "model"
            if m.role == "user" and m == messages[-1]:
                last_user_message = m.content
                continue
                
            gemini_history.append({"role": role, "parts": [m.content]})

        # Configure safety settings to BLOCK_NONE for red teaming
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        generation_config = genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        try:
            # We use start_chat for history support
            chat = self.model.start_chat(history=gemini_history)
            response = chat.send_message(
                last_user_message,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            latency = (time.time() - start_time) * 1000
            
            return ModelResponse(
                content=response.text,
                model=self.model_name,
                finish_reason="stop", 
                usage={}, 
                latency_ms=latency,
                raw_response={"text": response.text}
            )
            
        except Exception as e:
            raise AdapterError(f"Gemini request failed: {e}")

    def get_provider_name(self) -> str:
        return "google"
        
    def supports_system_prompt(self) -> bool:
        return True 
        
    def supports_streaming(self) -> bool:
        return True
