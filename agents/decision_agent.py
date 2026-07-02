def decide(score):
    if score >= 80:
        return "NEXT_CHAPTER"
    else:
        return "RETRY"