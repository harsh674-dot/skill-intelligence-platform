"""
AI-powered MCQ generation from learning content.

Uses:
    google/flan-t5-base

Generates varied MCQs from supplied learning content.
"""

import re
from typing import Any

# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "google/flan-t5-base"

MAX_INPUT_LENGTH = 1024
MAX_OUTPUT_LENGTH = 256

VALID_DIFFICULTIES = {
    "beginner",
    "intermediate",
    "advanced",
}

QUESTION_FOCUSES = [
    "definition or meaning of an important concept",
    "a key fact or statement from the material",
    "a relationship between two concepts",
    "a practical application or example",
    "a comparison or distinction between concepts",
    "a cause, effect, or consequence",
    "an important property or characteristic",
    "a calculation, rule, or technical detail if present",
]

# ============================================================
# LAZY LOAD MODEL
# ============================================================

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
        print(f"Loading question generation model: {MODEL_NAME}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
        model.eval()
        _tokenizer = tokenizer
        _model = model
        print("Question generation model loaded.")
        return _tokenizer, _model
    except Exception as exc:
        print(f"[QuestionGenerator] Transformers/Torch model not available: {exc}. Using grounded fallback generator.")
        return None, None


# ============================================================
# MODEL GENERATION
# ============================================================

def _generate_text(prompt: str) -> str:
    """
    Generate text using FLAN-T5 if available.
    """
    tokenizer, model = _get_model()
    if tokenizer is None or model is None:
        raise RuntimeError("Model not available")

    import torch
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_INPUT_LENGTH,
    )

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_OUTPUT_LENGTH,
            do_sample=True,
            temperature=0.85,
            top_p=0.92,
            top_k=50,
            no_repeat_ngram_size=3,
            repetition_penalty=1.15,
        )

    result = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    )

    return result.strip()



# ============================================================
# TEXT CLEANING
# ============================================================

def _clean_text(value: str) -> str:
    """Clean generated text."""

    if not value:
        return ""

    value = value.replace("\r", " ")
    value = value.replace("\n", " ")

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


# ============================================================
# OPTION EXTRACTION
# ============================================================

