class ExerciseAgent:

    def __init__(self, exercise_generator_skill):
        self.exercise_generator_skill = exercise_generator_skill

    def run(self, exercise_rules):
        subject = exercise_rules["subject"]
        level = exercise_rules["level"] 
        mistakes = exercise_rules["mistakes"]

        return self.exercise_generator_skill.run(subject, level, mistakes)


