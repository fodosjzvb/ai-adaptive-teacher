class LearningPathAgent:
    
    def __init__(self, planner_skill):
        self.planner_skill = planner_skill

    def run(self, user_preferences):
        subject = user_preferences["subject"]
        known_topics  = user_preferences["known_topics"]
        learning_style = user_preferences["learning_style"]
        difficulty_level = user_preferences["difficulty_level"]
        
        return self.planner_skill.run(subject, known_topics, learning_style, difficulty_level)
        