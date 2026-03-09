import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
import os
from supabase import create_client, Client
from core.logger import get_logger
from ai.assistant import ai_assistant  # Import the AI assistant

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

        ai_btn = tk.Button(self.root, text="AI Assistant", command=self.open_ai_assistant)
        ai_btn.pack(pady=5)

        logout_btn = tk.Button(self.root, text="Logout", command=self.do_logout)
        logout_btn.pack(pady=5)

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

    def open_ai_assistant(self):
        """Open the AI Assistant window"""
        ai_window = tk.Toplevel(self.root)
        ai_window.title("AI Assistant")
        ai_window.geometry("700x500")

        # Chat display area
        chat_frame = tk.Frame(ai_window)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Input frame
        input_frame = tk.Frame(ai_window)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.user_input = tk.Entry(input_frame, font=("Arial", 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.user_input.bind("<Return>", self.send_message)  # Enter key sends message

        send_button = tk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Initial greeting
        self.display_message("AI Assistant", "Hello! I'm your AI assistant. How can I help you today?", "assistant")

    def send_message(self, event=None):
        """Send user message to AI and display response"""
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        # Display user message
        self.display_message("You", user_text, "user")
        self.user_input.delete(0, tk.END)

        # Get AI response
        try:
            result = ai_assistant.query_ai(user_text)
            ai_response = result['response']
            self.display_message("AI Assistant", ai_response, "assistant")
        except Exception as e:
            self.display_message("AI Assistant", f"Sorry, I encountered an error: {str(e)}", "assistant")

    def display_message(self, sender, message, role):
        """Display a message in the chat window"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add sender tag with formatting
        if role == "user":
            self.chat_display.insert(tk.END, f"{sender}: ", "user_tag")
        else:
            self.chat_display.insert(tk.END, f"{sender}: ", "assistant_tag")
            
        # Add message content
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        # Configure tags for styling
        self.chat_display.tag_config("user_tag", foreground="blue", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("assistant_tag", foreground="green", font=("Arial", 10, "bold"))
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)  # Scroll to bottom

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WatchDogGUI(root)
    root.mainloop()
