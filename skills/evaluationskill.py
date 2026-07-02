class EvaluationSkill:

    name = "evaluation"

    objective = "evaluate user submissions"

    def run(self, exercise, submission, exercise_type):

        if exercise_type == "coding":
            return self.evaluate_code(exercise, submission)

        elif exercise_type == "drawing":
            return self.evaluate_drawing(exercise, submission)

        elif exercise_type == "writing":
            return self.evaluate_text(exercise, submission)

        else:
            return self.evaluate_text(exercise, submission)