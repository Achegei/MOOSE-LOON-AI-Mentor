"""Streamlit learner workspace for the MOOSE LOON AI Mentor Platform."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import requests
import streamlit as st
import streamlit.components.v1 as components

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
    :root {
        --ml-ink: #162033;
        --ml-muted: #647084;
        --ml-border: #d7dde8;
        --ml-panel: #ffffff;
        --ml-soft: #eef6f4;
        --ml-bg: #f4f6f9;
        --ml-teal: #0e766e;
        --ml-amber: #b45f06;
        --ml-blue: #275fd3;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(14,118,110,.12), transparent 32rem),
            linear-gradient(180deg, #f8fafc 0%, var(--ml-bg) 42%, #eef2f7 100%);
        color: var(--ml-ink);
    }
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1240px;
    }
    h1, h2, h3 {
        letter-spacing: 0;
    }
    .app-shell {
        background: var(--ml-panel);
        border: 1px solid var(--ml-border);
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .hero-panel {
        background:
            linear-gradient(135deg, rgba(22,32,51,.98) 0%, rgba(14,118,110,.96) 62%, rgba(180,95,6,.92) 100%);
        color: #ffffff;
        border-radius: 12px;
        padding: 1.6rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 18px 42px rgba(22,32,51,.16);
    }
    .hero-panel h1 {
        margin: 0 0 .5rem 0;
        font-size: 2rem;
        line-height: 1.15;
    }
    .hero-panel p {
        max-width: 760px;
        margin: 0;
        color: rgba(255,255,255,.9);
    }
    .metric-card {
        background: var(--ml-panel);
        border: 1px solid var(--ml-border);
        border-radius: 10px;
        padding: 1rem;
        min-height: 136px;
        box-shadow: 0 10px 24px rgba(22,32,51,.05);
    }
    .metric-card .label {
        color: var(--ml-muted);
        font-size: .82rem;
        margin-bottom: .35rem;
    }
    .metric-card .value {
        color: var(--ml-ink);
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: .35rem;
    }
    .metric-card p {
        color: var(--ml-muted);
        margin: 0;
        font-size: .92rem;
    }
    .section-kicker {
        color: var(--ml-muted);
        font-size: .88rem;
        margin-bottom: .2rem;
    }
    .stButton button {
        border-radius: 8px;
        border: 1px solid var(--ml-border);
        min-height: 2.4rem;
        font-weight: 650;
    }
    .stButton button[kind="primary"] {
        background: var(--ml-teal);
        border-color: var(--ml-teal);
    }
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px;
    }
    [data-testid="stSidebar"] {
        background: #fbfcfe;
        border-right: 1px solid var(--ml-border);
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--ml-ink);
    }
    .workspace-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        background: rgba(255,255,255,.78);
        border: 1px solid var(--ml-border);
        border-radius: 12px;
        padding: .8rem 1rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(8px);
    }
    .workspace-header .brand {
        font-weight: 800;
        color: var(--ml-ink);
    }
    .workspace-header .status {
        color: var(--ml-muted);
        font-size: .92rem;
    }
    .pill {
        display: inline-block;
        padding: .2rem .55rem;
        border-radius: 999px;
        background: var(--ml-soft);
        color: var(--ml-teal);
        border: 1px solid rgba(14,118,110,.18);
        font-size: .82rem;
        font-weight: 650;
    }
    .plan-card {
        background: #ffffff;
        border: 1px solid var(--ml-border);
        border-radius: 10px;
        padding: 1rem;
        min-height: 330px;
        box-shadow: 0 10px 24px rgba(22,32,51,.05);
    }
    .plan-card h3 {
        margin: 0 0 .25rem 0;
    }
    .plan-card .price {
        font-size: 1.45rem;
        font-weight: 800;
        color: var(--ml-ink);
        margin: .25rem 0 .75rem 0;
    }
    .plan-card p, .plan-card li {
        color: var(--ml-muted);
        font-size: .92rem;
    }
    .dev-callout {
        background: #111827;
        border-radius: 10px;
        color: #f9fafb;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .dev-callout p {
        color: #d1d5db;
        margin-bottom: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

api_host = "127.0.0.1" if settings.API_HOST == "0.0.0.0" else settings.API_HOST
API_BASE_URL = f"http://{api_host}:{settings.API_PORT}"
REFRESH_COOKIE = "mlm_refresh_token"


def ensure_session_state() -> None:
    """Initialize Streamlit session state."""
    defaults = {
        "access_token": None,
        "refresh_token": None,
        "chat_history": [],
        "conversation_id": None,
        "auth_message": None,
        "learning_path": None,
        "assignment": None,
        "project": None,
        "portfolio_review": None,
        "progress_summary": None,
        "session_profile": None,
        "billing_tiers": None,
        "subscription": None,
        "developer_keys": None,
        "new_api_key": None,
        "cookie_action": None,
        "session_restored": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_headers() -> dict[str, str]:
    """Return auth headers for API requests."""
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def persist_refresh_cookie(refresh_token: str | None) -> None:
    """Queue browser cookie persistence for the refresh token."""
    st.session_state["cookie_action"] = {
        "action": "set",
        "refresh_token": refresh_token,
    }


def clear_refresh_cookie() -> None:
    """Queue browser cookie removal."""
    st.session_state["cookie_action"] = {"action": "clear"}


def render_cookie_sync() -> None:
    """Synchronize the refresh-token cookie in the browser."""
    action = st.session_state.get("cookie_action")
    if not action:
        return

    if action["action"] == "set" and action.get("refresh_token"):
        token = json.dumps(action["refresh_token"])
        script = f"""
        <script>
        const token = {token};
        document.cookie = "{REFRESH_COOKIE}=" + encodeURIComponent(token)
            + "; path=/; max-age=" + (60 * 60 * 24 * 30) + "; SameSite=Lax";
        </script>
        """
    else:
        script = f"""
        <script>
        document.cookie = "{REFRESH_COOKIE}=; path=/; max-age=0; SameSite=Lax";
        </script>
        """
    components.html(script, height=0)
    st.session_state["cookie_action"] = None


def restore_session_from_cookie() -> None:
    """Restore a Streamlit session after browser refresh using refresh-token rotation."""
    if st.session_state.get("access_token") or st.session_state.get("session_restored"):
        return
    st.session_state["session_restored"] = True
    refresh_token = st.context.cookies.get(REFRESH_COOKIE)
    if not refresh_token:
        return
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=15,
        )
        response.raise_for_status()
        token_data = response.json()
        st.session_state["access_token"] = token_data.get("access_token")
        st.session_state["refresh_token"] = token_data.get("refresh_token")
        persist_refresh_cookie(st.session_state["refresh_token"])
        st.session_state["session_profile"] = api_get("/settings/session")
    except requests.RequestException:
        clear_refresh_cookie()


def set_auth_message(level: str, text: str) -> None:
    """Store a short account message for the sidebar."""
    st.session_state["auth_message"] = {"level": level, "text": text}


def show_message(message: dict[str, str] | None) -> None:
    """Render a sidebar message."""
    if not message:
        return
    if message["level"] == "success":
        st.success(message["text"])
    elif message["level"] == "error":
        st.error(message["text"])
    else:
        st.info(message["text"])


def friendly_error(exc: requests.RequestException) -> str:
    """Return a learner-safe API error message."""
    if exc.response is None:
        return "The mentor service is not reachable. Please try again shortly."
    try:
        detail = exc.response.json().get("detail")
    except ValueError:
        detail = None
    if exc.response.status_code == 401:
        return "Your session expired. Please sign in again."
    if exc.response.status_code == 403:
        return detail or "Your current plan cannot access this action."
    if exc.response.status_code == 429:
        return detail or "Your monthly API limit has been reached."
    if exc.response.status_code >= 500:
        return "The mentor service had a temporary issue. Please try again."
    return detail or "The request could not be completed. Please review the form and try again."


def refresh_session() -> bool:
    """Refresh access credentials using the stored refresh token."""
    refresh_token = st.session_state.get("refresh_token") or st.context.cookies.get(REFRESH_COOKIE)
    if not refresh_token:
        return False
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=15,
        )
        response.raise_for_status()
        token_data = response.json()
        st.session_state["access_token"] = token_data.get("access_token")
        st.session_state["refresh_token"] = token_data.get("refresh_token")
        persist_refresh_cookie(st.session_state["refresh_token"])
        return True
    except requests.RequestException:
        st.session_state["access_token"] = None
        st.session_state["refresh_token"] = None
        clear_refresh_cookie()
        return False


def api_get(path: str) -> dict[str, Any] | None:
    """Call a protected GET endpoint."""
    try:
        response = requests.get(
            f"{API_BASE_URL}{path}",
            headers=get_headers(),
            timeout=25,
        )
        if response.status_code == 401 and refresh_session():
            response = requests.get(
                f"{API_BASE_URL}{path}",
                headers=get_headers(),
                timeout=25,
            )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(friendly_error(exc))
        return None


def api_post(path: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Call a protected POST endpoint."""
    try:
        response = requests.post(
            f"{API_BASE_URL}{path}",
            headers=get_headers(),
            json=payload,
            timeout=60,
        )
        if response.status_code == 401 and refresh_session():
            response = requests.post(
                f"{API_BASE_URL}{path}",
                headers=get_headers(),
                json=payload,
                timeout=60,
            )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(friendly_error(exc))
        return None


