from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection, init_db
from mock_ai import summarize_meeting, generate_chat_response

app = Flask(__name__)
CORS(app) # Allow frontend to communicate with backend

# Initialize database
init_db()

# --- MEETINGS ---
@app.route('/api/meetings/process', methods=['POST'])
def process_meeting():
    data = request.json
    transcript = data.get('transcript', '')
    
    if not transcript:
        return jsonify({"error": "Transcript is required"}), 400
        
    summary, tasks = summarize_meeting(transcript)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Save meeting
    cursor.execute('INSERT INTO meetings (transcript, summary) VALUES (?, ?)', (transcript, summary))
    
    # Save extracted tasks
    for task in tasks:
        cursor.execute(
            'INSERT INTO tasks (title, owner, deadline, priority) VALUES (?, ?, ?, ?)',
            (task['title'], task['owner'], task['deadline'], task['priority'])
        )
        
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": "Meeting processed successfully",
        "summary": summary,
        "extracted_tasks": tasks
    })

# --- TASKS ---
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks ORDER BY priority, deadline')
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    title = data.get('title')
    owner = data.get('owner', '')
    deadline = data.get('deadline', '')
    priority = data.get('priority', 'Medium')
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title, owner, deadline, priority) VALUES (?, ?, ?, ?)',
        (title, owner, deadline, priority)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Task added successfully"}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    status = data.get('status')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (status, task_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task updated successfully"})

# --- NOTES ---
@app.route('/api/notes', methods=['GET'])
def get_notes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notes ORDER BY timestamp DESC')
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(notes)

@app.route('/api/notes', methods=['POST'])
def add_note():
    data = request.json
    content = data.get('content')
    
    if not content:
        return jsonify({"error": "Content is required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notes (content) VALUES (?)', (content,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Note added successfully"}), 201

# --- CHAT ---
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    
    response_text = generate_chat_response(messages)
    
    return jsonify({"response": response_text})

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
