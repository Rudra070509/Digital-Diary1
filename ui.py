from backend import *
from auth import AuthWindow
 
# ─────────────────────────── Main App ─────────────────────────────────────────
class DiaryApp(tk.Tk):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.title(f"📓 Digital Diary — {username}")
        self.config(bg=BG)
        self.minsize(900, 600)
        self._center(1060, 680)
        self._build_ui()
        self._show_panel("home")
 
    def _center(self, w, h):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
 
    # ── Layout ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=BG3, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
 
        tk.Label(self.sidebar, text="📓", bg=BG3, fg=AMBER,
                 font=("Georgia", 32)).pack(pady=(24,2))
        tk.Label(self.sidebar, text="DIGITAL DIARY", bg=BG3, fg=AMBER,
                 font=("Georgia", 11, "bold")).pack(pady=(0,4))
        tk.Label(self.sidebar, text=f"👤 {self.username}", bg=BG3, fg=TEXT_DIM,
                 font=FONT_SM).pack(pady=(0,16))
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=16)
 
        self._nav_btns = {}
        nav = [
            ("home",    "🏠  Home"),
            ("add",     "➕  New Entry"),
            ("view",    "📖  All Entries"),
            ("search",  "🔍  Search"),
            ("stats",   "📊  Statistics"),
            ("export",  "💾  Export"),
            ("passwd",  "🔐  Password"),
        ]
        for key, label_ in nav:
            b = tk.Button(self.sidebar, text=label_, bg=BG3, fg=TEXT,
                          relief="flat", anchor="w", font=FONT,
                          padx=20, pady=10, cursor="hand2",
                          activebackground=AMBER_DK, activeforeground=TEXT,
                          command=lambda k=key: self._show_panel(k))
            b.pack(fill="x")
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg=AMBER_DK))
            b.bind("<Leave>", lambda e, btn=b, k=key: btn.config(
                bg=AMBER if self._nav_btns.get(k) and self._nav_btns[k]["bg"] == AMBER else BG3))
            self._nav_btns[key] = b
 
        # Exit at bottom
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, side="bottom", pady=4)
        tk.Button(self.sidebar, text="🚪  Exit", bg=BG3, fg=TEXT_DIM,
                  relief="flat", anchor="w", font=FONT, padx=20, pady=8,
                  cursor="hand2", activebackground=RED, activeforeground=TEXT,
                  command=self._exit).pack(fill="x", side="bottom")
 
        # Main content
        self.content = tk.Frame(self, bg=BG2)
        self.content.pack(side="left", fill="both", expand=True)
 
    def _show_panel(self, key):
        for k, b in self._nav_btns.items():
            b.config(bg=AMBER if k == key else BG3,
                     fg=BG    if k == key else TEXT)
        for w in self.content.winfo_children():
            w.destroy()
        {
            "home":   self._panel_home,
            "add":    self._panel_add,
            "view":   self._panel_view,
            "search": self._panel_search,
            "stats":  self._panel_stats,
            "export": self._panel_export,
            "passwd": self._panel_passwd,
        }[key]()
 
    # ── Home ────────────────────────────────────────────────────────────────
    def _panel_home(self):
        fr = tk.Frame(self.content, bg=BG2, padx=40, pady=30)
        fr.pack(fill="both", expand=True)
 
        entries = load_user_entries(self.username)
 
        tk.Label(fr, text="Good " + self._time_greet(), bg=BG2, fg=TEXT_DIM, font=FONT).pack(anchor="w")
        tk.Label(fr, text="Your Diary", bg=BG2, fg=TEXT, font=("Georgia", 28, "bold")).pack(anchor="w")
        tk.Frame(fr, bg=AMBER, height=3, width=60).pack(anchor="w", pady=(4,20))
 
        # Stats row
        sf = tk.Frame(fr, bg=BG2)
        sf.pack(fill="x", pady=(0,24))
        for val, lbl in [(str(len(entries)), "Total\nEntries"),
                          (self._streak(), "Day\nStreak"),
                          (self._top_mood(entries), "Top\nMood")]:
            card = tk.Frame(sf, bg=BG3, padx=20, pady=16, relief="flat")
            card.pack(side="left", padx=(0,12))
            tk.Label(card, text=val, bg=BG3, fg=AMBER, font=("Georgia", 26, "bold")).pack()
            tk.Label(card, text=lbl, bg=BG3, fg=TEXT_DIM, font=FONT_SM).pack()
 
        # Recent entries
        tk.Label(fr, text="Recent Entries", bg=BG2, fg=TEXT, font=FONT_LG).pack(anchor="w", pady=(0,8))
        recent = entries[-5:][::-1]
        if not recent:
            tk.Label(fr, text="No entries yet — write your first one! ✨",
                     bg=BG2, fg=TEXT_DIM, font=FONT).pack(anchor="w")
        else:
            for e in recent:
                self._entry_card(fr, e)
 
    def _time_greet(self):
        h = datetime.now().hour
        return "Morning ☀️" if h < 12 else "Afternoon 🌤️" if h < 18 else "Evening 🌙"
 
    def _streak(self):
        entries = load_user_entries(self.username)
        if not entries:
            return "0"
        dates = sorted({e["created_at"][:10] for e in entries}, reverse=True)
        streak = 1
        for i in range(1, len(dates)):
            d1 = datetime.strptime(dates[i-1], "%Y-%m-%d")
            d2 = datetime.strptime(dates[i],   "%Y-%m-%d")
            if (d1 - d2).days == 1:
                streak += 1
            else:
                break
        return str(streak)
 
    def _top_mood(self, entries):
        if not entries:
            return "─"
        counts = {}
        for e in entries:
            counts[e["mood"]] = counts.get(e["mood"], 0) + 1
        best = max(counts, key=counts.get)
        return MOODS.get(best, "?") + " " + best
 
    def _entry_card(self, parent, e, show_full=False):
        card = tk.Frame(parent, bg=BG3, padx=14, pady=10, relief="flat",
                        cursor="hand2")
        card.pack(fill="x", pady=3)
        top = tk.Frame(card, bg=BG3)
        top.pack(fill="x")
        tk.Label(top, text=f"{e['mood_emoji']}  {e['title']}",
                 bg=BG3, fg=TEXT, font=FONT_LG, anchor="w").pack(side="left")
        tk.Label(top, text=e["created_at"][:10], bg=BG3, fg=TEXT_DIM,
                 font=FONT_SM).pack(side="right", padx=(0,4))
        if e["tags"]:
            tk.Label(card, text="🏷  " + ", ".join(e["tags"]),
                     bg=BG3, fg=AMBER_DK, font=FONT_SM, anchor="w").pack(fill="x")
        preview = e["content"][:120] + ("…" if len(e["content"]) > 120 else "")
        tk.Label(card, text=preview, bg=BG3, fg=TEXT_DIM, font=FONT_SM,
                 anchor="w", wraplength=700, justify="left").pack(fill="x", pady=(4,0))
        card.bind("<Button-1>", lambda ev, eid=e["id"]: self._view_detail(eid))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda ev, eid=e["id"]: self._view_detail(eid))
            for gc in child.winfo_children():
                gc.bind("<Button-1>", lambda ev, eid=e["id"]: self._view_detail(eid))
        # hover
        def on_enter(ev, c=card): _hover_card(c, True)
        def on_leave(ev, c=card): _hover_card(c, False)
        def _hover_card(c, h):
            col = "#382D25" if h else BG3
            c.config(bg=col)
            for ch in c.winfo_children():
                try:
                    ch.config(bg=col)
                except Exception:
                    pass
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
 
    # ── Add Entry ────────────────────────────────────────────────────────────
    def _panel_add(self, prefill=None):
        is_edit = prefill is not None
        fr = tk.Frame(self.content, bg=BG2, padx=40, pady=24)
        fr.pack(fill="both", expand=True)
 
        tk.Label(fr, text="✏️  Edit Entry" if is_edit else "➕  New Entry",
                 bg=BG2, fg=TEXT, font=FONT_H).pack(anchor="w")
        tk.Frame(fr, bg=AMBER, height=2, width=60).pack(anchor="w", pady=(2,16))
 
        # Title
        tk.Label(fr, text="Title", bg=BG2, fg=TEXT_DIM, font=FONT_SM, anchor="w").pack(fill="x")
        title_var = tk.StringVar(value=prefill["title"] if is_edit else "")
        title_e = styled_entry(fr, width=60)
        title_e.insert(0, title_var.get())
        title_e.pack(fill="x", ipady=5, pady=(2,10))
 
        # Content
        tk.Label(fr, text="Content", bg=BG2, fg=TEXT_DIM, font=FONT_SM, anchor="w").pack(fill="x")
        content_t = styled_text(fr, h=10, w=70)
        if is_edit:
            content_t.insert("1.0", prefill["content"])
        content_t.pack(fill="x", pady=(2,10))
 
        row = tk.Frame(fr, bg=BG2)
        row.pack(fill="x", pady=4)
 
        # Tags
        tl = tk.Frame(row, bg=BG2)
        tl.pack(side="left", fill="x", expand=True, padx=(0,12))
        tk.Label(tl, text="Tags (comma-separated)", bg=BG2, fg=TEXT_DIM, font=FONT_SM, anchor="w").pack(fill="x")
        tags_e = styled_entry(tl, width=30)
        if is_edit:
            tags_e.insert(0, ", ".join(prefill["tags"]))
        tags_e.pack(fill="x", ipady=5, pady=(2,0))
 
        # Mood
        ml = tk.Frame(row, bg=BG2)
        ml.pack(side="left")
        tk.Label(ml, text="Mood", bg=BG2, fg=TEXT_DIM, font=FONT_SM, anchor="w").pack(fill="x")
        mood_var = tk.StringVar(value=prefill["mood"] if is_edit else "Neutral")
        mood_opts = list(MOODS.keys())
        mood_menu = tk.OptionMenu(ml, mood_var, *mood_opts)
        mood_menu.config(bg=BG3, fg=TEXT, activebackground=AMBER_DK,
                         activeforeground=TEXT, relief="flat", font=FONT,
                         highlightthickness=0, width=10)
        mood_menu["menu"].config(bg=BG3, fg=TEXT, activebackground=AMBER,
                                  activeforeground=BG)
        mood_menu.pack(ipady=4, pady=(2,0))
 
        # Buttons
        btn_row = tk.Frame(fr, bg=BG2)
        btn_row.pack(fill="x", pady=16)
 
        def save():
            title = title_e.get().strip()
            content = content_t.get("1.0", "end").strip()
            if not title:
                messagebox.showwarning("Missing", "Title cannot be empty.", parent=self)
                return
            if not content:
                messagebox.showwarning("Missing", "Content cannot be empty.", parent=self)
                return
            raw_tags = tags_e.get().strip()
            tags = [t.strip().lower() for t in raw_tags.split(",") if t.strip()] if raw_tags else []
            mood_lbl = mood_var.get()
            mood_em  = MOODS.get(mood_lbl, "😐")
 
            entries = load_user_entries(self.username)
            if is_edit:
                for e in entries:
                    if e["id"] == prefill["id"]:
                        e.update({"title": title, "content": content, "tags": tags,
                                  "mood": mood_lbl, "mood_emoji": mood_em,
                                  "updated_at": get_ts()})
            else:
                entries.append({
                    "id": gen_id(entries), "title": title, "content": content,
                    "tags": tags, "mood": mood_lbl, "mood_emoji": mood_em,
                    "created_at": get_ts(), "updated_at": None
                })
            save_user_entries(self.username, entries)
            messagebox.showinfo("Saved", "Entry saved successfully! ✅", parent=self)
            self._show_panel("view")
 
        styled_btn(btn_row, "💾  Save Entry", save).pack(side="left", padx=(0,8))
        styled_btn(btn_row, "✖  Cancel", lambda: self._show_panel("view"),
                   fg=TEXT_DIM, bg=BG3).pack(side="left")
 
    # ── View All ─────────────────────────────────────────────────────────────
    def _panel_view(self):
        fr = tk.Frame(self.content, bg=BG2, padx=40, pady=24)
        fr.pack(fill="both", expand=True)
 
        header = tk.Frame(fr, bg=BG2)
        header.pack(fill="x")
        entries = load_user_entries(self.username)
        tk.Label(header, text=f"📖  All Entries  ({len(entries)})",
                 bg=BG2, fg=TEXT, font=FONT_H).pack(side="left", anchor="w")
        styled_btn(header, "➕  New", lambda: self._show_panel("add"), padx=10, pady=4).pack(side="right")
        tk.Frame(fr, bg=AMBER, height=2, width=60).pack(anchor="w", pady=(2,16))
 
        if not entries:
            tk.Label(fr, text="📭  No entries yet. Start writing!", bg=BG2,
                     fg=TEXT_DIM, font=FONT).pack(pady=40)
            return
 
        # Scrollable list
        canvas = tk.Canvas(fr, bg=BG2, highlightthickness=0)
        scroll = ttk.Scrollbar(fr, orient="vertical", command=canvas.yview)
        inner  = tk.Frame(canvas, bg=BG2)
 
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(
            -1*(e.delta//120), "units"))
 
        for e in reversed(entries):
            row = tk.Frame(inner, bg=BG3, padx=14, pady=10, cursor="hand2")
            row.pack(fill="x", pady=3)
            info = tk.Frame(row, bg=BG3)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=f"{e['mood_emoji']}  {e['title']}",
                     bg=BG3, fg=TEXT, font=FONT_LG, anchor="w").pack(anchor="w")
            meta = e["created_at"][:10]
            if e["tags"]:
                meta += "  🏷 " + ", ".join(e["tags"])
            tk.Label(info, text=meta, bg=BG3, fg=TEXT_DIM, font=FONT_SM, anchor="w").pack(anchor="w")
 
            acts = tk.Frame(row, bg=BG3)
            acts.pack(side="right", padx=4)
            styled_btn(acts, "👁", lambda eid=e["id"]: self._view_detail(eid),
                       padx=6, pady=2).pack(side="left", padx=2)
            styled_btn(acts, "✏️", lambda eid=e["id"]: self._edit_entry(eid),
                       padx=6, pady=2, bg=AMBER_DK).pack(side="left", padx=2)
            styled_btn(acts, "🗑", lambda eid=e["id"]: self._delete_entry(eid),
                       padx=6, pady=2, bg="#5C1A1A", fg=TEXT).pack(side="left", padx=2)
 
    # ── View Detail ───────────────────────────────────────────────────────────
    def _view_detail(self, entry_id):
        entries = load_user_entries(self.username)
        e = next((x for x in entries if x["id"] == entry_id), None)
        if not e:
            return
 
        win = tk.Toplevel(self)
        win.title(e["title"])
        win.config(bg=BG2)
        win.geometry("700x540")
        win.grab_set()
 
        fr = tk.Frame(win, bg=BG2, padx=30, pady=20)
        fr.pack(fill="both", expand=True)
 
        tk.Label(fr, text=f"{e['mood_emoji']}  {e['title']}",
                 bg=BG2, fg=TEXT, font=FONT_H, wraplength=620, anchor="w").pack(fill="x")
        tk.Frame(fr, bg=AMBER, height=2).pack(fill="x", pady=(4,12))
 
        meta = tk.Frame(fr, bg=BG2)
        meta.pack(fill="x", pady=(0,12))
        for k, v in [("Created", e["created_at"]),
                     ("Mood",    e["mood_emoji"] + " " + e["mood"]),
                     ("Tags",    ", ".join(e["tags"]) if e["tags"] else "—")]:
            r = tk.Frame(meta, bg=BG2)
            r.pack(fill="x", pady=1)
            tk.Label(r, text=k + ":", bg=BG2, fg=TEXT_DIM, font=FONT_SM, width=10, anchor="w").pack(side="left")
            tk.Label(r, text=v,       bg=BG2, fg=TEXT,     font=FONT_SM, anchor="w").pack(side="left")
 
        tk.Frame(fr, bg=BORDER, height=1).pack(fill="x", pady=6)
 
        txt = tk.Text(fr, bg=BG3, fg=TEXT, font=("Georgia", 12), relief="flat",
                      wrap="word", padx=10, pady=8,
                      highlightthickness=1, highlightbackground=BORDER)
        txt.insert("1.0", e["content"])
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True)
 
        btn_row = tk.Frame(fr, bg=BG2)
        btn_row.pack(fill="x", pady=12)
        styled_btn(btn_row, "✏️  Edit",
                   lambda: [win.destroy(), self._edit_entry(entry_id)]).pack(side="left", padx=(0,8))
        styled_btn(btn_row, "🗑  Delete",
                   lambda: [win.destroy(), self._delete_entry(entry_id)],
                   bg="#5C1A1A", fg=TEXT).pack(side="left", padx=(0,8))
        styled_btn(btn_row, "✖  Close", win.destroy,
                   bg=BG3, fg=TEXT_DIM).pack(side="left")
 
    def _edit_entry(self, entry_id):
        entries = load_user_entries(self.username)
        e = next((x for x in entries if x["id"] == entry_id), None)
        if e:
            self._panel_add(prefill=e)
 
    def _delete_entry(self, entry_id):
        entries = load_user_entries(self.username)
        e = next((x for x in entries if x["id"] == entry_id), None)
        if not e:
            return
        if messagebox.askyesno("Confirm Delete",
                               f"Delete '{e['title']}'? This cannot be undone.", parent=self):
            entries.remove(e)
            save_user_entries(self.username, entries)
            messagebox.showinfo("Deleted", "Entry deleted.", parent=self)
            self._show_panel("view")
 
    # ── Search ────────────────────────────────────────────────────────────────
    def _panel_search(self):
        fr = tk.Frame(self.content, bg=BG2, padx=40, pady=24)
        fr.pack(fill="both", expand=True)
 
        tk.Label(fr, text="🔍  Search Entries", bg=BG2, fg=TEXT, font=FONT_H).pack(anchor="w")
        tk.Frame(fr, bg=AMBER, height=2, width=60).pack(anchor="w", pady=(2,16))
 
        ctrl = tk.Frame(fr, bg=BG2)
        ctrl.pack(fill="x", pady=(0,12))
 
        tk.Label(ctrl, text="Search by:", bg=BG2, fg=TEXT_DIM, font=FONT_SM).pack(side="left")
        mode_var = tk.StringVar(value="Keyword")
        for m in ["Keyword", "Tag", "Mood", "Date"]:
            tk.Radiobutton(ctrl, text=m, variable=mode_var, value=m,
                           bg=BG2, fg=TEXT, selectcolor=BG3,
                           activebackground=BG2, font=FONT_SM).pack(side="left", padx=8)
 
        qrow = tk.Frame(fr, bg=BG2)
        qrow.pack(fill="x", pady=4)
        query_e = styled_entry(qrow, width=50)
        query_e.pack(side="left", ipady=5, padx=(0,8))
 
        results_fr = tk.Frame(fr, bg=BG2)
 
        def do_search():
            for w in results_fr.winfo_children():
                w.destroy()
            q = query_e.get().strip().lower()
            if not q:
                return
            entries = load_user_entries(self.username)
            mode = mode_var.get()
            if mode == "Keyword":
                res = [e for e in entries if q in e["title"].lower() or q in e["content"].lower()]
            elif mode == "Tag":
                res = [e for e in entries if q in e["tags"]]
            elif mode == "Mood":
                res = [e for e in entries if e["mood"].lower() == q]
            elif mode == "Date":
                res = [e for e in entries if e["created_at"].startswith(q)]
            else:
                res = []
 
            tk.Label(results_fr, text=f"{len(res)} result(s)", bg=BG2,
                     fg=AMBER, font=FONT_SM).pack(anchor="w", pady=(0,6))
            if not res:
                tk.Label(results_fr, text="No entries matched your search.",
                         bg=BG2, fg=TEXT_DIM, font=FONT).pack()
                return
            for e in res:
                self._entry_card(results_fr, e)
 
        styled_btn(qrow, "🔍  Search", do_search, padx=12).pack(side="left")
        query_e.bind("<Return>", lambda ev: do_search())
        results_fr.pack(fill="both", expand=True, pady=8)
 
    # ── Stats ─────────────────────────────────────────────────────────────────
    def _panel_stats(self):
        fr = tk.Frame(self.content, bg=BG2, padx=40, pady=24)
        fr.pack(fill="both", expand=True)
 
        tk.Label(fr, text="📊  Statistics", bg=BG2, fg=TEXT, font=FONT_H).pack(anchor="w")
        tk.Frame(fr, bg=AMBER, height=2, width=60).pack(anchor="w", pady=(2,16))
 
        entries = load_user_entries(self.username)
        if not entries:
            tk.Label(fr, text="No entries to analyse.", bg=BG2, fg=TEXT_DIM, font=FONT).pack()
            return
 
        # Cards row
        mood_counts: dict = {}
        for e in entries:
            k = e["mood"]
            mood_counts[k] = mood_counts.get(k, 0) + 1
        top_mood = max(mood_counts, key=mood_counts.get)
        longest  = max(entries, key=lambda e: len(e["content"]))
 
        cards = tk.Frame(fr, bg=BG2)
        cards.pack(fill="x", pady=(0,20))
        for val, lbl in [
            (str(len(entries)),          "Total Entries"),
            (MOODS[top_mood]+" "+top_mood, "Fav Mood"),
            (f"{len(longest['content'])} ch", "Longest Entry"),
        ]:
            c = tk.Frame(cards, bg=BG3, padx=22, pady=14)
            c.pack(side="left", padx=(0,12))
            tk.Label(c, text=val,  bg=BG3, fg=AMBER, font=("Georgia", 20, "bold")).pack()
            tk.Label(c, text=lbl,  bg=BG3, fg=TEXT_DIM, font=FONT_SM).pack()
 
        # Mood bar chart
        tk.Label(fr, text="Mood Distribution", bg=BG2, fg=TEXT, font=FONT_LG).pack(anchor="w", pady=(0,8))
        max_c = max(mood_counts.values())
        BAR_W = 340
        for mood, count in sorted(mood_counts.items(), key=lambda x: -x[1]):
            row = tk.Frame(fr, bg=BG2)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{MOODS[mood]} {mood:<10}", bg=BG2, fg=TEXT,
                     font=FONT, width=16, anchor="w").pack(side="left")
            bar_fr = tk.Frame(row, bg=BG3, width=BAR_W, height=18)
            bar_fr.pack(side="left", padx=6)
            bar_fr.pack_propagate(False)
            filled = int(BAR_W * count / max_c)
            tk.Frame(bar_fr, bg=AMBER, width=filled, height=18).place(x=0, y=0)
            tk.Label(row, text=str(count), bg=BG2, fg=TEXT_DIM, font=FONT_SM).pack(side="left")
 
        # Top tags
        all_tags: dict = {}
        for e in entries:
            for t in e["tags"]:
                all_tags[t] = all_tags.get(t, 0) + 1
        if all_tags:
            tk.Label(fr, text="Top Tags", bg=BG2, fg=TEXT,
                     font=FONT_LG).pack(anchor="w", pady=(16,6))
            tag_row = tk.Frame(fr, bg=BG2)
            tag_row.pack(anchor="w")
            for tag, cnt in sorted(all_tags.items(), key=lambda x: -x[1])[:8]:
                tk.Label(tag_row, text=f"#{tag}  {cnt}",
                         bg=AMBER_DK, fg=TEXT, font=FONT_SM,
                         padx=8, pady=4).pack(side="left", padx=4)
 
    # ── Export ────────────────────────────────────────────────────────────────
    def _panel_export(self):
        fr = tk.Frame(self.content, bg=BG2, padx=40, pady=24)
        fr.pack(fill="both", expand=True)
 
        tk.Label(fr, text="💾  Export Diary", bg=BG2, fg=TEXT, font=FONT_H).pack(anchor="w")
        tk.Frame(fr, bg=AMBER, height=2, width=60).pack(anchor="w", pady=(2,20))
 
        entries = load_user_entries(self.username)
        tk.Label(fr, text=f"{len(entries)} entries will be exported as a plain-text file.",
                 bg=BG2, fg=TEXT_DIM, font=FONT).pack(anchor="w", pady=(0,20))
 
        self._export_msg = tk.Label(fr, text="", bg=BG2, fg=GREEN, font=FONT)
 
        def do_export():
            if not entries:
                messagebox.showwarning("Empty", "No entries to export.", parent=self)
                return
            fn = f"diary_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(fn, "w", encoding="utf-8") as f:
                f.write("MY DIGITAL DIARY — EXPORT\n")
                f.write("=" * 50 + "\n\n")
                for e in entries:
                    f.write(f"[{e['id']}] {e['title']}\n")
                    f.write(f"Date  : {e['created_at']}\n")
                    f.write(f"Mood  : {e['mood_emoji']} {e['mood']}\n")
                    if e["tags"]:
                        f.write(f"Tags  : {', '.join(e['tags'])}\n")
                    f.write("\n" + e["content"] + "\n")
                    f.write("-" * 50 + "\n\n")
            self._export_msg.config(text=f"✅  Exported to '{fn}'")
 
        styled_btn(fr, "💾  Export to .txt", do_export).pack(anchor="w")
        self._export_msg.pack(anchor="w", pady=10)
 
    # ── Password ──────────────────────────────────────────────────────────────
    def _panel_passwd(self):
        fr = tk.Frame(self.content, bg=BG2, padx=40, pady=24)
        fr.pack(fill="both", expand=True)
 
        tk.Label(fr, text="🔐  Change Password", bg=BG2, fg=TEXT, font=FONT_H).pack(anchor="w")
        tk.Frame(fr, bg=AMBER, height=2, width=60).pack(anchor="w", pady=(2,20))
 
        fields = {}
        for lbl, key in [("Current Password", "old"),
                          ("New Password",     "new"),
                          ("Confirm New",      "new2")]:
            tk.Label(fr, text=lbl, bg=BG2, fg=TEXT_DIM, font=FONT_SM, anchor="w").pack(fill="x")
            e = styled_entry(fr, width=36, show="●")
            e.pack(ipady=5, pady=(2,10))
            fields[key] = e
 
        msg = tk.Label(fr, text="", bg=BG2, fg=RED, font=FONT)
        msg.pack(anchor="w")
 
        def change():
            cfg = load_config()
            if hash_password(fields["old"].get()) != cfg.get("password_hash", ""):
                msg.config(text="❌  Current password is wrong.", fg=RED)
                return
            p1, p2 = fields["new"].get(), fields["new2"].get()
            if not p1:
                msg.config(text="❌  New password cannot be empty.", fg=RED)
                return
            if p1 != p2:
                msg.config(text="❌  Passwords do not match.", fg=RED)
                return
            cfg["password_hash"] = hash_password(p1)
            save_config(cfg)
            msg.config(text="✅  Password updated successfully!", fg=GREEN)
            for e in fields.values():
                e.delete(0, "end")
 
        styled_btn(fr, "🔐  Update Password", change).pack(anchor="w", pady=8)
 
    # ── Exit ──────────────────────────────────────────────────────────────────
    def _exit(self):
        if messagebox.askyesno("Exit", "Close your diary?", parent=self):
            self.destroy()
 
 
# ─────────────────────────── Entry point ──────────────────────────────────────
if __name__ == "__main__":
    # TTK style tweak for scrollbar
    style_root = tk.Tk()
    style_root.withdraw()
    s = ttk.Style(style_root)
    s.theme_use("clam")
    s.configure("Vertical.TScrollbar",
                 background=BG3, troughcolor=BG, arrowcolor=TEXT_DIM,
                 bordercolor=BG, darkcolor=BG3, lightcolor=BG3)
    style_root.destroy()
 
    auth = AuthWindow()
    auth.mainloop()
    if not auth._authenticated:
        sys.exit(0)
 
    app = DiaryApp(
        
auth.logged_in_user)
    app.mainloop()