def api_delete(path: str) -> dict[str, Any] | None:
    """Call a protected DELETE endpoint."""
    try:
        response = requests.delete(
            f"{API_BASE_URL}{path}",
            headers=get_headers(),
            timeout=25,
        )
        if response.status_code == 401 and refresh_session():
            response = requests.delete(
                f"{API_BASE_URL}{path}",
                headers=get_headers(),
                timeout=25,
            )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(friendly_error(exc))
        return None


def login(username_or_email: str, password: str, remember: bool = True) -> None:
    """Authenticate a learner."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/token",
            json={"username_or_email": username_or_email, "password": password},
            timeout=15,
        )
        response.raise_for_status()
        token_data = response.json()
        st.session_state["access_token"] = token_data.get("access_token")
        st.session_state["refresh_token"] = token_data.get("refresh_token")
        if remember:
            persist_refresh_cookie(st.session_state["refresh_token"])
        st.session_state["session_profile"] = api_get("/settings/session")
        set_auth_message("success", "Welcome back.")
    except requests.RequestException as exc:
        set_auth_message("error", friendly_error(exc))


def register(email: str, username: str, password: str, full_name: str) -> None:
    """Create a learner account."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "email": email,
                "username": username,
                "password": password,
                "full_name": full_name,
            },
            timeout=15,
        )
        response.raise_for_status()
        set_auth_message("success", "Account created. Sign in to begin.")
    except requests.RequestException as exc:
        set_auth_message("error", friendly_error(exc))


