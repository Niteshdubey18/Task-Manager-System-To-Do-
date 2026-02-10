import os
import io
import customtkinter as ctk
from PIL import Image
from tkinter import ttk, messagebox

# -----------------------------
# App Theme Settings
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# -----------------------------
# Create Main Window
# -----------------------------
app = ctk.CTk()
app.title("Task Management System")
app.geometry("1000x600")

# --- 3-part layout: Header / Main / Footer ---
app.grid_rowconfigure(0, weight=0)  # header (fixed)
app.grid_rowconfigure(1, weight=1)  # main (expands)
app.grid_rowconfigure(2, weight=0)  # footer (fixed)
app.grid_columnconfigure(0, weight=1)

# -----------------------------
# Header
# -----------------------------
header = ctk.CTkFrame(app, height=60, corner_radius=0)
header.grid(row=0, column=0, sticky="nsew")
header.grid_propagate(False)

# ✅ LOGO + TITLE
LOGO_PATH = os.path.join("assets", "Logo.png")
if not os.path.exists(LOGO_PATH):
    raise FileNotFoundError(f"Logo not found: {LOGO_PATH}")

logo_pil = Image.open(LOGO_PATH)
logo_ctk = ctk.CTkImage(light_image=logo_pil, dark_image=logo_pil, size=(50, 50))

header.grid_columnconfigure(0, weight=0)
header.grid_columnconfigure(1, weight=1)

logo_label = ctk.CTkLabel(header, text="", image=logo_ctk)
logo_label.grid(row=0, column=0, padx=15, pady=5, sticky="w")
logo_label.image = logo_ctk  # keep reference

title_label = ctk.CTkLabel(header, text="Task Management System", font=("Times New Roman", 30, "bold"))
title_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

# -----------------------------
# Main (background + overlay controls)
# -----------------------------
main = ctk.CTkFrame(app, corner_radius=0)
main.grid(row=1, column=0, sticky="nsew")

# Background Image Path
BG_PATH = os.path.join("assets", "Background.jpg")
if not os.path.exists(BG_PATH):
    raise FileNotFoundError(f"Background image not found: {BG_PATH}")

original = Image.open(BG_PATH)

# Background Label (Image Holder)
bg_label = ctk.CTkLabel(main, text="")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Fill entire frame

# -----------------------------
# Controls (overlay ON the background image)
# -----------------------------
controls = ctk.CTkFrame(
    master=bg_label,
    fg_color="transparent",
    corner_radius=10
)
controls.place(relx=0.5, rely=0.05, anchor="n")
controls.lift()

# -----------------------------
# Simple "Task List" Label (initially hidden)
# -----------------------------
task_title_wrapper = ctk.CTkFrame(
    master=bg_label,
    fg_color="transparent",
)
task_title = ctk.CTkLabel(
    master=task_title_wrapper,
    text="Task List",
    font=ctk.CTkFont("Times New Roman", 26, "bold"),
    fg_color="transparent",
)
task_title.pack(padx=10, pady=10)

# -----------------------------
# Real Table (Treeview) container
# -----------------------------
table_container = ctk.CTkFrame(
    master=bg_label,
    fg_color=("white", "gray17"),
    corner_radius=10
)
table_container.grid_rowconfigure(0, weight=1)
table_container.grid_columnconfigure(0, weight=1)

# ttk.Style for a clean table look
style = ttk.Style()
style.theme_use("clam")

# Colors
BG_DARK = "#222426"
ROW_ODD = "#2B2D30"
ROW_EVEN = "#232527"
FG_TEXT = "#F1F1F1"
HDR_BG = "#3A3D41"
HDR_FG = "#FFFFFF"
SEL_BG = "#0A84FF"
SEL_FG = "#FFFFFF"

style.configure(
    "Treeview",
    background=BG_DARK,
    fieldbackground=BG_DARK,
    foreground=FG_TEXT,
    rowheight=40,
    borderwidth=0
)
style.configure(
    "Treeview.Heading",
    background=HDR_BG,
    foreground=HDR_FG,
    relief="flat",
    font=("Segoe UI", 15, "bold")
)
style.map(
    "Treeview",
    background=[("selected", SEL_BG)],
    foreground=[("selected", SEL_FG)]
)

# Create Treeview
columns = ("serial", "task", "status", "action")
tree = ttk.Treeview(
    table_container,
    columns=columns,
    show="headings",
    selectmode="browse",
    height=1,  # visible rows are controlled dynamically
)

# Define headings
tree.heading("serial", text="Serial No.")
tree.heading("task",   text="Task Name")
tree.heading("status", text="Status")
tree.heading("action", text="Action")

# Define columns (widths & alignment)
tree.column("serial", width=100, anchor="w", stretch=False)
tree.column("task",   width=520, anchor="w", stretch=True)
tree.column("status", width=140, anchor="w", stretch=False)
tree.column("action", width=220, anchor="center", stretch=False)  # wider for two "buttons"

# Scrollbars
vsb = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
hsb = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

