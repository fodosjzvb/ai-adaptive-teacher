class CourseSearchSkill:

    name = "course_search"

    objective = "Search learning resources for a topic"

    rules = [
        "Must recommend high-quality learning resources",
        "Must adapt to the preferred learning style",
        "Must return structured JSON"
    ]

    def __init__(self, llm):
        self.llm = llm

    def run(self, topic, learning_style):

        prompt = f"""
        You are an AI learning resource recommender.

        The user wants to learn:
        {topic}

        Preferred learning style:
        {learning_style}

        Requirements:
        - Recommend high-quality learning resources.
        - Adapt recommendations to the preferred learning style.
        - If the learning style is "all", recommend every available type of resource.
        - Include a short explanation for each recommendation.
        - Return ONLY valid JSON.
        - No markdown.
        - No explanations outside the JSON.
        - Do NOT include backticks
        - Do NOT include multiple JSON objects

        Supported resource types include:
        - Video courses
        - Written tutorials
        - Documentation
        - Interactive websites
        - Practice platforms
        - Projects
        - Books
        - Articles

        Output format:

        {{
            "learning_objective": "Understand what Python is and install the development environment.",

            "recommended_resource": {{
                "title": "Python for Everybody - Getting Started",
                "type": "video",
                "url": "...",
                "watch": "0:00 - 18:35",
                "reason": "This section covers installation and your first Python program."
            }},

            "optional_resources": [
                {{
                    "title": "Corey Schafer",
                    "url": "..."
                }}
            ],

            "estimated_time": "20 minutes"
        }}
        """

        return self.llm.generate(prompt, json_mode=True)