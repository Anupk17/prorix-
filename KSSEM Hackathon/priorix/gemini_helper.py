import google.generativeai as genai

_configured = False


def configure_gemini(api_key: str):
    global _configured
    genai.configure(api_key=api_key)
    _configured = True


def summarize_notifications(notifications: list, app_name: str) -> str:
    """
    Summarizes a list of notification strings for an app using Gemini.
    Returns a 2-3 bullet-point summary string.
    Raises an exception on API errors (caller should handle).
    """
    notifications_text = "\n".join(f"- {n}" for n in notifications)
    prompt = (
        f"You are a notification summarizer. Summarize these {app_name} notifications "
        f"in 2-3 bullet points, keeping only the most important information. "
        f"Be concise and action-oriented.\n\n"
        f"Notifications:\n{notifications_text}\n\nSummary:"
    )

    model_name = "models/gemini-1.5-flash"
    try:
        available_models = [
            m.name for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        
        # Prefer a flash or pro model from the available list
        for m in available_models:
            if "flash" in m:
                model_name = m
                break
            if "pro" in m:
                model_name = m

        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
    except Exception as e:
        raise Exception(f"Failed to call Gemini API with model '{model_name}': {str(e)}")

    return response.text.strip()
