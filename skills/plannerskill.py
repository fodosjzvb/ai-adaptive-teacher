class PlannerSkill:

    name = "planner"
    objective = "generate a learning path"
    rules = [
        "Must return structured topics", 
        "Must be progressive",
    ]

    def __init__(self, llm):
        self.llm = llm

    def run(self, subject, known_topics, learning_style, difficulty_level):
        prompt = f"""
        You are an AI learning path generator.

        The user wants to learn {subject}.
        Background knowledge:
        {known_topics}
        Preferred learning style:
        {learning_style}
        Current difficulty level:
        {difficulty_level}

        CRITICAL:
        - Do NOT include backticks
        - Do NOT include multiple JSON objects

        Requirements:
        - Create a progressive learning path.
        - Skip topics already mastered.
        - Adapt to the user's preferred learning style.
        - Return only valid JSON.
        - No markdown.
        - No explanations.
        - Must return structured topics
        - Must be progressive
        - Ensure the learning path respects the user's global level.
        - Do not introduce advanced topics too early even if partially known topics exist.

        Output format:
        {{
        "topics": ["topic1", "topic2", "topic3", "topic4", "topic5"]
        }}
        """
        return self.llm.generate(prompt)