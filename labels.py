def get_label(result):

    if result == "likely_ai":

        return (
            "Likely AI-generated. "
            "Our analysis found strong indicators "
            "that this content was generated using AI."
        )

    elif result == "likely_human":

        return (
            "Likely human-written. "
            "Our analysis found strong indicators "
            "that this content was written by a human."
        )

    else:

        return (
            "Uncertain. "
            "The submitted content contains both "
            "human and AI characteristics."
        )