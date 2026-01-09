import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
import psutil
import keyboard
import win32gui
import win32process
import win32api
import win32con

CONFIG_FILE = "SmileyConf.json"
HOTKEY = "num 3"
SELF_PID = os.getpid()

# ================= CONFIG =================

default_config = {
    "whitelist_enabled": True,
    "whitelist_exe": ["RobloxPlayerBeta.exe", "javaw.exe"],
    "scan_enabled": True,
    "scan_interval": 5,
    "toggle_mode": False,
    "timeout_enabled": False,
    "timeout_seconds": 5,
    "thread_mode": False,
    "thread_targets": {}  # exe -> [thread_ids]
}

config = default_config.copy()
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config.update(json.load(f))
    except:
        pass

def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

# ================= PROCESS HELPERS =================

def get_foreground_pid():
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return None if pid == SELF_PID else pid

def get_gui_processes():
    result = {}
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                exe = os.path.basename(psutil.Process(pid).exe())
                result[exe] = pid
            except:
                pass
        return True
    win32gui.EnumWindows(cb, None)
    return result

# ================= THREAD CONTROL =================

suspended = set()

def suspend(pid, threads=None):
    try:
        p = psutil.Process(pid)
        for t in p.threads():
            if threads and t.id not in threads:
                continue
            h = win32api.OpenThread(win32con.THREAD_SUSPEND_RESUME, False, t.id)
            win32process.SuspendThread(h)
            win32api.CloseHandle(h)
        suspended.add(pid)
    except:
        pass

def resume(pid):
    try:
        p = psutil.Process(pid)
        for t in p.threads():
            h = win32api.OpenThread(win32con.THREAD_SUSPEND_RESUME, False, t.id)
            win32process.ResumeThread(h)
            win32api.CloseHandle(h)
        suspended.discard(pid)
    except:
        pass

# ================= WHITELIST SCAN =================

active_whitelist = set()

def whitelist_scanner():
    while True:
        if config["scan_enabled"] and config["whitelist_enabled"]:
            active_whitelist.clear()
            gui = get_gui_processes()
            for exe in config["whitelist_exe"]:
                if exe in gui:
                    active_whitelist.add(gui[exe])
        time.sleep(config["scan_interval"])

# ================= FREEZE =================

freeze_active = False
freeze_start = 0

def apply_freeze(state):
    global freeze_active, freeze_start
    freeze_active = state
    if state:
        freeze_start = time.time()

    targets = set(active_whitelist)
    fg = get_foreground_pid()
    if fg:
        targets.add(fg)

    targets.discard(SELF_PID)

    for pid in targets:
        if state:
            if config["thread_mode"]:
                exe = os.path.basename(psutil.Process(pid).exe())
                threads = config["thread_targets"].get(exe)
                suspend(pid, threads)
            else:
                suspend(pid)
        else:
            resume(pid)

# ================= HOTKEY =================

def hotkey_worker():
    last = False
    while True:
        pressed = keyboard.is_pressed(HOTKEY)
        if config["toggle_mode"]:
            if pressed and not last:
                apply_freeze(not freeze_active)
        else:
            if pressed and not freeze_active:
                apply_freeze(True)
            elif not pressed and freeze_active:
                apply_freeze(False)

            if (
                freeze_active
                and config["timeout_enabled"]
                and pressed
                and time.time() - freeze_start >= config["timeout_seconds"]
            ):
                apply_freeze(False)
                time.sleep(0.05)
                apply_freeze(True)

        last = pressed
        time.sleep(0.02)

# ================= GUI =================

root = tk.Tk()
root.title("Smiley Freeze Macro")
root.geometry("750x400")
root.resizable(False, False)

# --- Layout frames
left = ttk.LabelFrame(root, text="Freeze Settings")
left.place(x=10, y=10, width=260, height=360)

mid = ttk.LabelFrame(root, text="Advanced")
mid.place(x=280, y=10, width=220, height=360)

right = ttk.LabelFrame(root, text="Whitelist")
right.place(x=510, y=10, width=230, height=360)

