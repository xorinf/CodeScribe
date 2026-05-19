"""
nlp.py -- NLP Integration for Documentation Generation.

This module integrates Cloud LLM APIs (specifically Google Gemini)
to automatically generate human-readable summaries and descriptions
for code elements (functions, classes) that lack docstrings.

Usage:
    from src.generator.nlp import NLPEngine
    
    engine = NLPEngine(api_key="...", enabled=True)
    summary = engine.generate_function_summary(func_info, "my_module.py")
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from src.parser.base import ClassInfo, FunctionInfo

logger = logging.getLogger("CodeScribe")


class NLPEngine:
    """Natural Language Processing engine for enhancing documentation.

    Uses the Google Gemini API to analyze function signatures and class
    structures and generate concise descriptions.
    """

    def __init__(self, api_key: Optional[str] = None, enabled: bool = False) -> None:
        """Initialize the NLP engine.

        Args:
            api_key: The API key for the generative AI provider. If None,
                    it attempts to read from the environment.
            enabled: Whether the NLP engine is actually enabled. If False,
                    all generation methods will immediately return None.
        """
        self.enabled = enabled
        self._model = None

        if not self.enabled:
            return

        try:
            from google import genai
        except ImportError:
            logger.warning(
                "google-genai package not found. NLP generation disabled."
            )
            self.enabled = False
            return

        key = api_key or os.environ.get("CODESCRIBE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not key:
            logger.warning(
                "No API key provided for NLP generation. NLP generation disabled."
            )
            self.enabled = False
            return

        try:
            self._client = genai.Client(api_key=key)
            # Use gemini-2.5-flash as it is fast and suitable for this task
            self._model_name = "gemini-2.5-flash"
            logger.info("NLP Engine initialized successfully with Google Gemini.")
        except Exception as e:
            logger.error(f"Failed to initialize NLP client: {e}")
            self.enabled = False

    def generate_function_summary(self, func: FunctionInfo, module_name: str) -> Optional[str]:
        """Generate a concise summary for a function.

        Args:
            func: The function info.
            module_name: The name of the module containing the function.

        Returns:
            A generated string description, or None if disabled/failed.
        """
        if not self.enabled or not getattr(self, "_client", None):
            return None

        prompt = self._build_function_prompt(func, module_name)
        return self._call_model(prompt)

    def generate_class_summary(self, cls: ClassInfo, module_name: str) -> Optional[str]:
        """Generate a concise summary for a class.

        Args:
            cls: The class info.
            module_name: The name of the module containing the class.

        Returns:
            A generated string description, or None if disabled/failed.
        """
        if not self.enabled or not getattr(self, "_client", None):
            return None

        prompt = self._build_class_prompt(cls, module_name)
        return self._call_model(prompt)

    def _call_model(self, prompt: str) -> Optional[str]:
        """Execute the prompt against the Gemini model."""
        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt
            )
            if response and response.text:
                return response.text.strip()
            return None
        except Exception as e:
            logger.debug(f"NLP generation failed: {e}")
            return None

    def _build_function_prompt(self, func: FunctionInfo, module_name: str) -> str:
        """Construct the prompt for function summarization."""
        params_str = ", ".join(
            f"{p.name}: {p.type_hint or 'Any'}" for p in func.parameters
        )
        return_str = func.return_type or "Any"
        
        return f"""
You are an expert Python developer writing documentation.
Write a concise, 1-2 sentence description for the following function.
Do NOT use markdown formatting, just return plain text.

Function: `{func.name}`
Module: `{module_name}`
Signature: `def {func.name}({params_str}) -> {return_str}`
Visibility: {func.visibility.value}

Description:
"""

    def _build_class_prompt(self, cls: ClassInfo, module_name: str) -> str:
        """Construct the prompt for class summarization."""
        methods = [m.name for m in cls.methods if not m.name.startswith("_")]
        bases = ", ".join(cls.base_classes) if cls.base_classes else "None"
        
        return f"""
You are an expert Python developer writing documentation.
Write a concise, 1-2 sentence description for the following class.
Do NOT use markdown formatting, just return plain text.

Class: `{cls.name}`
Module: `{module_name}`
Inherits from: {bases}
Public Methods: {', '.join(methods) if methods else 'None'}

Description:
"""
