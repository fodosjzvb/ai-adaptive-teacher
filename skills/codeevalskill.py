class CodeValidationSkill:

    name = "code_validation"
    objective = "Validate Python exercises"

    def __init__(self, evaluator_tool):
        self.evaluator_tool = evaluator_tool

    def run(self, file_path, exercise):

        result = self.evaluator_tool.run(
            file_path=file_path,
            function_name=exercise["function_name"],
            tests=exercise["tests"]
        )

        # Transformation pédagogique
        return {
            "passed": result["passed"],
            "score": result["score"],
            "feedback": self._generate_feedback(result)
        }

    def _generate_feedback(self, result):
        if result["passed"]:
            return "Excellent, all tests passed 🎉"

        return f"""
        Score: {result['score']}%

        Failed tests: {len(result.get('failed_tests', []))}

        Tip: Check your logic on the failing cases.
        """