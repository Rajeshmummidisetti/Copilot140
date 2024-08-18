import streamlit as st
import google.generativeai as genai
import os
import requests
import re

# Set up your Gemini API key
os.environ["API_KEY"] = "AIzaSyCnfZhx5ukV2_Ll9I-R8oeWqO3sjiZaQyU"
genai.configure(api_key=os.environ["API_KEY"])

# JDoodle API credentials
JD_API_URL = "https://api.jdoodle.com/v1/execute"
JD_CLIENT_ID = "d1919119ec9b0db122bce969dfe1ebfd"
JD_CLIENT_SECRET = "72ae62c266af5d5c06d0ee065f86beb6d6f1187229ac1c9ae5d8ff7dad334c52"

# Function to extract code from response
def extract_code_from_response(response_text):
    code_pattern = re.compile(r"```(?:\w+)?\s*([\s\S]*?)\s*```")
    match = code_pattern.search(response_text)
    if match:
        return match.group(1).strip()  # Extract and return the code block
    return response_text.strip()  # Return the full text if no code block is found

# Function to generate code using Gemini API
def generate_code(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return extract_code_from_response(response.text)

# Function to run code via JDoodle API
def run_code_with_jdoodle(code, language, version):
    data = {
        "script": code,
        "language": language,
        "versionIndex": version,
        "clientId": JD_CLIENT_ID,
        "clientSecret": JD_CLIENT_SECRET
    }
    response = requests.post(JD_API_URL, json=data)
    if response.status_code == 200:
        result = response.json()
        return result.get('output', 'No output')
    else:
        return f"Error: {response.status_code} - {response.text}"

# Streamlit UI
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>Copilot140</h1>", unsafe_allow_html=True)

# Initialize session state for control sets
if "control_sets" not in st.session_state:
    st.session_state.control_sets = [{"prompt": "", "generated_code": "", "output": "", "language": "Python"}]

# Function to add a new control set
def add_control_set():
    st.session_state.control_sets.append({"prompt": "", "generated_code": "", "output": "", "language": "Python"})

# Function to remove a control set
def remove_control_set(index):
    if len(st.session_state.control_sets) > 1:
        st.session_state.control_sets.pop(index)

# Display control sets
for idx, control_set in enumerate(st.session_state.control_sets):
    with st.expander("", expanded=True):
        col1, col2,col3, col4, col5, col6  = st.columns([1, 1,1,1,1,1])

        # Language selection
        with col1:
            if f"language_{idx}" not in st.session_state:
                st.session_state[f"language_{idx}"] = control_set.get("language", "Python")

            language = st.selectbox("Language:", ("Python", "Java", "C"), key=f"language_{idx}", index=("Python", "Java", "C").index(st.session_state[f"language_{idx}"]))
            st.session_state.control_sets[idx]["language"] = language


        # Generate Button with icon
        with col3:
            if st.button("✨", key=f"generate_{idx}"):
                generated_code = generate_code("Generate code for " + st.session_state.control_sets[idx]["prompt"] + " in " + st.session_state.control_sets[idx]["language"])
                st.session_state.control_sets[idx]["generated_code"] = generated_code

        # Run Button with icon
        with col4:
            if st.button("▶️", key=f"run_{idx}"):
                if st.session_state.control_sets[idx]["generated_code"]:
                    language = st.session_state.control_sets[idx]["language"]
                    language_map = {"Python": ("python3", "4"), "Java": ("java", "4"), "C": ("c", "5")}
                    jdoodle_language, jdoodle_version = language_map[language]
                    output = run_code_with_jdoodle(st.session_state.control_sets[idx]["generated_code"], jdoodle_language, jdoodle_version)
                    st.session_state.control_sets[idx]["output"] = output

        # Add Cell Button with icon
        with col5:
            if st.button("➕", key=f"add_{idx}"):
                add_control_set()

        # Remove Cell Button with icon
        with col6:
            if st.button("🗑️", key=f"remove_{idx}"):
                remove_control_set(idx)

        # Input field for code prompt
        prompt = st.text_input("Ask AI (e.g., 'binary search'):", key=f"prompt_{idx}")
        st.session_state.control_sets[idx]["prompt"] = prompt

        # Code box (fixed)
        modified_code = st.text_area("Code:", value=control_set["generated_code"],height=150,key=f"modifiable_code_{idx}")
        st.session_state.control_sets[idx]["generated_code"] = modified_code

        # Output box (only shows after running)
        if st.session_state.control_sets[idx]["output"]:
            st.text_area("Output:", value=st.session_state.control_sets[idx]["output"], height=50)

