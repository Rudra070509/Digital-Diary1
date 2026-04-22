import tkinter as tk
from storage import *

class DiaryApp(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.title(f"Diary - {user}")
        self.geometry("500x500")

        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="Digital Diary", font=("Arial", 18)).pack(pady=10)

        self.title_entry = tk.Entry(self, width=40)
        self.title_entry.pack()

        self.text = tk.Text(self, height=6)
        self.text.pack()

        self.mood = tk.StringVar(value="Happy")
        tk.OptionMenu(self, self.mood, "Happy", "Sad", "Angry").pack()

        tk.Button(self, text="Save", command=self.save).pack()
        tk.Button(self, text="View", command=self.view).pack()
        tk.Button(self, text="Search", command=self.search).pack()

    def save(self):
        add_entry(self.user,
                  self.title_entry.get(),
                  self.text.get("1.0", tk.END),
                  self.mood.get())

    def view(self):
        data = load_entries(self.user)
        win = tk.Toplevel(self)
        for i, e in enumerate(data):
            tk.Label(win, text=f"{i+1}. {e['title']}").pack()

    def search(self):
        key = self.title_entry.get()
        results = search_entries(self.user, key)
        win = tk.Toplevel(self)
        for e in results:
            tk.Label(win, text=e["title"]).pack()