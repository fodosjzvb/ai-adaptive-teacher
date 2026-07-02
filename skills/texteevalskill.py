class TextValidationSkill:

    name = "text_validation"

    objective = "Evaluate written answers"

    def __init__(self, llm):
        self.llm = llm

    def run(self, file_path, exercise):
        import json
        import re

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                answer = f.read()
        except Exception as e:
            return {
                "passed": False,
                "score": 0,
                "feedback": f"Failed to read file: {str(e)}"
            }

        prompt = f"""
You are an AI teacher.

Topic:
{exercise["title"]}

Exercise:
{exercise["description"]}

Student answer:
{answer}

Evaluate:

- Does the answer solve the exercise?
- Is it correct?
- Give a score from 0 to 100.
- Give short feedback.

Return ONLY JSON matching this format:

{{
    "passed": true,
    "score": 95,
    "feedback": "Very good answer."
}}
"""

        raw_response = self.llm.generate(prompt)
        try:
            return json.loads(raw_response)
        except Exception:
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return {
                "passed": False,
                "score": 0,
                "feedback": f"Failed to parse model response: {raw_response}"
            }