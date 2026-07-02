class ExerciseGeneratorSkill:

    name = "exercise_generator"
    objective = "Generate adaptive exercises"

    def __init__(self, llm):
        self.llm = llm

    def run(self, subject, level, mistakes):

        prompt = f"""
        You are an AI teacher designing an exercise for a student.

        Topic/Subject: {subject}
        Student's target difficulty level: {level}
        User's previous mistakes: {mistakes}

        Determine the appropriate exercise type based on the Topic/Subject:
        - If the topic is coding, scripting, or programming, the exercise_type must be "coding" and the expected_file_type must be ".py".
        - If the topic is artistic, drawing, sketching, or visual, the exercise_type must be "image" and the expected_file_type must be ".png" or ".jpg".
        - If the topic is math, theory, writing, history, or textual problem solving, the exercise_type must be "text" and the expected_file_type must be ".txt".

        Requirements:
        - Adapt the exercise difficulty to the user's level and address previous mistakes if any.
        - Return ONLY valid JSON.
        - Do NOT include markdown blocks or backticks.

        JSON Schemas to conform to depending on the chosen exercise_type:

        For "coding" exercises:
        {{
            "title": "Exercise Title",
            "description": "Clear description of the function to implement.",
            "exercise_type": "coding",
            "expected_file_type": ".py",
            "function_name": "function_name_to_call",
            "tests": [
                [[arg1, arg2], expected_result],
                ...
            ]
        }}

        For "image" exercises:
        {{
            "title": "Exercise Title",
            "description": "Clear instructions of what the student needs to draw or capture in the image.",
            "exercise_type": "image",
            "expected_file_type": ".png",
            "function_name": "",
            "tests": []
        }}

        For "text" exercises:
        {{
            "title": "Exercise Title",
            "description": "Clear instructions for the math or theoretical question the student needs to solve in a text file.",
            "exercise_type": "text",
            "expected_file_type": ".txt",
            "function_name": "",
            "tests": []
        }}
        """

        return self.llm.generate(prompt, json_mode=True)
