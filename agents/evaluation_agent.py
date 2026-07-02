class EvaluationAgent:

    def __init__(self, evaluation_skill):
        self.evaluation_skill = evaluation_skill

    def run(self, exercise, submission):

        exercise_type = exercise["exercise_type"]

        return self.evaluation_skill.run(
            exercise,
            submission,
            exercise_type
        )