def logout() -> None:
    """End the learner session."""
    try:
        requests.post(
            f"{API_BASE_URL}/auth/logout",
            headers=get_headers(),
            json={"refresh_token": st.session_state.get("refresh_token")},
            timeout=15,
        )
    except requests.RequestException:
        pass
    for key in [
        "access_token",
        "refresh_token",
        "conversation_id",
        "session_profile",
        "learning_path",
        "assignment",
        "project",
        "portfolio_review",
        "progress_summary",
        "subscription",
        "developer_keys",
        "new_api_key",
    ]:
        st.session_state[key] = None
    st.session_state["chat_history"] = []
    clear_refresh_cookie()
    set_auth_message("success", "Signed out.")


def require_auth() -> bool:
    """Require a learner session for protected pages."""
    if st.session_state.get("access_token"):
        return True
    st.info("Sign in to continue.")
    return False


def send_chat(prompt: str) -> None:
    """Send a mentor chat request."""
    if not prompt.strip():
        st.warning("Ask a focused question so your mentor can help.")
        return
    result = api_post(
        "/chat/",
        {
            "prompt": prompt.strip(),
            "conversation_id": st.session_state.get("conversation_id"),
        },
    )
    if not result:
        return
    st.session_state["conversation_id"] = result.get("conversation_id")
    st.session_state["chat_history"].append(("You", prompt.strip()))
    st.session_state["chat_history"].append(("Mentor", result.get("reply", "")))


