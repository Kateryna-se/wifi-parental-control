# wifi_control.py

import tkinter as tk
from tkinter import messagebox
import datetime
import os

# --------------------------
# 📁 Конфигурация и данные
# --------------------------

# Словарь: лимиты на день (в минутах)
DEVICE_LIMITS = {
    "iPhone_Anna": 120,
    "Laptop_Katya": 180,
    "Tablet_Kids": 90
}

# Файлы для хранения данных
USAGE_FILE = "usage_data.txt"
RESET_TRACKER_FILE = "last_reset.txt"
LOG_FILE = "attempt_log.txt"

# Состояние авторизации
logged_in = False

# Словарь с текущим временем использования
usage_data = {}

# --------------------------
# 📂 Загрузка и сохранение
# --------------------------

def load_usage_data():
    """Читает использование из файла или создаёт новый."""
    global usage_data
    usage_data = {device: 0 for device in DEVICE_LIMITS}
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    device, minutes = line.strip().split(":")
                    usage_data[device] = int(minutes)
                except:
                    continue
    save_usage_data()

def save_usage_data():
    """Сохраняет текущее использование в файл."""
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        for device, minutes in usage_data.items():
            f.write(f"{device}:{minutes}\n")

def reset_usage_if_new_day():
    """Обнуляет использование, если наступил новый день."""
    today = datetime.date.today().isoformat()
    if os.path.exists(RESET_TRACKER_FILE):
        with open(RESET_TRACKER_FILE, "r") as f:
            last_date = f.read().strip()
        if last_date != today:
            for d in usage_data:
                usage_data[d] = 0
            save_usage_data()
    with open(RESET_TRACKER_FILE, "w") as f:
        f.write(today)

def log_unauthorized(action):
    """Логирует неавторизованные попытки."""
    timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[UNAUTHORIZED] {action} — {timestamp}\n")

# --------------------------
# 🖥️ Интерфейс программы
# --------------------------

root = tk.Tk()
root.title("Smart Wi-Fi Parental Control")
root.geometry("430x640")
root.config(bg="#f0f4f8")

# --------------------------
# 🔐 Авторизация
# --------------------------

def login():
    global logged_in
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    if username and password:
        logged_in = True
        status_label.config(text=f"Logged in as {username} ✅", fg="green")
        messagebox.showinfo("Login", f"Welcome, {username}!")
    else:
        messagebox.showwarning("Login Failed", "Enter both username and password.")

login_frame = tk.LabelFrame(root, text="🔐 Login", bg="#e0f7fa", padx=10, pady=10)
login_frame.pack(padx=10, pady=10, fill="x")

username_entry = tk.Entry(login_frame, width=30)
username_entry.pack(pady=2)
username_entry.insert(0, "")

password_entry = tk.Entry(login_frame, width=30, show="*")
password_entry.pack(pady=2)

status_label = tk.Label(login_frame, text="Status: Not logged in 🔴", fg="red", bg="#e0f7fa")
status_label.pack(pady=4)

tk.Button(login_frame, text="Login", command=login, bg="#add8e6").pack(pady=5)

# --------------------------
# 📱 Управление устройствами
# --------------------------

def block_device():
    if not logged_in:
        log_unauthorized("Block Device")
        messagebox.showwarning("Denied", "Login required.")
        return
    name = device_entry.get().strip()
    if name:
        messagebox.showinfo("Blocked", f"{name} has been blocked.")
    else:
        messagebox.showwarning("Enter a device name.")

def unblock_device():
    if not logged_in:
        log_unauthorized("Unblock Device")
        messagebox.showwarning("Denied", "Login required.")
        return
    name = device_entry.get().strip()
    if name:
        messagebox.showinfo("Unblocked", f"{name} has been unblocked.")
    else:
        messagebox.showwarning("Enter a device name.")

def restart_router():
    if not logged_in:
        log_unauthorized("Restart Router")
        messagebox.showwarning("Denied", "Login required.")
        return
    messagebox.showinfo("Restart", "Router is restarting...")

device_frame = tk.LabelFrame(root, text="📶 Device Management", bg="#fce4ec", padx=10, pady=10)
device_frame.pack(padx=10, pady=10, fill="x")

device_entry = tk.Entry(device_frame, width=30)
device_entry.pack()

tk.Button(device_frame, text="Block Device", command=block_device, bg="#ff6961").pack(pady=2)
tk.Button(device_frame, text="Unblock Device", command=unblock_device, bg="#77dd77").pack(pady=2)
tk.Button(device_frame, text="Restart Router", command=restart_router, bg="#fdfd96").pack(pady=4)

# --------------------------
# 📊 Отображение устройств
# --------------------------

def add_time(device):
    if usage_data[device] >= DEVICE_LIMITS[device]:
        messagebox.showinfo("Limit Reached", f"{device} has hit its limit.")
    else:
        usage_data[device] += 15
        save_usage_data()
        refresh_device_list()

def refresh_device_list(filter_text=""):
    for w in devices_frame.winfo_children():
        if isinstance(w, tk.Frame):
            w.destroy()
    for i, dev in enumerate(DEVICE_LIMITS, 1):
        if filter_text.lower() in dev.lower():
            row = tk.Frame(devices_frame, bg="#fff3e0")
            row.pack(fill="x", pady=2)
            label = f"{i}. {dev} — {usage_data[dev]}/{DEVICE_LIMITS[dev]} min"
            tk.Label(row, text=label, anchor="w", width=30, bg="#fff3e0").pack(side="left")
            tk.Button(row, text="+15 min", command=lambda d=dev: add_time(d), bg="#d1c4e9").pack(side="right")

def search_keyrelease(event):
    refresh_device_list(search_entry.get())

devices_frame = tk.LabelFrame(root, text="📱 Connected Devices", bg="#fff3e0", padx=10, pady=10)
devices_frame.pack(padx=10, pady=10, fill="x")

search_entry = tk.Entry(devices_frame, width=30)
search_entry.insert(0, "Search...")
search_entry.pack(pady=(0, 5))
search_entry.bind("<KeyRelease>", search_keyrelease)

# --------------------------
# 🚀 Запуск
# --------------------------

load_usage_data()
reset_usage_if_new_day()
refresh_device_list()

root.mainloop()
