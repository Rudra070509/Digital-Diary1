import json, os
from datetime import datetime

def get_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_file(user):
    return f"diary_{user}.json"

def load_entries(user):
    file = get_file(user)
    if os.path.exists(file):
        with open(file) as f:
            return json.load(f)
    return []

def save_entries(user, data):
    with open(get_file(user), "w") as f:
        json.dump(data, f, indent=2)

def add_entry(user, title, content, mood):
    data = load_entries(user)
    data.append({
        "id": len(data)+1,
        "title": title,
        "content": content,
        "mood": mood,
        "date": get_ts()
    })
    save_entries(user, data)

def delete_entry(user, index):
    data = load_entries(user)
    if 0 <= index < len(data):
        data.pop(index)
        save_entries(user, data)

def search_entries(user, keyword):
    data = load_entries(user)
    return [e for e in data if keyword.lower() in e["title"].lower()]