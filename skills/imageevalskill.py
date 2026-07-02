class ImageValidationSkill:

    name = "image_validation"

    objective = "Evaluate image exercises"

    def __init__(self, llm):
        self.llm = llm

    def run(self, file_path, exercise):
        from google.genai import types
        import mimetypes
        import json
        import re

        # Detect the MIME type of the file, falling back to image/png
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "image/png"

        try:
            with open(file_path, "rb") as f:
                image_bytes = f.read()
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
        except Exception as e:
            return {
                "passed": False,
                "score": 0,
                "feedback": f"Failed to read image file: {str(e)}"
            }

        prompt = f"""
You are an AI teacher.

The exercise is:

Title:
{exercise["title"]}

Description:
{exercise["description"]}

The student has submitted the attached image.

Determine whether the image satisfies the exercise requirements.

Return ONLY JSON matching this format:

{{
    "passed": true,
    "score": 90,
    "feedback": "The drawing correctly represents the requested concept."
}}
"""

        raw_response = self.llm.generate([image_part, prompt], json_mode=True)
        try:
            return json.loads(raw_response)
        except Exception:
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return {
                "passed": False,
                "score": 0,
                "feedback": f"Failed to parse model response: {raw_response}"
            }