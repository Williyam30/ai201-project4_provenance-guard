import os
import re
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def detect_with_groq(text):
    prompt = f"""
    You are a strict AI detection system.

    Rules:
    - Casual human writing must often score 0.1-0.4
    - Formal academic AI-like writing: 0.7-1.0
    - Mixed writing: 0.4-0.7

    Return ONLY valid JSON:

    {{
        "confidence": 0.0,
        "classification": "very likely AI | very likely human | mixed"
    }}

    TEXT:
    {text}
    """

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = completion.choices[0].message.content
    cleaned = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(cleaned)

        confidence = result.get("confidence", 0.5)
        confidence = max(0.0, min(confidence, 1.0))

        classification = result.get("classification", "uncertain")

        return {
            "llm_score": float(confidence),
            "attribution": classification
        }

    except Exception as e:
        print("Groq parse failed:", e)

        return {
            "llm_score": 0.5,
            "attribution": "uncertain"
        }

## milestone_4, second detection signal

def stylometric_score(text):
    """
    Returns a score between 0 and 1.

    Higher score = more AI-like
    """

    words = re.findall(r"\w+", text)

    if len(words) == 0:
        return 0.5

    # Vocabulary diversity
    unique_words = len(set(words))
    type_token_ratio = unique_words / len(words)

    # Sentence lengths
    sentences = re.split(r"[.!?]+", text)
    sentence_lengths = [
        len(re.findall(r"\w+", s))
        for s in sentences if s.strip()
    ]

    if len(sentence_lengths) > 1:
        variance = max(sentence_lengths) - min(sentence_lengths)
    else:
        variance = 0

    punctuation = len(re.findall(r"[,:;!?]", text))

    score = 0

    # vocabulary diversity (stronger separation)
    if type_token_ratio < 0.55:
        score += 0.5
    elif type_token_ratio < 0.7:
        score += 0.25

    # sentence variation
    if variance < 4:
        score += 0.4
    elif variance < 8:
        score += 0.2

    # punctuation usage
    if punctuation < 2:
        score += 0.3
    elif punctuation < 4:
        score += 0.1

    # force better spread
    score = max(0.0, min(score, 1.0))

    return round(min(score, 1.0), 2)

if __name__ == "__main__":

    sample = """
The sun dipped below the horizon, painting the sky in hues of amber and rose.
"""

    result = detect_with_groq(sample)

    print(result)