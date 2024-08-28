import tkinter as tk
from tkinter import ttk

def update_progress(progress_bar, label, splash_screen, i=0):
    if i <= 100:
        progress_bar["value"] = i
        label.config(text=f"Loading... {i}%")
        splash_screen.update_idletasks()
        splash_screen.after(50, update_progress, progress_bar, label, splash_screen, i + 1)
    else:
        splash_screen.destroy()

def create_splash_screen():
    splash_screen = tk.Tk()
    splash_screen.title("Loading")
    splash_screen.geometry("400x200")

    # 居中窗口
    x = (splash_screen.winfo_screenwidth() // 2) - (400 // 2)
    y = (splash_screen.winfo_screenheight() // 2) - (200 // 2)
    splash_screen.geometry(f'+{x}+{y}')

    label = tk.Label(splash_screen, text="Loading...", font=("Helvetica", 16))
    label.pack(pady=20)

    progress_bar = ttk.Progressbar(splash_screen, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=20)

    # 启动进度条更新
    splash_screen.after(0, update_progress, progress_bar, label, splash_screen)

    splash_screen.mainloop()

if __name__ == "__main__":
    create_splash_screen()
