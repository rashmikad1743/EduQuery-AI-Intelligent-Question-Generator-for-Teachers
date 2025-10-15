def validate_input(text):
    if not text or len(text.strip()) < 20:
        return False
    return True
