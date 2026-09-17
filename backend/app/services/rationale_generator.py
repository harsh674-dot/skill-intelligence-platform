"""
AI-powered recommendation rationale generation using FLAN-T5.

Uses context (user role, department, course title, course description, gap) 
to generate a human-readable explanation of why a course is recommended.
"""

from typing import Any
import logging

logger = logging.getLogger(__name__)

MODEL_NAME = "google/flan-t5-base"

_tokenizer = None
_model = None
_load_attempted = False

def _get_model():
    global _tokenizer, _model, _load_attempted
    if _tokenizer is not None and _model is not None:
        return _tokenizer, _model
    if _load_attempted:
        return None, None
    _load_attempted = True
    try:
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        logger.info(f"Loading rationale generation model: {MODEL_NAME}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        model.eval()
        _tokenizer = tokenizer
        _model = model
        logger.info("Rationale generation model loaded.")
        return _tokenizer, _model
    except Exception as exc:
        logger.error(f"Transformers/Torch model not available: {exc}. Using fallback generator.")
        return None, None

def generate_rationale(
    user_designation: str,
    competency_name: str,
    current_level: int,
    required_level: int,
    course_title: str,
    course_description: str
) -> str:
    """
    Generate a short, personalized rationale for why this course is recommended.
    """
    tokenizer, model = _get_model()
    
    if tokenizer is None or model is None:
        # Fallback rationale
        return (f"This course covers {competency_name} which is needed for your role as "
                f"{user_designation}. It will help you bridge your gap from level {current_level} "
                f"to the required level {required_level}.")
        
    prompt = f"""
Given the following details, write a brief, encouraging 2-sentence rationale explaining why the user should take this course. 
Do not hallucinate facts.

Role: {user_designation}
Competency to improve: {competency_name}
Current Level: {current_level}
Required Level: {required_level}
Course Title: {course_title}
Course Description: {course_description}

Rationale:
    """.strip()
    
    try:
        import torch
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
            )

        result = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
        )
        
        return result.strip()
    except Exception as e:
        logger.error(f"Failed to generate LLM rationale: {e}")
        return (f"This course covers {competency_name} which is needed for your role as "
                f"{user_designation}. It will help you bridge your gap from level {current_level} "
                f"to the required level {required_level}.")