def _extract_option(
    text: str,
    letter: str,
) -> str | None:

    pattern = (
        rf"(?:^|\s){letter}"
        rf"\s*[\.\):\-]?\s*"
        rf"(.+?)"
        rf"(?=\s+[A-D]\s*[\.\):\-]?\s+|$)"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    option = match.group(1).strip()

    option = re.split(
        r"\s+(?:Answer|Correct Answer|Explanation)"
        r"\s*[:\-]?",
        option,
        flags=re.IGNORECASE,
    )[0]

    option = _clean_text(option)

    return option if option else None


# ============================================================
# QUESTION EXTRACTION
# ============================================================

def _extract_question(text: str) -> str:

    text = _clean_text(text)

    text = re.sub(
        r"^question\s*[:\-]\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.split(
        r"\s+(?:Options?|A)\s*[\:\.\)]",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    return _clean_text(text)


# ============================================================
# ANSWER EXTRACTION
# ============================================================

def _extract_answer(text: str) -> str | None:

    patterns = [
        r"(?:correct\s+answer|answer|correct)"
        r"\s*[:\-]?\s*([A-D])\b",

        r"\b([A-D])\s*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1).upper()

    return None


# ============================================================
# EXPLANATION EXTRACTION
# ============================================================

def _extract_explanation(text: str) -> str:

    match = re.search(
        r"(?:explanation|because)"
        r"\s*[:\-]?\s*(.+)$",
        text,
        flags=re.IGNORECASE,
    )

    if match:

        explanation = _clean_text(
            match.group(1)
        )

        return explanation[:1000]

    return ""


# ============================================================
# VALIDATION
# ============================================================

def _validate_mcq(
    question: str,
    options: dict[str, str],
    correct_answer: str | None,
) -> tuple[bool, str]:

    if not question:
        return False, "Question is empty."

    required_options = [
        "A",
        "B",
        "C",
        "D",
    ]

    for letter in required_options:

        if letter not in options:
            return (
                False,
                f"Missing option {letter}.",
            )

        if not options[letter].strip():
            return (
                False,
                f"Option {letter} is empty.",
            )

    normalized = [
        options[x].strip().lower()
        for x in required_options
    ]

    if len(set(normalized)) != 4:
        return (
            False,
            "Options contain duplicates.",
        )

    if correct_answer not in required_options:
        return (
            False,
            "Correct answer must be A, B, C or D.",
        )

    return True, ""


# ============================================================
# FALLBACK
# ============================================================

def _fallback_mcq(
    context: str,
    difficulty: str,
    question_number: int = 1,
) -> dict[str, Any]:

    # --------------------------------------------------------
    # Extract useful sentences from the content.
    # --------------------------------------------------------

    sentences = [
        _clean_text(x)
        for x in re.split(
            r"[.!?]",
            context,
        )
        if len(_clean_text(x)) > 20
    ]

    if not sentences:

        sentences = [
            "the concepts discussed in the learning material"
        ]

    # Pick different material for different questions.
    sentence = sentences[
        (question_number - 1) % len(sentences)
    ]

    # --------------------------------------------------------
    # Create a safer fallback.
    # --------------------------------------------------------

    return {
        "question_text": (
            f"Which statement is supported by the "
            f"learning material regarding: {sentence}?"
        ),
        "options": {
            "A": sentence,
            "B": "The material provides no information about this topic.",
            "C": "The topic refers only to an unrelated physical object.",
            "D": "The topic describes an unrelated historical event.",
        },
        "correct_answer": "A",
        "explanation": (
            "Option A is supported directly by the provided "
            "learning material."
        ),
        "difficulty": difficulty,
    }


# ============================================================
# PROMPT
# ============================================================

def _build_prompt(
    context: str,
    difficulty: str,
    question_number: int = 1,
) -> str:

    focus = QUESTION_FOCUSES[
        (question_number - 1) % len(QUESTION_FOCUSES)
    ]

    return f"""
Create ONE high-quality multiple-choice question from the
learning material below.

Question number: {question_number}

Difficulty: {difficulty}

Preferred question focus:
{focus}

Learning material:
{context}

Return EXACTLY this format:

Question: <question>
A. <option A>
B. <option B>
C. <option C>
D. <option D>
Answer: <A, B, C, or D>
Explanation: <short explanation>

Rules:

- The question MUST be answerable using ONLY the learning material.
- Do NOT use outside knowledge.
- Make the question specific to the material.
- Avoid generic questions such as "Which statement is related
  to the learning material?"
- Create four meaningful options.
- Exactly ONE option must be correct.
- The incorrect options must be plausible but contradicted by
  or unsupported by the learning material.
- Do not repeat the question wording.
- Do not add any text outside the requested format.
""".strip()


# ============================================================
# PARSE MODEL OUTPUT
# ============================================================

def _parse_mcq(
    raw_output: str,
    difficulty: str,
) -> dict[str, Any]:

    raw_output = _clean_text(
        raw_output
    )

    # --------------------------------------------------------
    # Question
    # --------------------------------------------------------

    question_match = re.search(
        r"Question\s*:\s*(.+?)"
        r"(?=\s+A\s*[\.\):\-])",
        raw_output,
        flags=re.IGNORECASE,
    )

    if question_match:

        question = _clean_text(
            question_match.group(1)
        )

    else:

        question = _extract_question(
            raw_output
        )

    # --------------------------------------------------------
    # Options
    # --------------------------------------------------------

    options: dict[str, str] = {}

    for letter in [
        "A",
        "B",
        "C",
        "D",
    ]:

        option = _extract_option(
            raw_output,
            letter,
        )

        if option:
            options[letter] = option

    # --------------------------------------------------------
    # Answer
    # --------------------------------------------------------

    correct_answer = _extract_answer(
        raw_output
    )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    explanation = _extract_explanation(
        raw_output
    )

    return {
        "question_text": question,
        "options": options,
        "correct_answer": correct_answer,
        "explanation": explanation,
        "difficulty": difficulty,
    }


# ============================================================
# MAIN FUNCTION
# ============================================================

def generate_mcq(
    context: str,
    difficulty: str = "beginner",
    question_number: int = 1,
) -> dict[str, Any]:

    if not context or not context.strip():

        raise ValueError(
            "Learning content cannot be empty."
        )

    difficulty = difficulty.lower().strip()

    if difficulty not in VALID_DIFFICULTIES:

        raise ValueError(
            "Difficulty must be one of: "
            "beginner, intermediate, advanced."
        )

    context = context.strip()[:6000]

    prompt = _build_prompt(
        context=context,
        difficulty=difficulty,
        question_number=question_number,
    )

    last_error = ""
    last_output = ""

    # --------------------------------------------------------
    # Try multiple generations.
    # --------------------------------------------------------

    for attempt in range(1, 4):

        try:

            print(
                f"MCQ generation attempt "
                f"{attempt}/3 "
                f"(question {question_number})"
            )

            raw_output = _generate_text(
                prompt
            )

            last_output = raw_output

            print(
                f"Model output: {raw_output}"
            )

            parsed = _parse_mcq(
                raw_output,
                difficulty,
            )

            valid, error = _validate_mcq(
                parsed["question_text"],
                parsed["options"],
                parsed["correct_answer"],
            )

            if valid:

                if not parsed["explanation"]:

                    parsed["explanation"] = (
                        "The correct answer is supported "
                        "by the provided learning material."
                    )

                return parsed

            last_error = error

            print(
                f"MCQ validation failed: {error}"
            )

        except Exception as exc:

            last_error = str(exc)

            print(
                f"MCQ generation attempt "
                f"{attempt} failed: {exc}"
            )

    # --------------------------------------------------------
    # Safe fallback.
    # --------------------------------------------------------

    print(
        "Model failed to generate a valid MCQ."
    )

    print(
        f"Last validation error: {last_error}"
    )

    print(
        f"Last model output: {last_output}"
    )

    return _fallback_mcq(
        context=context,
        difficulty=difficulty,
        question_number=question_number,
    )