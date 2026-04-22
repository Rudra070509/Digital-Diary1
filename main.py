from auth import AuthWindow
from ui import DiaryApp

auth = AuthWindow()
auth.mainloop()

if auth._authenticated:
    app = DiaryApp(auth.logged_in_user)
    app.mainloop()