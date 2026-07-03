import streamlit as st
import json
import re
import os
import tempfile
import pandas as pd

# Import backend agents, skills, and tools
from llm import GeminiLLM
from agents.planner_agent import LearningPathAgent
from skills.plannerskill import PlannerSkill
from agents.course_agent import CourseSearchAgent
from skills.courseskill import CourseSearchSkill
from agents.exercise_agent import ExerciseAgent
from skills.exercicegeneratorskill import ExerciseGeneratorSkill
from tools.codeevaluatortool import CodeEvaluatorTool
from agents.validation_agent import ValidationAgent
from skills.codeevalskill import CodeValidationSkill
from skills.texteevalskill import TextValidationSkill
from skills.imageevalskill import ImageValidationSkill
from memory.memory_manager import MemoryManager
from tools.filetypetool import type_file_checking
#debug

# Set page configurations
st.set_page_config(
    page_title="AI Personal Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    st.title("🎓 Welcome to AI Personal Tutor")

    email = st.text_input("Enter your email")

    if st.button("Continue"):
        if email.strip():
            st.session_state.user_id = email.strip().lower()
            st.rerun()
        else:
            st.error("Please enter an email address.")

    st.stop()

# Custom premium styling
st.markdown("""
<style>
    .roadmap-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        background-color: #0e1117;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        border: 1px solid #30363d;
    }
    .roadmap-step {
        text-align: center;
        flex: 1;
        position: relative;
    }
    .roadmap-step:not(:last-child)::after {
        content: '';
        position: absolute;
        top: 20px;
        right: -50%;
        width: 100%;
        height: 4px;
        background-color: #30363d;
        z-index: 1;
    }
    .roadmap-step.completed:not(:last-child)::after {
        background-color: #238636;
    }
    .circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #21262d;
        border: 3px solid #30363d;
        display: inline-flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        z-index: 2;
        position: relative;
        color: #8b949e;
        margin: 0 auto;
    }
    .circle.completed {
        background-color: #238636;
        border-color: #2ea043;
        color: white;
    }
    .circle.active {
        background-color: #1f6feb;
        border-color: #58a6ff;
        color: white;
        box-shadow: 0 0 12px #58a6ff;
    }
    .circle.locked {
        background-color: #161b22;
        border-color: #21262d;
        color: #484f58;
    }
    .label {
        margin-top: 8px;
        font-size: 13px;
        color: #c9d1d9;
        font-weight: 500;
    }
    .label.active {
        color: #58a6ff;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to handle JSON responses safely
def safe_json_loads(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        raise ValueError(f"Invalid JSON response: {text}")

# Initialize session state variables
if "api_key" not in st.session_state:
    st.session_state.api_key = st.secrets.get("API_KEY", "")
    #st.session_state.api_key = "YOUR_API_KEY"
if "learning_path" not in st.session_state:
    st.session_state.learning_path = None
if "current_topic_index" not in st.session_state:
    st.session_state.current_topic_index = 0
if "resources" not in st.session_state:
    st.session_state.resources = {}
if "exercise" not in st.session_state:
    st.session_state.exercise = {}
if "validation" not in st.session_state:
    st.session_state.validation = {}
if "streak" not in st.session_state:
    st.session_state.streak = 1
if "mistakes" not in st.session_state:
    st.session_state.mistakes = []
if "skills_progress" not in st.session_state:
    st.session_state.skills_progress = []
if "memory_loaded" not in st.session_state:
    st.session_state.memory_loaded = False


memory = MemoryManager(st.session_state.user_id)

def _int_keys(d):
    """Convert string keys (from JSON) back to integer keys used at runtime."""
    if isinstance(d, dict):
        try:
            return {int(k): v for k, v in d.items()}
        except (ValueError, TypeError):
            return d
    return d

if not st.session_state.memory_loaded:
    memory_data = memory.load()

    if memory_data:
        st.session_state.learning_path = memory_data.get("learning_path", None)
        st.session_state.current_topic_index = memory_data.get("current_topic_index", 0)
        st.session_state.streak = memory_data.get("streak", 1)
        st.session_state.mistakes = memory_data.get("mistakes", [])
        st.session_state.skills_progress = memory_data.get("skills_progress", [])
        # JSON serialises integer dict keys as strings — convert them back
        st.session_state.resources = _int_keys(memory_data.get("resources", {}))
        st.session_state.exercise = _int_keys(memory_data.get("exercise", {}))
        st.session_state.validation = _int_keys(memory_data.get("validation", {}))

    st.session_state.memory_loaded = True

def save_memory():
    data = {
        "learning_path": st.session_state.get("learning_path"),
        "current_topic_index": st.session_state.get("current_topic_index"),
        "streak": st.session_state.get("streak"),
        "mistakes": st.session_state.get("mistakes"),
        "skills_progress": st.session_state.get("skills_progress"),
        "resources": st.session_state.get("resources"),
        "exercise": st.session_state.get("exercise"),
        "validation": st.session_state.get("validation"),
    }
    memory.save(data)

# Fetch topic data function
def load_topic_data(topic_index):
    topic = st.session_state.learning_path["topics"][topic_index]
    llm = GeminiLLM(st.session_state.api_key)
    
    # 1. Load resources
    course_skill = CourseSearchSkill(llm)
    course_agent = CourseSearchAgent(course_skill)
    course_preferences = {
        "topic": topic,
        "learning_style": st.session_state.learning_style.lower()
    }
    
    with st.spinner("📚 Finding learning resources..."):
        try:
            courses_raw = course_agent.run(course_preferences)
            st.session_state.resources[topic_index] = safe_json_loads(courses_raw)
        except Exception as e:
            st.error(f"Error loading resources: {e}")
            st.session_state.resources[topic_index] = None

    # 2. Load exercise
    exercise_skill = ExerciseGeneratorSkill(llm)
    exercise_agent = ExerciseAgent(exercise_skill)
    exercise_rules = {
        "subject": topic,
        "level": st.session_state.difficulty_level.lower(),
        "mistakes": st.session_state.mistakes if st.session_state.mistakes else ["None"]
    }
    
    with st.spinner("🧠 Preparing practice exercise..."):
        try:
            exercise_raw = exercise_agent.run(exercise_rules)
            st.session_state.exercise[topic_index] = safe_json_loads(exercise_raw)
        except Exception as e:
            st.error(f"Error generating exercise: {e}")
            st.session_state.exercise[topic_index] = None
            
    # Reset validation for this new topic attempt
    st.session_state.validation[topic_index] = None

    if not st.session_state.get("learning_path"):
        return

    save_memory()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎓 AI Personal Tutor")
    st.write("Configure your learning goals below.")

    # Form / Preferences
    subject = st.text_input("What do you want to learn?", value="Python", key="subject_input")
    st.session_state.subject = subject
    
    learning_style = st.selectbox(
        "Preferred Learning Style",
        ["Video", "Text", "Mixed", "Projects"],
        key="learning_style_select"
    )
    st.session_state.learning_style = learning_style
    
    difficulty_level = st.selectbox(
        "Difficulty Level",
        ["Beginner", "Intermediate", "Advanced"],
        key="difficulty_select"
    )
    st.session_state.difficulty_level = difficulty_level

    # Optional Custom API Key input
    api_key_input = st.text_input("Gemini API Key (Optional - use your own if server key fails)", type="password")
    if api_key_input.strip():
        st.session_state.api_key = api_key_input.strip()

    st.markdown("---")

    # Generate Roadmap Button
    if st.button("Generate Learning Path 🚀", type="primary", use_container_width=True):
        llm = GeminiLLM(st.session_state.api_key)
        planner_skill = PlannerSkill(llm)
        planner_agent = LearningPathAgent(planner_skill)
        
        difficulty_mapping = {
            "Beginner": 0,
            "Intermediate": 1,
            "Advanced": 2
        }
        
        user_preferences = {
            "subject": st.session_state.subject,
            "known_topics": ["None"],
            "learning_style": st.session_state.learning_style.lower(),
            "difficulty_level": difficulty_mapping[st.session_state.difficulty_level]
        }
        
        with st.spinner("🗺️ Designing your custom curriculum roadmap..."):
            try:
                path_raw = planner_agent.run(user_preferences)
                st.session_state.learning_path = safe_json_loads(path_raw)
                st.session_state.current_topic_index = 0
                st.session_state.resources = {}
                st.session_state.exercise = {}
                st.session_state.validation = {}
                st.session_state.skills_progress = []

                save_memory()               
                
                # Fetch first topic data
                load_topic_data(0)
                st.success("Successfully generated learning path!")
            except Exception as e:
                st.error(f"Failed to generate learning path: {e}")
        
        st.session_state.memory_loaded = False

    st.markdown("---")

    # Restart button (needs memory to be initialised first, so it lives here)
    if st.session_state.get("learning_path"):
        if st.button("🔄 Restart Roadmap Course", use_container_width=True):
            st.session_state.learning_path = None
            st.session_state.current_topic_index = 0
            st.session_state.resources = {}
            st.session_state.exercise = {}
            st.session_state.validation = {}
            st.session_state.skills_progress = []
            st.session_state.mistakes = []
            st.session_state.memory_loaded = False
            memory.save({})
            st.rerun()
        st.markdown("---")

    if st.button("🚪 Logout"):
        st.session_state.user_id = None
        st.session_state.memory_loaded = False
        st.rerun()
    
    # Dashboard / Stats
    if st.session_state.learning_path:
        st.markdown(f"### 🔥 Streak: **{st.session_state.streak} Days**")
        
        # Progress Bar
        total_topics = len(st.session_state.learning_path["topics"])
        completed_topics = st.session_state.current_topic_index
        progress_val = completed_topics / total_topics
        st.markdown(f"**Path Completion:** {completed_topics}/{total_topics} topics")
        st.progress(progress_val)
        
        # Mistake history
        if st.session_state.mistakes:
            with st.expander("⚠️ Mistake Journal"):
                for m in st.session_state.mistakes:
                    st.caption(m)
        
        # Skill improvement over time chart
        if st.session_state.skills_progress:
            st.markdown("### 📊 Skill Mastery")
            df = pd.DataFrame(st.session_state.skills_progress)
            st.dataframe(df, hide_index=True)
            
            # Simple chart
            st.line_chart(df.set_index("topic")["score"])

# --- MAIN PANEL ---
if not st.session_state.learning_path:
    st.markdown("""
    # Welcome to your Personal AI Tutor! 🚀
    
    This platform uses state-of-the-art AI agents to curate a personalized curriculum, recommend optimal resources, generate practice exercises, and automatically evaluate your work.
    
    ### 🎯 How to start:
    1. Enter the **Subject** you want to learn in the sidebar.
    2. Choose your **Learning Style** and **Difficulty Level**.
    3. Click **Generate Learning Path** to start your roadmap!
    """)
else:
    topics = st.session_state.learning_path["topics"]
    
    # 1. Road Map Visualization (Duolingo Style)
    st.markdown("### 🗺️ Curriculum Roadmap")
    html_roadmap = "<div class='roadmap-container'>"
    for idx, t in enumerate(topics):
        status_class = "locked"
        symbol = str(idx + 1)
        if idx < st.session_state.current_topic_index:
            status_class = "completed"
            symbol = "✓"
        elif idx == st.session_state.current_topic_index:
            status_class = "active"
            symbol = "★"

        label_class = "active" if status_class == "active" else ""
        html_roadmap += (
            f'<div class="roadmap-step">'
            f'<div class="circle {status_class}">{symbol}</div>'
            f'<div class="label {label_class}">{t}</div>'
            f'</div>'
        )
    html_roadmap += "</div>"
    st.markdown(html_roadmap, unsafe_allow_html=True)

    # Current topic metadata
    current_topic = topics[st.session_state.current_topic_index]
    st.title(f"🎯 Current Topic: {current_topic}")

    # 2. Learning Resources Section
    res_data = st.session_state.resources.get(st.session_state.current_topic_index)
    if res_data:
        st.subheader("📚 Recommended Learning Resources")
        
        # Display learning objective
        if res_data.get("learning_objective"):
            st.info(f"💡 **Learning Objective:** {res_data.get('learning_objective')}")
            
        # Featured recommendation
        rec = res_data.get("recommended_resource")
        if rec:
            st.markdown(f"#### 🌟 Featured Resource: [{rec.get('title')}]({rec.get('url')})")
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**Type:** `{rec.get('type')}`")
                if rec.get('watch'):
                    st.markdown(f"**Target:** {rec.get('watch')}")
            with col2:
                st.markdown(f"**Why it's recommended:** {rec.get('reason')}")
        
        # Optional resources
        opts = res_data.get("optional_resources", [])
        if opts:
            with st.expander("🔗 Optional/Alternative Resources"):
                for opt in opts:
                    st.markdown(f"- [{opt.get('title')}]({opt.get('url')})")
                    
        # Estimated learning time
        if res_data.get("estimated_time"):
            st.caption(f"⏱️ **Estimated Study Time:** {res_data.get('estimated_time')}")
    else:
        st.info("No learning resources loaded for this topic yet.")

    st.markdown("---")

    # 3. Exercise Section
    ex_data = st.session_state.exercise.get(st.session_state.current_topic_index)
    if not ex_data:
        load_topic_data(st.session_state.current_topic_index)
        ex_data = st.session_state.exercise.get(st.session_state.current_topic_index)

    if ex_data:
        st.subheader("📝 Practice Exercise")
        st.write(f"### {ex_data.get('title', 'Exercise')}")
        st.markdown(ex_data.get("description", ""))
        
        exercise_type = ex_data.get("exercise_type", "coding")
        expected_file_type = ex_data.get("expected_file_type", ".py")
        
        user_submission = None
        temp_file_path = None
        
        # Render appropriate input widget
        if exercise_type == "coding":
            st.markdown(f"**Upload your python file (`{expected_file_type}`):**")
            uploaded_file = st.file_uploader(
                "Choose .py file",
                type=["py"],
                key=f"uploader_{st.session_state.current_topic_index}"
            )
            if uploaded_file is not None:
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                user_submission = temp_file_path

        elif exercise_type == "image":
            st.markdown(f"**Upload your drawing (`{expected_file_type}` / `.jpg`):**")
            uploaded_file = st.file_uploader(
                "Choose image file",
                type=["png", "jpg", "jpeg"],
                key=f"uploader_{st.session_state.current_topic_index}"
            )
            if uploaded_file is not None:
                temp_dir = tempfile.gettempdir()
                file_ext = os.path.splitext(uploaded_file.name)[1]
                if not file_ext:
                    file_ext = ".png"
                temp_file_path = os.path.join(temp_dir, f"submission_{st.session_state.current_topic_index}{file_ext}")
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                user_submission = temp_file_path
                
                # Image Preview
                st.image(uploaded_file, caption="Preview of your drawing submission", use_container_width=True)

        elif exercise_type == "text":
            st.markdown("**Write your solution below:**")
            user_text_input = st.text_area(
                "Your Response:",
                height=150,
                key=f"text_{st.session_state.current_topic_index}"
            )
            if user_text_input.strip():
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, f"submission_{st.session_state.current_topic_index}.txt")
                with open(temp_file_path, "w", encoding="utf-8") as f:
                    f.write(user_text_input)
                user_submission = temp_file_path

        # 4. Validation Action
        val_data = st.session_state.validation.get(st.session_state.current_topic_index)
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if user_submission:
                btn_clicked = st.button("🚀 Evaluate Submission", type="primary")
            else:
                btn_clicked = st.button("🚀 Evaluate Submission", type="primary", disabled=True)
                st.caption("Please upload a file or write a response to evaluate.")
                
            if btn_clicked and user_submission:
                llm = GeminiLLM(st.session_state.api_key)
                code_evaluator_tool = CodeEvaluatorTool()
                
                validation_agent = ValidationAgent(
                    code_validation_skill=CodeValidationSkill(code_evaluator_tool),
                    text_validation_skill=TextValidationSkill(llm),
                    image_validation_skill=ImageValidationSkill(llm)
                )
                
                with st.spinner("🔍 Grading submission..."):
                    try:
                        # Extension check
                        if not type_file_checking(user_submission, expected_file_type):
                            st.error(f"Invalid file type. Expected: {expected_file_type}")
                        else:
                            val_data = validation_agent.run(ex_data, user_submission)
                            st.session_state.validation[st.session_state.current_topic_index] = val_data
                            
                            score = val_data.get("score", 0)
                            
                            # Log/update skill metrics
                            st.session_state.skills_progress = [
                                item for item in st.session_state.skills_progress if item["topic"] != current_topic
                            ]
                            st.session_state.skills_progress.append({
                                "topic": current_topic,
                                "score": score
                            })
                            
                            if score >= 80:
                                st.session_state.streak += 1
                            else:
                                mistake_msg = f"Mistake on '{current_topic}': (Score {score}/100) Feedback: {val_data.get('feedback', '')}"
                                st.session_state.mistakes.append(mistake_msg)
                                
                            # -------------------------
                            # MEMORY SAVE (IMPORTANT)
                            # -------------------------
                            save_memory()
                            
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error during grading: {e}")
                        
        # 5. Validation Results & Next Steps
        if val_data is not None:
            score = val_data.get("score", 0)
            passed = val_data.get("passed", score >= 80)
            feedback = val_data.get("feedback", "")
            
            st.markdown("### 📊 Evaluation Result")
            if score >= 80:
                st.success(f"✅ **Passed! Score: {score}/100**")
                st.markdown(f"**Teacher Feedback:**\n{feedback}")
                
                # Next Topic Navigation
                if st.session_state.current_topic_index < len(topics) - 1:
                    if st.button("➡️ Next Topic", type="primary"):
                        st.session_state.current_topic_index += 1
                        save_memory()
                        load_topic_data(st.session_state.current_topic_index)
                        st.rerun()
                else:
                    st.balloons()
                    st.success("🎓 Congratulations! You completed the entire roadmap course!")
                    if st.button("🔄 Restart Roadmap Course"):
                        st.session_state.learning_path = None
                        st.session_state.current_topic_index = 0
                        st.session_state.resources = {}
                        st.session_state.exercise = {}
                        st.session_state.validation = {}
                        st.session_state.skills_progress = []
                        st.session_state.mistakes = []
                        st.session_state.memory_loaded = False
                        st.rerun()
            else:
                st.error(f"❌ **Failed. Score: {score}/100 (Required: 80/100)**")
                st.markdown(f"**Teacher Feedback:**\n{feedback}")
                st.warning("💡 Modify your submission and click 'Evaluate Submission' to try again.")
    else:
        st.info("No exercise generated for this topic yet.")
