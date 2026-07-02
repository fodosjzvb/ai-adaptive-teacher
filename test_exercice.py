# personalized_greeting.py

def create_personalized_greeting(name: str, favorite_number: int) -> str:
    result = favorite_number * 2
    return f"Hello, {name}! Your favorite number is {favorite_number}. Did you know {favorite_number} * 2 is {result}?"