# --- Vars
toggle_var = tk.BooleanVar(value=config["toggle_mode"])
timeout_var = tk.BooleanVar(value=config["timeout_enabled"])
thread_var = tk.BooleanVar(value=config["thread_mode"])

# --- Left
ttk.Checkbutton(left, text="Toggle Mode", variable=toggle_var).pack(anchor="w")
ttk.Checkbutton(left, text="Timeout (Hold)", variable=timeout_var).pack(anchor="w")

ttk.Label(left, text="Timeout Seconds").pack(anchor="w")
timeout_entry = ttk.Entry(left, width=6)
timeout_entry.insert(0, str(config["timeout_seconds"]))
timeout_entry.pack(anchor="w")

ttk.Label(left, text="Hotkey: NUMPAD 3", foreground="gray").pack(anchor="w", pady=10)

# --- Advanced (Thread)
ttk.Checkbutton(
    mid,
    text="Thread Mode (ADVANCED)",
    variable=thread_var
).pack(anchor="w")

ttk.Label(
    mid,
    text="⚠ Default: all threads suspended\nRecommended for stability",
    foreground="orange"
).pack(anchor="w", pady=5)

ttk.Label(
    mid,
    text="Typical game threads:\n• Main Game Loop\n• Physics / Simulation\n• Network / Packet",
    foreground="gray"
).pack(anchor="w")

def select_threads():
    gui = get_gui_processes()
    win = tk.Toplevel(root)
    win.title("Select Application Threads")
    win.geometry("400x350")

    lb = tk.Listbox(win)
    lb.pack(fill="both", expand=True)

    exe_list = list(gui.keys())
    for e in exe_list:
        lb.insert(tk.END, e)

    def open_threads():
        sel = lb.curselection()
        if not sel:
            return
        exe = exe_list[sel[0]]
        pid = gui[exe]
        t_win = tk.Toplevel(win)
        t_win.title(f"Threads - {exe}")
        t_win.geometry("350x300")

        clb = tk.Listbox(t_win, selectmode="multiple")
        clb.pack(fill="both", expand=True)

        threads = psutil.Process(pid).threads()
        for t in threads:
            clb.insert(tk.END, f"Thread ID: {t.id}")

        def save_threads():
            sel_ids = [threads[i].id for i in clb.curselection()]
            config["thread_targets"][exe] = sel_ids
            save_config()
            t_win.destroy()

        ttk.Button(t_win, text="Save Threads", command=save_threads).pack()

    ttk.Button(win, text="Select", command=open_threads).pack()

ttk.Button(mid, text="Select Threads", command=select_threads).pack(pady=10)

# --- Whitelist
lb = tk.Listbox(right)
lb.pack(fill="both", expand=True)

def refresh_whitelist():
    lb.delete(0, tk.END)
    for exe in config["whitelist_exe"]:
        lb.insert(tk.END, exe)

def add_app():
    gui = get_gui_processes()
    win = tk.Toplevel(root)
    win.title("Add App")
    win.geometry("300x300")
    l = tk.Listbox(win)
    l.pack(fill="both", expand=True)
    exes = list(gui.keys())
    for e in exes:
        l.insert(tk.END, e)

    def add():
        sel = l.curselection()
        if sel:
            exe = exes[sel[0]]
            if exe not in config["whitelist_exe"]:
                config["whitelist_exe"].append(exe)
                save_config()
                refresh_whitelist()
        win.destroy()

    ttk.Button(win, text="Add", command=add).pack()

ttk.Button(right, text="Add Running App", command=add_app).pack(fill="x")

# --- Apply
def apply():
    config["toggle_mode"] = toggle_var.get()
    config["timeout_enabled"] = timeout_var.get()
    config["thread_mode"] = thread_var.get()
    try:
        config["timeout_seconds"] = float(timeout_entry.get())
    except:
        pass
    save_config()

ttk.Button(left, text="Apply", command=apply).pack(side="bottom", fill="x")

refresh_whitelist()

threading.Thread(target=whitelist_scanner, daemon=True).start()
threading.Thread(target=hotkey_worker, daemon=True).start()

root.mainloop()
