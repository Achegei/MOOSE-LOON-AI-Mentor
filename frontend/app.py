"""
Streamlit frontend for MOOSE LOON AI Mentor Platform.
"""

import streamlit as st
import sys
from pathlib import Path

import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings

st.set_page_config(
    page_title="MOOSE LOON AI Mentor",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    body {
        background: #f4f7fb;
    }
    .stApp {
        color: #0f172a;
    }
    .main .block-container {
        padding-top: 1.5rem;
    }
    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.06);
        border: 1px solid rgba(15, 23, 42, 0.08);
    }
    .hero-banner {
        background: linear-gradient(135deg, #4338ca 0%, #0ea5e9 100%);
        border-radius: 24px;
        padding: 2rem;
        color: white;
    }
    .hero-banner h1 {
        margin: 0;
        line-height: 1.1;
    }
    .hero-banner p {
        opacity: 0.95;
        font-size: 1.05rem;
    }
    .stButton button {
        border-radius: 12px;
    }
    .stTextInput>div>div>input {
        border-radius: 12px;
    }
    .stTextArea>div>div>textarea {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

api_host = "127.0.0.1" if settings.API_HOST == "0.0.0.0" else settings.API_HOST
API_DEFAULT_URL = f"http://{api_host}:{settings.API_PORT}"


def get_headers():
    token = st.session_state.get("access_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def ensure_session_state():
    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None
    if "refresh_token" not in st.session_state:
        st.session_state["refresh_token"] = None
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "conversation_id" not in st.session_state:
        st.session_state["conversation_id"] = None
    if "api_url" not in st.session_state:
        st.session_state["api_url"] = API_DEFAULT_URL
    if "auth_message" not in st.session_state:
        st.session_state["auth_message"] = None


def set_auth_message(level: str, text: str):
    st.session_state["auth_message"] = {"level": level, "text": text}


def require_auth() -> bool:
    """Show an auth warning and return whether the learner is logged in."""
    if not st.session_state["access_token"]:
        st.warning("Please login on the sidebar to access this mentor feature.")
        return False
    return True


def api_get(api_url: str, path: str):
    """Call a protected GET endpoint and return JSON data."""
    try:
        response = requests.get(
            f"{api_url}{path}",
            headers=get_headers(),
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        message = exc.response.text if exc.response is not None else str(exc)
        st.error(f"Request failed: {message}")
        return None


def api_post(api_url: str, path: str, payload: dict):
    """Call a protected POST endpoint and return JSON data."""
    try:
        response = requests.post(
            f"{api_url}{path}",
            headers=get_headers(),
            json=payload,
            timeout=45,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        message = exc.response.text if exc.response is not None else str(exc)
        st.error(f"Request failed: {message}")
        return None


def login(api_url: str, username_or_email: str, password: str):
    try:
        response = requests.post(
            f"{api_url}/auth/token",
            json={"username_or_email": username_or_email, "password": password},
            timeout=10,
        )
        response.raise_for_status()
        token_data = response.json()
        st.session_state["access_token"] = token_data.get("access_token")
        st.session_state["refresh_token"] = token_data.get("refresh_token")
        set_auth_message("success", "Logged in successfully.")
    except requests.RequestException as exc:
        message = exc.response.text if exc.response is not None else str(exc)
        set_auth_message("error", f"Login failed: {message}")


def register(api_url: str, email: str, username: str, password: str, full_name: str):
    try:
        response = requests.post(
            f"{api_url}/auth/register",
            json={
                "email": email,
                "username": username,
                "password": password,
                "full_name": full_name,
            },
            timeout=10,
        )
        response.raise_for_status()
        set_auth_message("success", "Registration successful. You can now login.")
    except requests.RequestException as exc:
        message = exc.response.text if exc.response is not None else str(exc)
        set_auth_message("error", f"Registration failed: {message}")


def send_chat(api_url: str, prompt: str):
    if not prompt:
        st.warning("Enter a question or prompt to send to your mentor.")
        return

    try:
        response = requests.post(
            f"{api_url}/chat/",
            headers=get_headers(),
            json={
                "prompt": prompt,
                "conversation_id": st.session_state.get("conversation_id"),
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        st.session_state["conversation_id"] = data.get("conversation_id")
        st.session_state["chat_history"].append(("You", prompt))
        st.session_state["chat_history"].append(("Mentor", data.get("reply")))
    except requests.RequestException as exc:
        message = exc.response.text if exc.response is not None else str(exc)
        st.error(f"Chat error: {message}")


def logout(api_url: str):
    try:
        response = requests.post(
            f"{api_url}/auth/logout",
            headers=get_headers(),
            json={"refresh_token": st.session_state.get("refresh_token")},
            timeout=10,
        )
        response.raise_for_status()
        st.session_state["access_token"] = None
        st.session_state["refresh_token"] = None
        st.session_state["conversation_id"] = None
        st.session_state["chat_history"] = []
        set_auth_message("success", "Logged out successfully.")
    except requests.RequestException as exc:
        message = exc.response.text if exc.response is not None else str(exc)
        st.error(f"Logout failed: {message}")


def main():
    """Main Streamlit application."""
    ensure_session_state()

    st.title("🫎 MOOSE LOON AI Mentor")
    st.subheader("A curriculum-first mentor for AI and automation learners")

    with st.sidebar:
        st.markdown("## Navigation")
        page = st.radio(
            "Select a page:",
            [
                "Home",
                "Chat with Mentor",
                "Learning Path",
                "Assignments",
                "Projects",
                "Portfolio",
                "Progress",
                "Settings",
            ],
        )

        st.markdown("---")
        st.markdown("### Backend Connection")
        api_url = st.text_input("API base URL", value=st.session_state["api_url"])
        st.session_state["api_url"] = api_url

        st.markdown("---")
        if st.session_state["auth_message"]:
            message = st.session_state["auth_message"]
            if message["level"] == "success":
                st.success(message["text"])
            elif message["level"] == "error":
                st.error(message["text"])
            else:
                st.info(message["text"])

        if st.session_state["access_token"]:
            st.success("Authenticated")
            st.button("Logout", on_click=logout, args=(api_url,))
        else:
            tabs = st.tabs(["Login", "Register"])
            with tabs[0]:
                st.markdown("**Login with your email or username**")
                username_or_email = st.text_input(
                    "Username or Email", key="login_username"
                )
                password = st.text_input(
                    "Password", type="password", key="login_password"
                )
                if st.button("Login"):
                    login(api_url, username_or_email, password)
            with tabs[1]:
                st.markdown("**Create a new learner account**")
                email = st.text_input("Email", key="register_email")
                username = st.text_input("Username", key="register_username")
                password = st.text_input(
                    "Password", type="password", key="register_password"
                )
                full_name = st.text_input("Full Name", key="register_full_name")
                if st.button("Register"):
                    register(api_url, email, username, password, full_name)

    if page == "Home":
        st.markdown(
            """
            <div class='hero-banner'>
                <h1>Build AI skills with a mentor that understands your journey.</h1>
                <p>Learn AI, automation, prompt engineering, and project workflows with guided advice and curriculum-backed coaching.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)
        col1.markdown(
            """
        <div class='metric-card'>
        <h3>Fast Setup</h3>
        <p>Connect your backend and start chatting with the mentor immediately.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        col2.markdown(
            """
        <div class='metric-card'>
        <h3>Secure Auth</h3>
        <p>JWT login and protected chat flow keep your learner sessions safe.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        col3.markdown(
            """
        <div class='metric-card'>
        <h3>Curriculum Focus</h3>
        <p>Designed for AI and automation learning, not generic chit-chat.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown(
            f"""
            ### Ready for action
            - Connect to the backend API
            - Register a learner account
            - Chat with the mentor
            - Build your first learning path

            **Backend:** `{api_url}`
            **Environment:** `{settings.ENVIRONMENT}`
            """
        )

    elif page == "Chat with Mentor":
        st.markdown("### Chat with Your Mentor")
        if not st.session_state["access_token"]:
            st.warning("Please login on the sidebar to access chat.")
        else:
            prompt = st.text_area(
                "Ask your mentor anything about AI, automation, or project planning.",
                height=140,
            )
            if st.button("Send"):
                send_chat(api_url, prompt)

            if st.session_state["chat_history"]:
                for speaker, message in st.session_state["chat_history"]:
                    if speaker == "You":
                        st.chat_message("user").write(message)
                    else:
                        st.chat_message("assistant").write(message)

    elif page == "Learning Path":
        st.markdown("### Your Learning Path")
        if require_auth():
            goals = st.text_area(
                "Learning goals",
                placeholder="Example: I want to learn AI agents and build an n8n portfolio project.",
            )
            skill_level = st.selectbox(
                "Skill level",
                ["beginner", "intermediate", "advanced"],
            )
            if st.button("Save Goals"):
                goal_items = [item.strip() for item in goals.splitlines() if item.strip()]
                result = api_post(
                    api_url,
                    "/memory/goals",
                    {"goals": goal_items, "skill_level": skill_level},
                )
                if result:
                    st.success("Goals saved.")

            if st.button("Generate Learning Path"):
                path = api_get(api_url, "/learning-path")
                if path:
                    for item in path["recommendations"]:
                        with st.container():
                            st.markdown(f"**{item['title']}**")
                            st.caption(f"{item['topic']} | {item['difficulty']}")
                            st.write(item["next_action"])

    elif page == "Assignments":
        st.markdown("### Assignments & Exercises")
        if require_auth():
            topic = st.selectbox(
                "Topic",
                ["AI Literacy", "Prompt Engineering", "APIs", "n8n", "AI Agents", "Portfolio"],
            )
            assignment_type = st.selectbox("Type", ["exercise", "quiz", "mini project"])
            difficulty = st.selectbox("Difficulty", ["beginner", "intermediate", "advanced"])
            if st.button("Generate Assignment"):
                assignment = api_post(
                    api_url,
                    "/assignments/generate",
                    {
                        "topic": topic,
                        "assignment_type": assignment_type,
                        "difficulty": difficulty,
                    },
                )
                if assignment:
                    st.markdown(f"**{assignment['title']}**")
                    st.caption(assignment["description"])
                    st.write(assignment["content"])

    elif page == "Projects":
        st.markdown("### Project Guidance")
        if require_auth():
            goal = st.text_area(
                "Project goal",
                value="Build a portfolio project that demonstrates AI, APIs, and automation.",
            )
            difficulty = st.selectbox(
                "Project difficulty",
                ["beginner", "intermediate", "advanced"],
            )
            if st.button("Recommend Project"):
                project = api_post(
                    api_url,
                    "/projects/recommend",
                    {"goal": goal, "difficulty": difficulty},
                )
                if project:
                    st.markdown(f"**{project['title']}**")
                    st.caption(f"Status: {project['status']}")
                    st.write(project["description"])

    elif page == "Portfolio":
        st.markdown("### Portfolio Review")
        if require_auth():
            project_title = st.text_input("Project title")
            repository_url = st.text_input("Repository URL")
            project_description = st.text_area(
                "Project description",
                placeholder="Describe the problem, users, features, tech stack, and current blockers.",
                height=180,
            )
            if st.button("Review Portfolio"):
                review = api_post(
                    api_url,
                    "/portfolio-review",
                    {
                        "project_title": project_title,
                        "project_description": project_description,
                        "repository_url": repository_url or None,
                    },
                )
                if review:
                    st.write(review["review"])

    elif page == "Progress":
        st.markdown("### Your Progress")
        if require_auth():
            if st.button("Refresh Progress"):
                summary = api_get(api_url, "/progress/summary")
                if summary:
                    memory = summary["memory"]
                    st.markdown("#### Memory")
                    st.write(f"Skill level: {memory['skill_level']}")
                    st.write("Goals:", memory["goals"])
                    st.write("Learning path:", memory["learning_path"])
                    st.markdown("#### Assignments")
                    st.table(summary["assignments"])
                    st.markdown("#### Projects")
                    st.table(summary["projects"])
                    st.markdown("#### Module Progress")
                    st.table(summary["progress"])

            st.markdown("#### Update Module Progress")
            module_id = st.number_input("Module ID", min_value=1, step=1)
            progress_percentage = st.slider("Progress percentage", 0, 100, 25)
            completed = st.checkbox("Completed")
            if st.button("Save Progress"):
                result = api_post(
                    api_url,
                    "/progress/update",
                    {
                        "module_id": int(module_id),
                        "progress_percentage": float(progress_percentage),
                        "completed": completed,
                    },
                )
                if result:
                    st.success("Progress saved.")

    elif page == "Settings":
        st.markdown("### Settings")
        if require_auth():
            session = api_get(api_url, "/settings/session")
            if session:
                st.write(f"Username: {session['username']}")
                st.write(f"Email: {session['email']}")
                st.write(f"Skill level: {session['skill_level']}")


if __name__ == "__main__":
    main()
