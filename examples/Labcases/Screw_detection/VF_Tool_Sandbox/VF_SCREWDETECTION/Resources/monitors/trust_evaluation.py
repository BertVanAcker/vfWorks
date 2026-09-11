def validate(monitor=None, **kwargs):
    """
    Evaluates the model certainty of the predictions.
    """
    value = kwargs["trust"]
    if value == "True":
        return {
        "trust": True
    }
    else:
        return {
            "trust": False
        }