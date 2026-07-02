from agents import validation_agent
from skills.exercicegeneratorskill import ExerciseGeneratorSkill
from agents.planner_agent import LearningPathAgent
from skills.plannerskill import PlannerSkill
from agents.exercise_agent import ExerciseAgent
from agents.course_agent import CourseSearchAgent
from skills.courseskill import CourseSearchSkill
from tools.codeevaluatortool import CodeEvaluatorTool
from agents.validation_agent import ValidationAgent
from skills.texteevalskill import TextValidationSkill
from skills.imageevalskill import ImageValidationSkill
from skills.codeevalskill import CodeValidationSkill
from memory.progress import load_progress, save_progress, clear_progress
from tools.filetypetool import type_file_checking
from llm import GeminiLLM
import json
import re



llm = GeminiLLM("YOUR_API_KEY")

user_preferences = {
    "subject": "Python",
    "known_topics": ["None"],
    "learning_style": "video",
    "difficulty_level": 0
}

# -----------------------------
# 1. Generate learning path
# -----------------------------
planner_skill = PlannerSkill(llm)
planner_agent = LearningPathAgent(planner_skill)

session = load_progress()

if session:
    print("Previous session found.")

    path = session["learning_path"]
    current_topic_index = session["current_topic_index"]

else:
    path = planner_agent.run(user_preferences)
    path = json.loads(path)

    current_topic_index = 0

    save_progress(current_topic_index, path)


print("\n=== LEARNING PATH ===")
print(path)


# -----------------------------
# 2. Init course search system
# -----------------------------
course_skill = CourseSearchSkill(llm)
course_agent = CourseSearchAgent(course_skill)


# -----------------------------
# 3. Init exercise system
# -----------------------------
exercise_skill = ExerciseGeneratorSkill(llm)
exercise_agent = ExerciseAgent(exercise_skill)


code_evaluator_tool = CodeEvaluatorTool()


text_validation_skill = TextValidationSkill(llm)
image_validation_skill = ImageValidationSkill(llm)
code_validation_skill = CodeValidationSkill(llm)


validation_agent = ValidationAgent(
    code_validation_skill=CodeValidationSkill(code_evaluator_tool),
    text_validation_skill=TextValidationSkill(llm),
    image_validation_skill=ImageValidationSkill(llm)
)



# -----------------------------
# Wait for user input
# -----------------------------
def wait_user(message="Press Enter to continue (q to quit): "):
    user_input = input(message).strip().lower()
    if user_input == "q":
        print("Exiting learning session...")
        exit()
    return user_input


def safe_json_loads(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise
    
# -----------------------------
# 4. Loop through topics
# -----------------------------
current_topic_index = 0

while current_topic_index < len(path["topics"]):

    topic = path["topics"][current_topic_index]

    print("\n====================")
    print("TOPIC:", topic)
    print("====================\n")


    # -----------------------------
    # 4.1 Find courses/resources
    # -----------------------------
    course_preferences = {
        "topic": topic,
        "learning_style": user_preferences["learning_style"]
    }

    courses = course_agent.run(course_preferences)
    courses = safe_json_loads(courses)

    print("\n📚 RESOURCES:")
    print(json.dumps(courses, indent=2))


    wait_user("\n➡️ Ready to do the exercise? (Enter = continue, q = quit): ")


    # -----------------------------
    # 4.2 Generate exercise
    # -----------------------------
    exercise_rules = {
        "subject": topic,
        "level": "beginner",
        "mistakes": ["None"]
    }

    exercise = exercise_agent.run(exercise_rules)
    exercise = safe_json_loads(exercise)

    print("\n🧠 EXERCISE:")
    print(json.dumps(exercise, indent=2))


    file_path = input("Path to your file: ")

    attempts = 0

    while attempts < 3:
        file_type = type_file_checking(file_path, exercise["expected_file_type"])
        if file_type:
            break
        file_path = input("Retry (or q): ")
        if file_path == "q":
            break
        attempts += 1


    validation = validation_agent.run(
        exercise,
        file_path
    )
    
    print(validation)

    wait_user("\n➡️ Did you complete the exercise? (Enter = next topic, q = quit): ")

    
    # -----------------------------
    # 4.3 (simulation) progress
    # -----------------------------
    if validation["score"] >= 80:
        current_topic_index += 1
        save_progress(current_topic_index, path)
    else:
        print("Exercise failed. Try again.")


print("\n🎉 Learning path completed!")
clear_progress()