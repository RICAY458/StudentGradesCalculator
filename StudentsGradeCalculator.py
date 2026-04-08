import streamlit as st
import sqlite3
from dashboard import show_dashboard

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (first_name TEXT, surname TEXT, email TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def add_user(first_name, surname, email, password):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (first_name, surname, email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    data = c.fetchone()
    conn.close()
    return data
    

init_db()

def init_students_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  surname TEXT, firstname TEXT, course_yr TEXT, 
                  section TEXT, subject TEXT, attendance INTEGER, 
                  quiz INTEGER, exam INTEGER, project INTEGER, grade REAL)''')
    conn.commit()
    conn.close()

init_students_db()

# --- CUSTOM CSS ---
st.set_page_config(page_title="Student Grades Calculator", layout="centered")

st.markdown("""
    <style>
    /* 1. The Main Gradient Background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #E0EAFC 0%, #CFDEF3 100%) !important;
    }

    /* 2. Clear the top header background */
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0) !important;
    }

    /* 3. The Glassmorphism Card (White box) */
    [data-testid="stVerticalBlock"] > div:has(div.stContainer) {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* 4. Fix for the Blue Link Buttons (To be centered and underlined) */
    div[data-testid="stButton"] > button {
        background: none !important;
        border: none !important;
        color: #007BFF !important;
        text-decoration: underline !important;
        display: block !important;
        margin: 0 auto !important;
        font-weight: normal !important;
    }

    /* 5. Fix for the Primary Buttons (Blue solid) */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: #007BFF !important;
        color: white !important;
        text-decoration: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        width: 100% !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = 'login'

elif st.session_state.page == 'dashboard':
    # This is where the magic happens!
    show_dashboard()

# --- LOGIN PAGE ---
if st.session_state.page == 'login':
    st.session_state.page_title = 'Student Grades Calculator'
    # Custom CSS to make buttons look like blue text links AND center the Login button
    st.markdown("""
    <style>
    /* 1. Soft Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* 2. Glassmorphism Card Effect */
    [data-testid="stVerticalBlock"] > div:has(div.stContainer) {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    /* 3. Centered Primary Button */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(45deg, #007BFF, #00C6FF) !important;
        color: white !important;
        border: none !important;
        padding: 12px 30px !important;
        border-radius: 25px !important;
        width: 180px !important;
        display: block !important;
        margin: 20px auto !important;
        font-weight: bold !important;
        transition: transform 0.2s;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0, 123, 255, 0.4);
    }

    /* 4. Text Links Style */
    div[data-testid="stButton"] > button {
        background: none !important;
        border: none !important;
        color: #555 !important;
        text-decoration: underline !important;
        font-size: 14px !important;
    }

    /* 5. Center the Titles */
    h1 {
        color: #2c3e50;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    
    with col_mid:
        st.markdown("<h1 style='text-align: center;'>Login</h1>", unsafe_allow_html=True)
        
        with st.container(border=True):
            email = st.text_input("Email", placeholder="example@email.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            # Row for Remember Me and Forgot Password
            col1, col2 = st.columns([1, 1])
            with col1:
                st.checkbox("Remember me")
            with col2:
                # This now looks like a simple text link
                if st.button("Forgot Password?", key="forgot"):
                    st.toast("Check your email for reset instructions.")

            # Main Login Button
            if st.button("Log in", type="primary"):
                user = login_user(email, password)
                if user:
                    st.session_state.user_name = user[0] # Save the name for the dashboard
                    st.session_state.page = 'dashboard'  # Tell the app to switch pages
                    st.rerun() # Refresh to show the Dashboard immediately
                else:
                    st.error("Invalid credentials.")

        # Link for Create Account
        st.write("")
        st.write("Don't have an account?")
        if st.button("Create account", key="signup_link_btn"):
            st.session_state.page = 'signup'
            st.rerun()

# --- SIGNUP PAGE ---
elif st.session_state.page == 'signup':
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    
    with col_mid:
        st.markdown("<h1 style='text-align: center;'>Create Account</h1>", unsafe_allow_html=True)
        st.write("Join us to start calculating your student grades.")

        with st.container(border=True):
            sn = st.text_input("Surname")
            fn = st.text_input("First Name")
            em = st.text_input("Email")
            pw = st.text_input("Create Password", type="password")
            cp = st.text_input("Confirm Password", type="password")

            if st.button("Create account", type="primary"):
                if pw != cp:
                    st.error("Passwords do not match!")
                elif not fn or not em or not pw:
                    st.warning("Please fill in all fields.")
                else:
                    if add_user(fn, sn, em, pw):
                        st.balloons()
                        st.success("Account created successfully!")
                    else:
                        st.error("Email already exists.")

        st.write("Already have an account?")
        if st.button("Log in"):
            st.session_state.page = 'login'
            st.rerun()