# Layout in grid
tree.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")
hsb.grid(row=1, column=0, sticky="ew")

# Striped rows
tree.tag_configure("oddrow",  background=ROW_ODD)
tree.tag_configure("evenrow", background=ROW_EVEN)

# -----------------------------
# Data + Persistence
# -----------------------------
FILE_PATH = "tasks.txt"  # TSV: uid \t task_name \t status

# TASKS: list of dicts: {'uid': int, 'task': str, 'status': 'Pending'|'Completed'}
TASKS = []
NEXT_UID = 1  # will be set after loading file
TREE_IID_TO_UID = {}  # maps Treeview item iid -> uid for click actions

def load_tasks_from_file():
    """Load tasks from FILE_PATH if exists."""
    global TASKS, NEXT_UID
    TASKS.clear()
    max_uid = 0
    if os.path.exists(FILE_PATH):
        with io.open(FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                try:
                    uid = int(parts[0])
                except ValueError:
                    continue
                task_name = parts[1]
                status = parts[2] if parts[2] in ("Pending", "Completed") else "Pending"
                TASKS.append({"uid": uid, "task": task_name, "status": status})
                if uid > max_uid:
                    max_uid = uid
    NEXT_UID = (max_uid + 1) if max_uid > 0 else 1

def save_tasks_to_file():
    """Persist TASKS to FILE_PATH."""
    with io.open(FILE_PATH, "w", encoding="utf-8") as f:
        for t in TASKS:
            f.write(f"{t['uid']}\t{t['task']}\t{t['status']}\n")

def get_task_index_by_uid(uid: int):
    for i, t in enumerate(TASKS):
        if t["uid"] == uid:
            return i
    return None

# -----------------------------
# Helpers for table visibility & sizing
# -----------------------------
MAX_VISIBLE_ROWS = 10  # table grows until this many visible rows; scrolls after

def show_table():
    if not task_title_wrapper.winfo_ismapped():
        task_title_wrapper.place(relx=0.5, rely=0.16, anchor="n")
    if not table_container.winfo_ismapped():
        # no relheight => frame height follows Treeview's requested height (rows * rowheight)
        table_container.place(relx=0.5, rely=0.30, anchor="n", relwidth=0.94)
    controls.lift()
    task_title_wrapper.lift()
    table_container.lift()

def hide_table():
    if task_title_wrapper.winfo_ismapped():
        task_title_wrapper.place_forget()
    if table_container.winfo_ismapped():
        table_container.place_forget()

def update_tree_height(n_rows: int):
    visible = min(n_rows, MAX_VISIBLE_ROWS)
    tree.configure(height=visible if visible > 0 else 1)

def refresh_table(data_rows):
    """
    Rebuild the table with data_rows: list of dicts {'uid','task','status'}
    """
    # Clear old rows
    for iid in tree.get_children():
        tree.delete(iid)
    TREE_IID_TO_UID.clear()

    # Insert new rows with stripes
    for idx, item in enumerate(data_rows, start=1):
        # Two "buttons" displayed as text; we detect clicks by x-position.
        action_text = "Completed    Delete"
        values = (idx, item["task"], item["status"], action_text)
        tag = "evenrow" if idx % 2 == 0 else "oddrow"
        iid = tree.insert("", "end", values=values, tags=(tag,))
        TREE_IID_TO_UID[iid] = item["uid"]

    # Show/hide + adjust height
    if len(data_rows) == 0:
        hide_table()
    else:
        show_table()
        update_tree_height(len(data_rows))

def current_filtered_rows():
    """Return list of dicts filtered by dropdown value."""
    flt = filter_dropdown.get()
    if flt == "All Task":
        return list(TASKS)
    else:
        return [t for t in TASKS if t["status"] == flt]

def apply_current_filter():
    refresh_table(current_filtered_rows())

# -----------------------------
# Actions: Complete / Delete
# -----------------------------
def mark_completed(uid: int):
    idx = get_task_index_by_uid(uid)
    if idx is None:
        return
    if TASKS[idx]["status"] == "Completed":
        # Already completed; no toggle back
        return
    TASKS[idx]["status"] = "Completed"
    save_tasks_to_file()
    apply_current_filter()

def delete_task(uid: int):
    idx = get_task_index_by_uid(uid)
    if idx is None:
        return
    del TASKS[idx]
    save_tasks_to_file()
    apply_current_filter()

def on_tree_click(event):
    """
    Detect clicks in the Action column and decide whether 'Completed' or 'Delete' was clicked.
    We split the Action cell into left/right halves.
    """
    region = tree.identify("region", event.x, event.y)
    if region != "cell":
        return
    col = tree.identify_column(event.x)  # '#1', '#2', '#3', '#4'...
    if col != "#4":  # 'action' column
        return
    row_iid = tree.identify_row(event.y)
    if not row_iid:
        return

    # Get the cell bbox (x, y, width, height) in tree coordinates
    try:
        x1, y1, w, h = tree.bbox(row_iid, column=col)
    except Exception:
        return
    if w <= 0:
        return

    # Decide which half was clicked
    left_half_end = x1 + (w // 2)
    uid = TREE_IID_TO_UID.get(row_iid)
    if uid is None:
        return

    if event.x <= left_half_end:
        # Left half: "Completed"
        mark_completed(uid)
    else:
        # Right half: "Delete"
        delete_task(uid)

# Bind mouse click to tree
tree.bind("<Button-1>", on_tree_click)

# -----------------------------
# Add Task Dialog
# -----------------------------
def center_window(win, parent):
    parent.update_idletasks()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    ww = 420
    wh = 180
    x = px + (pw - ww) // 2
    y = py + (ph - wh) // 2
    win.geometry(f"{ww}x{wh}+{x}+{y}")

def open_add_task_dialog():
    dlg = ctk.CTkToplevel(app)
    dlg.title("Add New Task")
    dlg.resizable(False, False)
    center_window(dlg, app)
    dlg.transient(app)
    dlg.grab_set()

    # Layout
    frm = ctk.CTkFrame(dlg, corner_radius=10)
    frm.pack(fill="both", expand=True, padx=16, pady=16)
    frm.grid_columnconfigure(1, weight=1)

    lbl = ctk.CTkLabel(frm, text="Task Name:")
    lbl.grid(row=0, column=0, padx=8, pady=8, sticky="e")

    entry = ctk.CTkEntry(frm, placeholder_text="Enter task name")
    entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
    entry.focus_set()

    btns = ctk.CTkFrame(frm, fg_color="transparent")
    btns.grid(row=1, column=0, columnspan=2, pady=(12, 0))

    def on_submit():
        name = entry.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Task name cannot be empty.")
            return
        add_task(name)  # default status 'Pending'
        dlg.destroy()

    def on_cancel():
        dlg.destroy()

    # Keyboard submit (Enter)
    entry.bind("<Return>", lambda e: on_submit())

    submit_btn = ctk.CTkButton(btns, text="Submit", width=120, command=on_submit)
    cancel_btn = ctk.CTkButton(btns, text="Cancel", width=120, fg_color="#555555", hover_color="#444444",
                               command=on_cancel)
    submit_btn.grid(row=0, column=0, padx=6)
    cancel_btn.grid(row=0, column=1, padx=6)

def add_task(task_name: str):
    global NEXT_UID
    new_task = {"uid": NEXT_UID, "task": task_name, "status": "Pending"}
    NEXT_UID += 1
    TASKS.append(new_task)
    save_tasks_to_file()
    apply_current_filter()

# -----------------------------
# Top Controls (Buttons & Filter)
# -----------------------------
btn_add = ctk.CTkButton(controls, text="Add New Task", command=open_add_task_dialog, width=170)
btn_add.grid(row=0, column=0, padx=5, pady=5)

def remove_all_task():
    if not TASKS:
        return
    if messagebox.askyesno("Confirm", "Remove ALL tasks? This cannot be undone."):
        TASKS.clear()
        save_tasks_to_file()
        apply_current_filter()  # table clears and hides

btn_remove = ctk.CTkButton(controls, text="Remove All Task", command=remove_all_task, width=170)
btn_remove.grid(row=0, column=1, padx=5, pady=5)

def filter_changed(value):
    apply_current_filter()

filter_dropdown = ctk.CTkOptionMenu(
    controls,
    values=["All Task", "Pending", "Completed"],  # filter by All or status
    command=filter_changed,
    width=170
)
filter_dropdown.set("All Task")
filter_dropdown.grid(row=0, column=2, padx=5, pady=5)

# -----------------------------
# Resize Function (Runs on Window Resize)
# -----------------------------
def resize(event):
    nonlocal_vars = resize.__dict__
    w, h = max(event.width, 1), max(event.height, 1)
    if nonlocal_vars.get("last") == (w, h):
        return
    nonlocal_vars["last"] = (w, h)

    img = ctk.CTkImage(light_image=original, dark_image=original, size=(w, h))
    bg_label.configure(image=img)
    bg_label.image = img

    # keep overlays above the image (only if visible)
    controls.lift()
    if task_title_wrapper.winfo_ismapped():
        task_title_wrapper.lift()
    if table_container.winfo_ismapped():
        table_container.lift()

# Bind resize to 'main' container (resizes with grid area changes)
main.bind("<Configure>", resize)

# -----------------------------
# Initial Data Load & Render
# -----------------------------
load_tasks_from_file()
apply_current_filter()  # this will show/hide table based on data

# -----------------------------
# Footer
# -----------------------------
footer = ctk.CTkFrame(app, height=30, corner_radius=0)
footer.grid(row=2, column=0, sticky="nsew")
footer.grid_propagate(False)

footer.columnconfigure(0, weight=1)
footer.rowconfigure(0, weight=1)

footer_label = ctk.CTkLabel(footer, text="© 2026 Task Management System. All rights reserved.", font=("Arial", 10))
footer_label.grid(row=0, column=0)

# -----------------------------
# Run Application Loop
# -----------------------------
app.mainloop()