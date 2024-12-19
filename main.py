import streamlit as st
import json

# Load user data from JSON
def load_users():
    with open("users.json", "r") as file:
        return json.load(file)["users"]

# Authenticate user credentials
def authenticate(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user["role"]
    return None

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# Login page
if not st.session_state.logged_in:
    st.title("Login Page")
    st.write("Enter your username and password.")

    # Input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = authenticate(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            if role == "admin":
                st.session_state.page = "pages/Admin"
            elif role == "user":
                st.session_state.page = "pages/User"
        else:
            st.error("Invalid username or password.")
else:
    # Navigate to the appropriate page
    if st.session_state.role == "admin":
        st.write("Redirecting to Admin Page...")
        st.stop()  # The actual Admin page is handled by Streamlit multi-page
    elif st.session_state.role == "user":
        st.write("Redirecting to User Page...")
        st.stop()
