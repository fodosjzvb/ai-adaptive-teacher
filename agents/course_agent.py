class CourseSearchAgent:

    def __init__(self, course_search_skill):
        self.course_search_skill = course_search_skill

    def run(self, course_preferences):

        topic = course_preferences["topic"]
        learning_style = course_preferences["learning_style"]

        return self.course_search_skill.run(
            topic,
            learning_style
        )