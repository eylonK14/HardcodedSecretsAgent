import threading
import subprocess
import time
import importlib.util
import os
import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from smart_agent import run_analysis
POLL_INTERVAL = 5  # seconds

class SecretWatcherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Git Push Secret Watcher")
        self.geometry("700x500")

        # Repo selection
        self.repo_path = None
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Select Git Repository", command=self.select_repo).pack(side=tk.LEFT, padx=5)
        self.start_btn = tk.Button(btn_frame, text="Start Monitoring", state=tk.DISABLED, command=self.start_monitor)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # Output area
        self.output = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Consolas", 10))
        self.output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.monitor_thread = None
        self.stopped = threading.Event()
        self.last_remote_hash = None

    def select_repo(self):
        path = filedialog.askdirectory(title="Select your Git repository root")
        if path and os.path.isdir(os.path.join(path, ".git")):
            self.repo_path = path
            self.output.insert(tk.END, f"📂 Repository set to: {self.repo_path}\n")
            self.start_btn.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Invalid Repository", "Selected folder is not a Git repository.")

    def start_monitor(self):
        if not self.repo_path: return
        self.start_btn.config(state=tk.DISABLED)
        self.output.insert(tk.END, "▶️ Starting monitor...\n")
        self.stopped.clear()
        # initialize last hash
        self.last_remote_hash = self.get_remote_head()
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def get_remote_head(self):
        try:
            completed = subprocess.run(
                ["git", "ls-remote", "origin", "HEAD"],
                cwd=self.repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=10
            )
            return completed.stdout.split()[0] if completed.stdout else None
        except Exception:
            return None

    def monitor_loop(self):
        while not self.stopped.is_set():
            time.sleep(POLL_INTERVAL)
            current = self.get_remote_head()
            if current and current != self.last_remote_hash:
                self.last_remote_hash = current
                self.on_push_detected(current)

    def on_push_detected(self, new_hash):
        self.output.insert(tk.END, f"\n🔔 Detected new push: {new_hash}\n")
        run_analysis(self.repo_path,self.output)

    def on_close(self):
        self.stopped.set()
        self.destroy()

if __name__ == "__main__":
    app = SecretWatcherApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
