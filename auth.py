import tkinter as tk
from tkinter import messagebox
import json, os, hashlib
from datetime import datetime

USERS_FILE = "users.json"

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def get_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


class AuthWindow(tk.Tk):
    def _init_(self):
        super()._init_()
        self.title("Login")
        self.geometry("350x300")

        self._authenticated = False
        self.logged_in_user = None

        self.build_login()

    def build_login(self):
        for w in self.winfo_children():
            w.destroy()

        tk.Label(self, text="Username").pack()
        self.user = tk.Entry(self)
        self.user.pack()

        tk.Label(self, text="Password").pack()
        self.pwd = tk.Entry(self, show="*")
        self.pwd.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=5)
        tk.Button(self, text="Register", command=self.build_register).pack()

    def build_register(self):
        for w in self.winfo_children():
            w.destroy()

        tk.Label(self, text="New Username").pack()
        self.new_user = tk.Entry(self)
        self.new_user.pack()

        tk.Label(self, text="Password").pack()
        self.new_pwd = tk.Entry(self, show="*")
        self.new_pwd.pack()

        tk.Button(self, text="Create", command=self.register).pack()

    def register(self):
        users = load_users()
        u = self.new_user.get()
        p = self.new_pwd.get()

        if u in users:
            messagebox.showerror("Error", "User exists")
            return

        users[u] = {"password": hash_password(p), "created": get_ts()}
        save_users(users)
        messagebox.showinfo("Done", "Account created")
        self.build_login()

    def login(self):
        users = load_users()
        u = self.user.get()
        p = self.pwd.get()

        if u in users and users[u]["password"] == hash_password(p):
            self._authenticated = True
            self.logged_in_user = u
            self.destroy()
        else:
            messagebox.showerror("Error", "Wrong credentials")