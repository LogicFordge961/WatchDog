import tkinter as tk
from tkinter import messagebox
import json
import os
from supabase import create_client, Client
from core.logger import get_logger

logger = get_logger("GUI")

# Supabase config - replace with your actual values
SUPABASE_URL = "https://bmpoabdmwmoxqwjyooio.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJtcG9hYmRtd21veHF3anlvb2lvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5NDM3MzYsImV4cCI6MjA4ODUxOTczNn0.-wMv2i4yCNXV5VGxsLOdwwtNZtGBm65-MmhUanonYP4"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

class WatchDogGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WatchDog - System Intelligence Framework")
        self.root.geometry("600x400")

        # Check if logged in
        self.session = self.load_session()
        if self.session:
            try:
                supabase.auth.set_session(self.session['access_token'], self.session['refresh_token'])
                self.show_main()
            except Exception:
                self.show_login()
        else:
            self.show_login()

    def load_session(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'user.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    return data.get('session')
            except json.JSONDecodeError:
                # Corrupted file, remove it
                os.remove(config_path)
                return None
        return None

    def save_session(self, session_dict):
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, 'user.json')
        with open(config_path, 'w') as f:
            json.dump({'session': session_dict}, f)

    def show_login(self):
        self.clear_window()
        label = tk.Label(self.root, text="Login to WatchDog", font=("Arial", 16))
        label.pack(pady=20)

        # Email
        email_label = tk.Label(self.root, text="Email:")
        email_label.pack()
        self.email_entry = tk.Entry(self.root, width=30)
        self.email_entry.pack(pady=5)

        # Password
        pass_label = tk.Label(self.root, text="Password:")
        pass_label.pack()
        self.pass_entry = tk.Entry(self.root, width=30, show="*")
        self.pass_entry.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        login_btn = tk.Button(btn_frame, text="Login", command=self.do_login)
        login_btn.pack(side=tk.LEFT, padx=5)
        signup_btn = tk.Button(btn_frame, text="Sign Up", command=self.do_signup)
        signup_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()

    def do_login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        if not email or not password:
            self.status_label.config(text="Enter email and password")
            return
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response.user:
                self.session = {
                    'access_token': response.session.access_token,
                    'refresh_token': response.session.refresh_token,
                    'user_id': response.user.id
                }
                self.save_session(self.session)
                self.show_main()
            else:
                self.status_label.config(text="Login failed")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def do_signup(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        if not email or not password:
            self.status_label.config(text="Enter email and password")
            return
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if response.user:
                self.status_label.config(text="Sign up successful! Check email to confirm.")
            else:
                self.status_label.config(text="Sign up failed")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def show_main(self):
        self.clear_window()
        label = tk.Label(self.root, text="Welcome to WatchDog!", font=("Arial", 16))
        label.pack(pady=20)

        # Add buttons for features
        run_btn = tk.Button(self.root, text="Run Monitoring", command=self.run_monitoring)
        run_btn.pack(pady=5)

        ai_btn = tk.Button(self.root, text="AI Assistant", command=self.ai_assistant)
        ai_btn.pack(pady=5)

        logout_btn = tk.Button(self.root, text="Logout", command=self.do_logout)
        logout_btn.pack(pady=5)

        # Add more buttons as needed

    def do_logout(self):
        try:
            supabase.auth.sign_out()
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'user.json')
            if os.path.exists(config_path):
                os.remove(config_path)
            self.session = None
            self.show_login()
        except Exception as e:
            messagebox.showerror("Error", f"Logout failed: {str(e)}")

    def run_monitoring(self):
        # Placeholder
        messagebox.showinfo("Info", "Monitoring started")

    def ai_assistant(self):
        # Placeholder
        messagebox.showinfo("Info", "AI Assistant")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WatchDogGUI(root)
    root.mainloop()