def render_metric(label: str, value: str, detail: str) -> None:
    """Render a compact dashboard card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <p>{detail}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workspace_header(page: str) -> None:
    """Render a polished top workspace header."""
    profile = st.session_state.get("session_profile") or {}
    name = profile.get("username", "Guest")
    tier = (st.session_state.get("subscription") or {}).get("tier", "free")
    st.markdown(
        f"""
        <div class="workspace-header">
            <div>
                <div class="brand">MOOSE LOON Workspace</div>
                <div class="status">{page} · {name}</div>
            </div>
            <div><span class="pill">{tier.title()} Plan</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    """Render navigation and account controls."""
    with st.sidebar:
        st.markdown("## MOOSE LOON")
        st.caption("AI and Automation Mentor")
        page = st.radio(
            "Workspace",
            [
                "Overview",
                "Mentor",
                "Learning Path",
                "Practice",
                "Projects",
                "Portfolio Review",
                "Progress",
                "Pricing",
                "Developers",
                "Account",
            ],
            label_visibility="collapsed",
        )

        st.divider()
        show_message(st.session_state.get("auth_message"))

        if st.session_state.get("access_token"):
            profile = st.session_state.get("session_profile") or api_get("/settings/session")
            st.session_state["session_profile"] = profile
            name = profile.get("username", "Learner") if profile else "Learner"
            level = profile.get("skill_level", "beginner") if profile else "beginner"
            st.markdown(f"**{name}**")
            st.caption(f"{level.title()} learner")
            st.button("Sign Out", on_click=logout, use_container_width=True)
        else:
            auth_tabs = st.tabs(["Sign In", "Create Account"])
            with auth_tabs[0]:
                identifier = st.text_input("Email or username", key="login_identifier")
                password = st.text_input("Password", type="password", key="login_password")
                remember = st.checkbox("Keep me signed in", value=True)
                if st.button("Sign In", use_container_width=True):
                    login(identifier, password, remember)
            with auth_tabs[1]:
                full_name = st.text_input("Full name", key="register_full_name")
                email = st.text_input("Email", key="register_email")
                username = st.text_input("Username", key="register_username")
                password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password",
                )
                if st.button("Create Account", use_container_width=True):
                    register(email, username, password, full_name)

    return page


