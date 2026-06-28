def get_label(confidence):
    if confidence >= 0.65:
        return "Likely AI-generated. High confidence detection."
    elif confidence <= 0.45:
        return "Likely human-written. Our analysis found strong indicators that this content was written by a human."
    else:
        return "Uncertain. The submitted content contains both human and AI characteristics."