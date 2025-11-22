import streamlit as st
import json, os, hashlib, uuid
from datetime import datetime

DATA_FILE = "data.json"
st.set_page_config(page_title="Simple Learn", layout="wide")

# ----------------------------------------------
# THEME (Soft Gradient)
# ----------------------------------------------
THEME_CSS = """
<style>
body {
    background-color: #f4f7fb;
}

.gradient-header {
    background: linear-gradient(90deg, #4f46e5, #9333ea, #06b6d4);
    padding: 25px;
    border-radius: 12px;
    color: white;
    font-size: 36px;
    font-weight: 800;
    margin-bottom: 20px;
}

.category-card, .course-card {
    background: white;
    padding: 18px;
    margin-bottom: 15px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 3px 12px rgba(0,0,0,0.07);
}

button, .stButton>button {
    background-color: #6366f1 !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 6px !important;
    padding: 8px 14px !important;
}

.cat-chip {
    background:#ecebff;
    padding:6px 12px;
    border-radius:999px;
    font-size:14px;
    color:#4f46e5;
    font-weight:600;
}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ----------------------------------------------
# DATA FUNCTIONS
# ----------------------------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        init = {
            "users": {},
            "categories": {},
            "courses": {},
            "progress": {}
        }

        # Create categories
        category_list = [
            ("Programming", "Learn basics and advanced coding."),
            ("Data Science", "ML, AI, Data Analysis."),
            ("Cybersecurity", "Ethical Hacking & Security."),
            ("Web Development", "HTML, CSS, JS, Backend."),
            ("Cloud / DevOps", "Cloud, Docker, Kubernetes.")
        ]

        cat_ids = []
        for title, desc in category_list:
            cid = str(uuid.uuid4())
            init["categories"][cid] = {"id": cid, "title": title, "desc": desc}
            cat_ids.append(cid)

        # Add sample courses with REAL YouTube videos
        def add_course(title, desc, category, videos):
            cid = str(uuid.uuid4())
            init["courses"][cid] = {
                "id": cid,
                "title": title,
                "desc": desc,
                "category_id": category,
                "videos": videos
            }

        add_course("Python Basics", "Start Python from zero.",
                   cat_ids[0],
                   [
                       ("Python Full Course", "https://www.youtube.com/watch?v=gfDE2a7MKjA"),
                       ("Variables & Data Types", "https://www.youtube.com/watch?v=b093aqAZiPU"),
                       ("Loops in Python", "https://www.youtube.com/watch?v=6iF8Xb7Z3wQ"),
                   ])

        add_course("Algorithms 101", "Learn basic algorithms.",
                   cat_ids[0],
                   [
                       ("What Are Algorithms?", "https://www.youtube.com/watch?v=8hly31xKli0"),
                       ("Sorting Algorithms", "https://www.youtube.com/watch?v=kgBjXUE_Nwc"),
                   ])

        add_course("Machine Learning Basics", "Intro to ML.",
                   cat_ids[1],
                   [
                       ("ML Course", "https://www.youtube.com/watch?v=Gv9_4yMHFhI"),
                       ("Regression Basics", "https://www.youtube.com/watch?v=kHwlB_j7Hkc")
                   ])

        add_course("Ethical Hacking Intro", "Learn cybersecurity fundamentals.",
                   cat_ids[2],
                   [
                       ("Hacking Basics", "https://www.youtube.com/watch?v=3Kq1MIfTWCE"),
                       ("Linux for Hackers", "https://www.youtube.com/watch?v=a4Z3IazpU8A")
                   ])

        add_course("HTML & CSS", "Web design and styling.",
                   cat_ids[3],
                   [
                       ("HTML Full Course", "https://www.youtube.com/watch?v=pQN-pnXPaVg"),
                       ("CSS Course", "https://www.youtube.com/watch?v=1Rs2ND1ryYc")
                   ])

        with open(DATA_FILE, "w") as f:
            json.dump(init, f, indent=2)

    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ----------------------------------------------
# AUTH SYSTEM
# ----------------------------------------------
def hash_pass(password, salt):
    import hashlib
    return hashlib.sha256((salt + password).encode()).hexdigest()

def create_user(username, password):
    data = load_data()
    if username in data["users"]:
        return False, "User exists"
    salt = uuid.uuid4().hex
    data["users"][username] = {
        "id": str(uuid.uuid4()),
        "password": hash_pass(password, salt) + ":" + salt
    }
    save_data(data)
    return True, "Account created!"

def login_user(username, password):
    data = load_data()
    if username not in data["users"]:
        return False, "User not found"
    stored = data["users"][username]["password"]
    hash_val, salt = stored.split(":")
    if hash_pass(password, salt) == hash_val:
        return True, data["users"][username]["id"]
    return False, "Wrong password"

# ----------------------------------------------
# SIDEBAR LOGIN
# ----------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

st.sidebar.title("Simple Learn")

if st.session_state.user:
    st.sidebar.success(f"Logged in as {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
else:
    st.sidebar.subheader("Login")
    un = st.sidebar.text_input("Username")
    pw = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        ok, res = login_user(un, pw)
        if ok:
            st.session_state.user = un
        else:
            st.sidebar.error(res)

    st.sidebar.subheader("Sign up")
    sun = st.sidebar.text_input("New Username")
    spw = st.sidebar.text_input("New Password", type="password")
    if st.sidebar.button("Create Account"):
        ok, msg = create_user(sun, spw)
        st.sidebar.success(msg) if ok else st.sidebar.error(msg)

# ----------------------------------------------
# PAGE NAVIGATION
# ----------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_category" not in st.session_state:
    st.session_state.selected_category = None

if "selected_course" not in st.session_state:
    st.session_state.selected_course = None

data = load_data()

# ----------------------------------------------
# HEADER
# ----------------------------------------------
st.markdown('<div class="gradient-header">Simple Learn — Online Courses</div>', unsafe_allow_html=True)

# ----------------------------------------------
# HOME PAGE (Categories)
# ----------------------------------------------
if st.session_state.page == "home":
    st.header("Choose a Category")

    cols = st.columns(2)
    i = 0

    for cid, cat in data["categories"].items():
        with cols[i % 2]:
            st.markdown('<div class="category-card">', unsafe_allow_html=True)
            st.write(f"## {cat['title']}")
            st.write(cat["desc"])
            if st.button(f"View {cat['title']} Courses", key=f"cat_{cid}"):
                st.session_state.selected_category = cid
                st.session_state.page = "category"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        i += 1

# ----------------------------------------------
# CATEGORY PAGE (Courses)
# ----------------------------------------------
elif st.session_state.page == "category":
    cat_id = st.session_state.selected_category
    cat = data["categories"][cat_id]

    st.header(f"{cat['title']} Courses")

    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    for cid, course in data["courses"].items():
        if course["category_id"] == cat_id:
            st.markdown('<div class="course-card">', unsafe_allow_html=True)
            st.write(f"### {course['title']}")
            st.write(course["desc"])
            if st.button(f"Open {course['title']}", key=f"open_{cid}"):
                st.session_state.selected_course = cid
                st.session_state.page = "course"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------
# COURSE PAGE (Videos)
# ----------------------------------------------
elif st.session_state.page == "course":
    cid = st.session_state.selected_course
    course = data["courses"][cid]

    st.header(course["title"])
    st.write(course["desc"])

    if st.button("⬅ Back to Category"):
        st.session_state.page = "category"
        st.rerun()

    st.write("---")
    st.subheader("Lessons")

    for title, url in course["videos"]:
        st.write(f"### {title}")
        st.video(url)
        st.write("---")