def overview_page() -> None:
    """Render the learner dashboard."""
    render_workspace_header("Overview")
    st.markdown(
        """
        <div class="hero-panel">
            <h1>MOOSE LOON AI Mentor</h1>
            <p>Your structured mentor for AI literacy, prompt engineering, APIs, automation, agents, career growth, and portfolio execution.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric(
            "Mentor focus",
            "Curriculum-first",
            "Answers prioritize your AI and automation learning path.",
        )
    with col2:
        render_metric(
            "Practice loop",
            "Assignments",
            "Generate exercises, quizzes, and mini projects for your level.",
        )
    with col3:
        render_metric(
            "Career proof",
            "Portfolio",
            "Plan, review, and improve projects that demonstrate practical skill.",
        )

    st.markdown("### Continue Learning")
    if require_auth():
        summary = api_get("/progress/summary")
        if summary:
            memory = summary["memory"]
            left, right = st.columns([1, 1])
            with left:
                st.markdown("#### Current Goals")
                goals = memory.get("goals") or ["Set your first learning goal."]
                for goal in goals[:5]:
                    st.write(f"- {goal}")
            with right:
                st.markdown("#### Recommended Path")
                path = memory.get("learning_path") or ["Generate your learning path."]
                for item in path[:5]:
                    st.write(f"- {item}")


def mentor_page() -> None:
    """Render mentor chat."""
    render_workspace_header("Mentor")
    st.markdown("## Mentor")
    st.caption("Ask for coaching, explanations, debugging guidance, or career direction.")
    if not require_auth():
        return

    prompt = st.text_area(
        "Message",
        placeholder="Example: Help me understand how RAG works and give me a beginner exercise.",
        height=132,
        label_visibility="collapsed",
    )
    if st.button("Send to Mentor", use_container_width=True):
        send_chat(prompt)

    if st.session_state["chat_history"]:
        st.divider()
        for speaker, message in st.session_state["chat_history"]:
            avatar = "user" if speaker == "You" else "assistant"
            st.chat_message(avatar).write(message)


def learning_path_page() -> None:
    """Render learning path tools."""
    render_workspace_header("Learning Path")
    st.markdown("## Learning Path")
    st.caption("Set goals and generate a sequence of next lessons and skills.")
    if not require_auth():
        return

    with st.form("goals_form"):
        goals = st.text_area(
            "Goals",
            placeholder="Write one goal per line. Example: Build an n8n workflow that uses an AI API.",
            height=140,
        )
        skill_level = st.selectbox("Current level", ["beginner", "intermediate", "advanced"])
        submitted = st.form_submit_button("Save Goals", use_container_width=True)
    if submitted:
        goal_items = [item.strip() for item in goals.splitlines() if item.strip()]
        result = api_post(
            "/memory/goals",
            {"goals": goal_items, "skill_level": skill_level},
        )
        if result:
            st.success("Your learning profile was updated.")

    if st.button("Generate Path", use_container_width=True):
        st.session_state["learning_path"] = api_get("/learning-path")

    path = st.session_state.get("learning_path")
    if path:
        st.markdown("### Recommended Next Steps")
        for index, item in enumerate(path["recommendations"], start=1):
            st.markdown(f"**{index}. {item['title']}**")
            st.caption(f"{item['topic']} | {item['difficulty'].title()}")
            st.write(item["next_action"])


def practice_page() -> None:
    """Render assignment generation."""
    render_workspace_header("Practice")
    st.markdown("## Practice")
    st.caption("Create exercises, quizzes, and mini projects matched to your level.")
    if not require_auth():
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        topic = st.selectbox(
            "Topic",
            ["AI Literacy", "Prompt Engineering", "APIs", "n8n", "AI Agents", "Portfolio"],
        )
    with col2:
        assignment_type = st.selectbox("Format", ["exercise", "quiz", "mini project"])
    with col3:
        difficulty = st.selectbox("Level", ["beginner", "intermediate", "advanced"])

    if st.button("Generate Practice", use_container_width=True):
        st.session_state["assignment"] = api_post(
            "/assignments/generate",
            {
                "topic": topic,
                "assignment_type": assignment_type,
                "difficulty": difficulty,
            },
        )

    assignment = st.session_state.get("assignment")
    if assignment:
        st.markdown(f"### {assignment['title']}")
        st.caption(assignment["description"])
        st.write(assignment["content"])


def projects_page() -> None:
    """Render project coach."""
    render_workspace_header("Projects")
    st.markdown("## Projects")
    st.caption("Plan portfolio projects with clear milestones and proof of skill.")
    if not require_auth():
        return

    goal = st.text_area(
        "Project direction",
        value="Build a portfolio project that demonstrates AI, APIs, and workflow automation.",
        height=120,
    )
    difficulty = st.selectbox("Project level", ["beginner", "intermediate", "advanced"])
    if st.button("Create Project Plan", use_container_width=True):
        st.session_state["project"] = api_post(
            "/projects/recommend",
            {"goal": goal, "difficulty": difficulty},
        )

    project = st.session_state.get("project")
    if project:
        st.markdown(f"### {project['title']}")
        st.caption(f"Status: {project['status'].title()}")
        st.write(project["description"])


def portfolio_page() -> None:
    """Render portfolio review."""
    render_workspace_header("Portfolio Review")
    st.markdown("## Portfolio Review")
    st.caption("Get mentor feedback on project clarity, technical proof, and career signal.")
    if not require_auth():
        return

    with st.form("portfolio_form"):
        project_title = st.text_input("Project title")
        repository_url = st.text_input("Repository URL")
        project_description = st.text_area(
            "Project description",
            placeholder="Describe the problem, users, features, tech stack, tradeoffs, and what you want improved.",
            height=180,
        )
        submitted = st.form_submit_button("Review Portfolio", use_container_width=True)
    if submitted:
        st.session_state["portfolio_review"] = api_post(
            "/portfolio-review",
            {
                "project_title": project_title,
                "project_description": project_description,
                "repository_url": repository_url or None,
            },
        )

    review = st.session_state.get("portfolio_review")
    if review:
        st.markdown("### Mentor Review")
        st.write(review["review"])


def progress_page() -> None:
    """Render learner progress."""
    render_workspace_header("Progress")
    st.markdown("## Progress")
    st.caption("Track modules, assignments, projects, goals, and learning memory.")
    if not require_auth():
        return

    if st.button("Refresh Progress", use_container_width=True):
        st.session_state["progress_summary"] = api_get("/progress/summary")

    summary = st.session_state.get("progress_summary") or api_get("/progress/summary")
    st.session_state["progress_summary"] = summary
    if summary:
        memory = summary["memory"]
        left, right = st.columns(2)
        with left:
            st.markdown("### Learning Memory")
            st.write(f"Skill level: {memory['skill_level'].title()}")
            st.write("Goals")
            st.write(memory["goals"] or ["No goals saved yet."])
        with right:
            st.markdown("### Active Work")
            st.write("Assignments")
            st.table(summary["assignments"] or [{"title": "No assignments yet.", "submitted": False}])
            st.write("Projects")
            st.table(summary["projects"] or [{"title": "No projects yet.", "status": "planning"}])

    st.markdown("### Update Module Progress")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        module_id = st.number_input("Lesson number", min_value=1, step=1)
    with col2:
        progress_percentage = st.slider("Progress", 0, 100, 25)
    with col3:
        completed = st.checkbox("Completed")
    if st.button("Save Progress", use_container_width=True):
        result = api_post(
            "/progress/update",
            {
                "module_id": int(module_id),
                "progress_percentage": float(progress_percentage),
                "completed": completed,
            },
        )
        if result:
            st.success("Progress saved.")
            st.session_state["progress_summary"] = api_get("/progress/summary")


def pricing_page() -> None:
    """Render monetization tiers."""
    render_workspace_header("Pricing")
    st.markdown("## Pricing")
    st.caption("Choose the level that matches your learning, portfolio, and integration needs.")

    if st.session_state.get("billing_tiers") is None:
        st.session_state["billing_tiers"] = api_get("/billing/tiers")
    tiers_payload = st.session_state.get("billing_tiers")
    tiers = tiers_payload.get("tiers", []) if tiers_payload else []

    current = None
    if st.session_state.get("access_token"):
        current = api_get("/billing/subscription")
        st.session_state["subscription"] = current

    columns = st.columns(4)
    for column, tier in zip(columns, tiers):
        with column:
            st.markdown(
                f"""
                <div class="plan-card">
                    <h3>{tier["name"]}</h3>
                    <div class="price">{tier["price"]}</div>
                    <p>{tier["description"]}</p>
                    <p><strong>{tier['api_keys']}</strong> API keys · <strong>{tier['monthly_api_calls']:,}</strong> calls/month</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for feature in tier["features"]:
                st.write(f"- {feature}")
            is_current = current and current.get("tier") == tier["id"]
            if is_current:
                st.success("Current plan")
            elif st.session_state.get("access_token"):
                if st.button(f"Choose {tier['name']}", key=f"tier_{tier['id']}"):
                    result = api_post("/billing/subscription", {"tier": tier["id"]})
                    if result:
                        st.session_state["subscription"] = api_get("/billing/subscription")
                        st.success(f"{tier['name']} selected.")
            else:
                st.info("Sign in to choose")

    st.markdown("### Monetization Model")
    st.write(
        "The current implementation stores the selected tier in the application database. "
        "For production billing, connect this flow to a payment provider checkout and update "
        "the subscription from verified webhooks."
    )


def developers_page() -> None:
    """Render developer guide and API key management."""
    render_workspace_header("Developers")
    st.markdown("## Developers")
    st.caption("Integrate MOOSE LOON mentor capabilities into your own tools and workflows.")

    tabs = st.tabs(["Guide", "API Keys", "API Reference"])
    with tabs[0]:
        st.markdown(
            """
            <div class="dev-callout">
                <h3>Build mentorship into your own product</h3>
                <p>Use API keys to connect curriculum-grounded mentor responses to learning platforms, n8n workflows, internal tools, and portfolio systems.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### Developer Guide")
        st.write(
            "Use the API to bring curriculum-grounded AI and automation mentorship into "
            "learning portals, internal tools, n8n workflows, and portfolio coaching systems."
        )
        st.markdown("#### Integration Flow")
        st.write("1. Choose a paid tier with API access.")
        st.write("2. Generate an API key.")
        st.write("3. Send requests to the mentor endpoint with the `X-API-Key` header.")
        st.write("4. Store the key securely in your own system or automation platform.")
        st.markdown("#### Recommended Use Cases")
        st.write("- Embed mentor feedback inside a learning platform.")
        st.write("- Trigger AI assignment generation from an n8n workflow.")
        st.write("- Add portfolio review to a career coaching portal.")
        st.write("- Route internal AI literacy questions through a curriculum-first mentor.")

    with tabs[1]:
        st.markdown("### API Keys")
        if not require_auth():
            return

        subscription = api_get("/billing/subscription")
        keys_payload = api_get("/developer/api-keys")
        st.session_state["subscription"] = subscription
        st.session_state["developer_keys"] = keys_payload

        if subscription:
            plan = subscription["plan"]
            st.info(
                f"Current plan: {plan['name']} | {plan['api_keys']} keys | "
                f"{plan['monthly_api_calls']:,} calls/month"
            )

        with st.form("create_api_key_form"):
            key_name = st.text_input("Key name", placeholder="Production n8n workflow")
            submitted = st.form_submit_button("Create API Key", use_container_width=True)
        if submitted:
            result = api_post("/developer/api-keys", {"name": key_name or "Integration key"})
            if result:
                st.session_state["new_api_key"] = result["api_key"]
                st.session_state["developer_keys"] = api_get("/developer/api-keys")

        if st.session_state.get("new_api_key"):
            st.success("Copy this key now. It will not be shown again.")
            st.code(st.session_state["new_api_key"], language="text")

        keys_payload = st.session_state.get("developer_keys")
        keys = keys_payload.get("api_keys", []) if keys_payload else []
        if keys:
            st.markdown("#### Existing Keys")
            for key in keys:
                left, right = st.columns([3, 1])
                with left:
                    status = "Revoked" if key["revoked"] else "Active"
                    st.write(f"**{key['name']}**")
                    st.caption(
                        f"{key['key_prefix']}... | {status} | "
                        f"{key['requests_this_month']}/{key['monthly_limit']} calls"
                    )
                with right:
                    if not key["revoked"] and st.button("Revoke", key=f"revoke_{key['id']}"):
                        result = api_delete(f"/developer/api-keys/{key['id']}")
                        if result:
                            st.session_state["developer_keys"] = api_get("/developer/api-keys")
                            st.success("Key revoked.")
        else:
            st.write("No API keys yet.")

    with tabs[2]:
        st.markdown("### Mentor API")
        st.write("Endpoint")
        st.code("POST /v1/mentor/chat", language="text")
        st.write("Headers")
        st.code("X-API-Key: mlm_your_key_here", language="text")
        st.write("Request body")
        st.code(
            """{
  "prompt": "Explain prompt engineering to a beginner.",
  "learner_context": "The learner is new to APIs and n8n."
}""",
            language="json",
        )
        st.write("Example response")
        st.code(
            """{
  "reply": "Prompt engineering means...",
  "usage": {
    "monthly_limit": 1000,
    "requests_this_month": 12
  }
}""",
            language="json",
        )


def account_page() -> None:
    """Render account profile."""
    render_workspace_header("Account")
    st.markdown("## Account")
    if not require_auth():
        return

    profile = api_get("/settings/session")
    if profile:
        st.markdown("### Profile")
        st.write(f"Username: {profile['username']}")
        st.write(f"Email: {profile['email']}")
        st.write(f"Skill level: {profile['skill_level'].title()}")
        st.button("Sign Out", on_click=logout)


def main() -> None:
    """Run the Streamlit app."""
    ensure_session_state()
    restore_session_from_cookie()
    render_cookie_sync()
    page = render_sidebar()

    page_handlers = {
        "Overview": overview_page,
        "Mentor": mentor_page,
        "Learning Path": learning_path_page,
        "Practice": practice_page,
        "Projects": projects_page,
        "Portfolio Review": portfolio_page,
        "Progress": progress_page,
        "Pricing": pricing_page,
        "Developers": developers_page,
        "Account": account_page,
    }
    page_handlers[page]()
    render_cookie_sync()


if __name__ == "__main__":
    main()
