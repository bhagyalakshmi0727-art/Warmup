import os
import streamlit as st
import requests
import pandas as pd

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000/api")

st.set_page_config(page_title="Collab Platform", layout="wide", page_icon="🤝")

def fetch_tasks():
    try:
        response = requests.get(f"{API_BASE_URL}/tasks")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
    return []

def fetch_notes():
    try:
        response = requests.get(f"{API_BASE_URL}/notes")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to connect to backend: {e}")
    return []

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Meeting Assistant", "Rough Notes", "AI Assistant"])

if page == "Dashboard":
    st.title("Task Dashboard")
    
    tasks = fetch_tasks()
    
    if tasks:
        # Metrics
        pending = sum(1 for t in tasks if t['status'] == 'Pending')
        completed = sum(1 for t in tasks if t['status'] == 'Completed')
        delayed = sum(1 for t in tasks if t['status'] == 'Delayed')
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Pending Tasks", pending)
        col2.metric("Completed Tasks", completed)
        col3.metric("Delayed Tasks", delayed)
        
        st.subheader("All Tasks")
        df = pd.DataFrame(tasks)
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Update Task Status")
        col1, col2 = st.columns(2)
        with col1:
            task_ids = [t['id'] for t in tasks]
            task_to_update = st.selectbox("Select Task ID", task_ids)
        with col2:
            new_status = st.selectbox("New Status", ["Pending", "Completed", "Delayed"])
            
        if st.button("Update Status"):
            res = requests.put(f"{API_BASE_URL}/tasks/{task_to_update}", json={"status": new_status})
            if res.status_code == 200:
                st.success("Task updated!")
                st.rerun()
    else:
        st.info("No tasks available. Go to Meeting Assistant to process a meeting or add manually.")
        
    st.subheader("Add Manual Task")
    with st.form("add_task_form"):
        t_title = st.text_input("Title")
        t_owner = st.text_input("Owner")
        t_deadline = st.date_input("Deadline")
        t_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        submitted = st.form_submit_button("Add Task")
        if submitted:
            res = requests.post(f"{API_BASE_URL}/tasks", json={
                "title": t_title,
                "owner": t_owner,
                "deadline": str(t_deadline),
                "priority": t_priority
            })
            if res.status_code == 201:
                st.success("Task added!")
                st.rerun()

elif page == "Meeting Assistant":
    st.title("Meeting Assistant")
    st.write("Paste your meeting transcript below to automatically generate a summary and extract action items.")
    
    transcript = st.text_area("Meeting Transcript", height=300)
    
    if st.button("Analyze Meeting"):
        if transcript:
            with st.spinner("Analyzing with AI..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/meetings/process", json={"transcript": transcript})
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Meeting processed successfully!")
                        st.subheader("Summary")
                        st.write(data.get("summary"))
                        
                        st.subheader("Extracted Tasks")
                        extracted = data.get("extracted_tasks", [])
                        if extracted:
                            df = pd.DataFrame(extracted)
                            st.table(df)
                        else:
                            st.info("No tasks extracted.")
                    else:
                        st.error("Error processing meeting.")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")
        else:
            st.warning("Please enter a transcript first.")

elif page == "Rough Notes":
    st.title("Employee Rough Notes")
    
    with st.form("add_note_form"):
        note_content = st.text_area("Write a quick note...")
        submitted = st.form_submit_button("Save Note")
        if submitted:
            if note_content:
                res = requests.post(f"{API_BASE_URL}/notes", json={"content": note_content})
                if res.status_code == 201:
                    st.success("Note saved!")
                    st.rerun()
            else:
                st.warning("Note cannot be empty.")
                
    st.divider()
    st.subheader("Saved Notes")
    notes = fetch_notes()
    for note in notes:
        st.info(f"{note['timestamp']} - {note['content']}")

elif page == "AI Assistant":
    st.title("AI Chat Assistant")
    st.write("Chat with your AI assistant about projects, tasks, and more.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            try:
                response = requests.post(f"{API_BASE_URL}/chat", json={"messages": st.session_state.messages})
                if response.status_code == 200:
                    ai_text = response.json().get("response", "I don't know.")
                    st.markdown(ai_text)
                    st.session_state.messages.append({"role": "assistant", "content": ai_text})
                else:
                    st.error("Error fetching AI response.")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
