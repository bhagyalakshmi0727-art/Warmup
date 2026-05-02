import random
from datetime import datetime, timedelta

def summarize_meeting(transcript):
    """
    Mock function to simulate AI summarizing a meeting and extracting tasks.
    """
    # Simply ignore the transcript and return mock data for now
    summary = "The team discussed the upcoming hackathon deliverables. Key action items include finalizing the database schema, setting up the backend API, and designing the frontend layout."
    
    # Mock extracted tasks
    mock_tasks = [
        {
            "title": "Finalize DB Schema",
            "owner": "Alice",
            "deadline": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "priority": "High"
        },
        {
            "title": "Setup API endpoints",
            "owner": "Bob",
            "deadline": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "priority": "High"
        },
        {
            "title": "Design frontend layout",
            "owner": "Charlie",
            "deadline": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "priority": "Medium"
        }
    ]
    
    return summary, mock_tasks

def generate_chat_response(messages):
    """
    Mock function to simulate an AI chat assistant.
    messages is a list of dicts like [{"role": "user", "content": "Hello"}]
    """
    last_user_message = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), "")
    
    responses = [
        "That's an interesting point. Let me check the project status for you.",
        "Based on your tasks, I recommend focusing on the High priority items first.",
        "I can help you draft an email to the team regarding this if you want.",
        "Could you provide more details about that issue?",
        "I've made a note of it. Let's make sure it's discussed in the next meeting."
    ]
    
    if "hello" in last_user_message.lower() or "hi" in last_user_message.lower():
        return "Hello! How can I help you and your team today?"
    if "task" in last_user_message.lower():
        return "You have some pending tasks. You can view them in the Tasks dashboard."
    
    return random.choice(responses)
