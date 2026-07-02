class ValidationAgent:

    def __init__(
        self,
        code_validation_skill,
        text_validation_skill,
        image_validation_skill
    ):
        self.code_validation_skill = code_validation_skill
        self.text_validation_skill = text_validation_skill
        self.image_validation_skill = image_validation_skill

    def run(self, exercise, file_path):

        exercise_type = exercise["exercise_type"]

        if exercise_type == "coding":
            return self.code_validation_skill.run(
                file_path,
                exercise
            )

        elif exercise_type == "text":
            return self.text_validation_skill.run(
                file_path,
                exercise
            )

        elif exercise_type == "image":
            return self.image_validation_skill.run(
                file_path,
                exercise
            )

        else:
            raise ValueError(f"Unknown exercise type: {exercise_type}")