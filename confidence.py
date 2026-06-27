# def calculate_confidence(llm_score, style_score):
#     """
#     Combine the two detection signals.

#     60% Groq
#     40% Stylometry
#     """

#     confidence = (llm_score * 0.60) + (style_score * 0.40)

#     if confidence <= 0.39:
#         attribution = "likely_human"

#     elif confidence <= 0.60:
#         attribution = "uncertain"

#     else:
#         attribution = "likely_ai"

#     return {
#         "confidence": round(confidence, 2),
#         "attribution": attribution
#     }

# _______

# def calculate_confidence(llm, style):
#     return {
#         "confidence": round(0.7 * llm + 0.3 * style, 2),
#         "attribution": (
#             "likely_ai" if (0.7 * llm + 0.3 * style) > 0.6
#             else "likely_human" if (0.7 * llm + 0.3 * style) < 0.4
#             else "uncertain"
#         )
#     }

# _______

def calculate_confidence(llm, style):
    #confidence = 0.7 * llm + 0.3 * style

    llm = float(llm)
    style = float(style)

    #confidence = (0.6 * llm) + (0.4 * style)
    confidence = (0.55 * llm) + (0.45 * style)

    # ✅ THIS is what you asked about
    confidence = max(0.0, min(confidence, 1.0))

    return {
        "confidence": round(confidence, 2),
        "attribution": (
            "likely_ai" if confidence >= 0.65
            else "likely_human" if confidence <= 0.45
            else "uncertain"
        )
    }