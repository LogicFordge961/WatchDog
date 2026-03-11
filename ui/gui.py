# gui/main_window.py
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import json
import os
from supabase import create_client, Client
from core.logger import get_logger
from ai.assistant import ai_assistant
import tkinter.font as tkFont

logger = get_logger("GUI")

# Supabase config
SUPABASE_URL = "https://bmpoabdmwmoxqwjyooio.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJtcG9hYmRtd21veHF3anlvb2lvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5NDM3MzYsImV4cCI6MjA4ODUxOTczNn0.-wMv2i4yCNXV5VGxsLOdwwtNZtGBm65-MmhUanonYP4"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

class ModernFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.config(bg="#2c3e50", relief="flat", bd=0)
        
class WatchDogGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WatchDog - System Intelligence Framework")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a2e")
        
        # Make window resizable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create canvas for grid background
        self.create_grid_background()
        
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

    def create_grid_background(self):
        """Create a subtle grid background"""
        self.canvas = tk.Canvas(self.root, bg="#1a1a2e", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Draw grid pattern
        self.draw_grid_pattern()
        
        # Bind resize event
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
    def draw_grid_pattern(self):
        """Draw subtle grid pattern on canvas"""
        self.canvas.delete("grid")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
            
        # Draw grid lines
        grid_size = 20
        for x in range(0, width, grid_size):
            self.canvas.create_line(x, 0, x, height, fill="#252540", tags="grid")
        for y in range(0, height, grid_size):
            self.canvas.create_line(0, y, width, y, fill="#252540", tags="grid")
            
        # Draw subtle dots at intersections
        for x in range(0, width, grid_size):
            for y in range(0, height, grid_size):
                self.canvas.create_oval(x-1, y-1, x+1, y+1, fill="#343455", outline="", tags="grid")

    def on_canvas_resize(self, event):
        """Handle canvas resize"""
        self.draw_grid_pattern()

    def load_session(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'user.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    return data.get('session')
            except json.JSONDecodeError:
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
        
        # Create main frame
        main_frame = ModernFrame(self.canvas)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="WatchDog Login", 
            font=("Arial", 24, "bold"),
            fg="#ffffff",
            bg="#2c3e50"
        )
        title_label.pack(pady=(30, 20))
        
        # Form container
        form_frame = ModernFrame(main_frame)
        form_frame.pack(padx=40, pady=(0, 30), fill="both", expand=True)
        
        # Email
        email_label = tk.Label(
            form_frame, 
            text="EMAIL", 
            font=("Arial", 10, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        email_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.email_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            bg="#34495e",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#3498db",
            highlightcolor="#3498db"
        )
        self.email_entry.pack(fill="x", padx=20, pady=(0, 15), ipady=8)
        
        # Password
        pass_label = tk.Label(
            form_frame, 
            text="PASSWORD", 
            font=("Arial", 10, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        pass_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.pass_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            bg="#34495e",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            show="*",
            highlightthickness=1,
            highlightbackground="#3498db",
            highlightcolor="#3498db"
        )
        self.pass_entry.pack(fill="x", padx=20, pady=(0, 20), ipady=8)
        
        # Buttons frame
        buttons_frame = tk.Frame(form_frame, bg="#2c3e50")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        login_btn = tk.Button(
            buttons_frame,
            text="LOGIN",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="#ffffff",
            activebackground="#2980b9",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            command=self.do_login
        )
        login_btn.pack(side=tk.LEFT, fill="x", expand=True, ipady=10)
        
        signup_btn = tk.Button(
            buttons_frame,
            text="SIGN UP",
            font=("Arial", 11, "bold"),
            bg="#2ecc71",
            fg="#ffffff",
            activebackground="#27ae60",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            command=self.do_signup
        )
        signup_btn.pack(side=tk.RIGHT, fill="x", expand=True, ipady=10, padx=(10, 0))
        
        # Status label
        self.status_label = tk.Label(
            form_frame,
            text="",
            font=("Arial", 10),
            fg="#e74c3c",
            bg="#2c3e50"
        )
        self.status_label.pack(pady=(0, 20))
        
        # Bind Enter key to login
        self.email_entry.bind("<Return>", lambda e: self.pass_entry.focus())
        self.pass_entry.bind("<Return>", lambda e: self.do_login())

    def do_login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        if not email or not password:
            self.status_label.config(text="Please enter email and password")
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
            self.status_label.config(text="Please enter email and password")
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
        
        # Recreate grid background
        self.create_grid_background()
        
        # Main container
        main_container = ModernFrame(self.canvas)
        main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.7)
        
        # Header
        header_frame = ModernFrame(main_container)
        header_frame.pack(fill="x", padx=20, pady=(30, 20))
        
        title_label = tk.Label(
            header_frame,
            text="WatchDog Dashboard",
            font=("Arial", 20, "bold"),
            fg="#ffffff",
            bg="#2c3e50"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Advanced System Monitoring & AI Assistant",
            font=("Arial", 11),
            fg="#bdc3c7",
            bg="#2c3e50"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Content frame
        content_frame = ModernFrame(main_container)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Feature buttons in a grid
        button_configs = [
            {"text": "Run Monitoring", "command": self.run_monitoring, "color": "#3498db"},
            {"text": "AI Assistant", "command": self.open_ai_assistant, "color": "#9b59b6"},
            {"text": "System Scanner", "command": self.system_scanner, "color": "#e67e22"},
            {"text": "Process Manager", "command": self.process_manager, "color": "#2ecc71"},
            {"text": "Settings", "command": self.settings, "color": "#f1c40f"},
            {"text": "Logout", "command": self.do_logout, "color": "#e74c3c"}
        ]
        
        # Create button grid
        row, col = 0, 0
        for i, config in enumerate(button_configs):
            if col > 2:  # 3 columns max
                col = 0
                row += 1
                
            btn_frame = tk.Frame(content_frame, bg="#2c3e50", relief="flat")
            btn_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            button = tk.Button(
                btn_frame,
                text=config["text"],
                font=("Arial", 12, "bold"),
                bg=config["color"],
                fg="#ffffff",
                activebackground=self.darken_color(config["color"]),
                activeforeground="#ffffff",
                relief="flat",
                cursor="hand2",
                command=config["command"],
                bd=0,
                padx=20,
                pady=15
            )
            button.pack(fill="both", expand=True)
            
            col += 1
        
        # Configure grid weights
        for i in range(3):
            content_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            content_frame.grid_rowconfigure(i, weight=1)

    def darken_color(self, color):
        """Simple color darkening function"""
        color_map = {
            "#3498db": "#2980b9",
            "#9b59b6": "#8e44ad",
            "#e67e22": "#d35400",
            "#2ecc71": "#27ae60",
            "#f1c40f": "#f39c12",
            "#e74c3c": "#c0392b"
        }
        return color_map.get(color, color)

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
        messagebox.showinfo("Monitoring", "System monitoring started!\nThis feature will continuously monitor your system performance.")

    def system_scanner(self):
        messagebox.showinfo("Scanner", "System scanner activated!\nThis will scan for potential issues and optimizations.")

    def process_manager(self):
        messagebox.showinfo("Process Manager", "Process management tools loaded!\nManage running applications and system resources.")

    def settings(self):
        messagebox.showinfo("Settings", "Settings panel opened!\nCustomize your WatchDog experience.")

    def open_ai_assistant(self):
        """Open the AI Assistant window"""
        ai_window = tk.Toplevel(self.root)
        ai_window.title("AI Assistant")
        ai_window.geometry("800x600")
        ai_window.configure(bg="#1a1a2e")
        ai_window.minsize(600, 400)
        
        # Create grid background for AI window
        ai_canvas = tk.Canvas(ai_window, bg="#1a1a2e", highlightthickness=0)
        ai_canvas.pack(fill="both", expand=True)
        
        def draw_ai_grid():
            ai_canvas.delete("grid")
            width = ai_canvas.winfo_width()
            height = ai_canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                return
                
            grid_size = 25
            for x in range(0, width, grid_size):
                ai_canvas.create_line(x, 0, x, height, fill="#252540", tags="grid")
            for y in range(0, height, grid_size):
                ai_canvas.create_line(0, y, width, y, fill="#252540", tags="grid")
                
        def on_ai_resize(event):
            draw_ai_grid()
            
        ai_canvas.bind("<Configure>", on_ai_resize)
        
        # Header frame
        header_frame = ModernFrame(ai_canvas)
        header_frame.place(relx=0.5, rely=0.05, anchor="n", relwidth=0.9)
        
        title_label = tk.Label(
            header_frame,
            text="AI Assistant",
            font=("Arial", 18, "bold"),
            fg="#ffffff",
            bg="#2c3e50"
        )
        title_label.pack(pady=15)
        
        # Chat container
        chat_container = ModernFrame(ai_canvas)
        chat_container.place(relx=0.5, rely=0.15, anchor="n", relwidth=0.9, relheight=0.7)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#2c3e50",
            fg="#ecf0f1",
            insertbackground="#ffffff",
            relief="flat",
            state=tk.DISABLED
        )
        self.chat_display.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Configure text tags for styling
        self.chat_display.tag_config("user_tag", foreground="#3498db", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("assistant_tag", foreground="#2ecc71", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("system_tag", foreground="#f1c40f", font=("Arial", 11, "bold"))
        
        # Input frame
        input_frame = ModernFrame(ai_canvas)
        input_frame.place(relx=0.5, rely=0.9, anchor="n", relwidth=0.9)
        
        # User input
        input_container = tk.Frame(input_frame, bg="#2c3e50")
        input_container.pack(fill="x", padx=15, pady=(0, 15))
        
        self.user_input = tk.Entry(
            input_container,
            font=("Arial", 12),
            bg="#34495e",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#3498db",
            highlightcolor="#3498db"
        )
        self.user_input.pack(side=tk.LEFT, fill="x", expand=True, ipady=10, padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)
        
        send_button = tk.Button(
            input_container,
            text="SEND",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="#ffffff",
            activebackground="#2980b9",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            command=self.send_message
        )
        send_button.pack(side=tk.RIGHT, ipadx=20, ipady=10)
        
        # Initial greeting
        self.display_message("AI Assistant", "Hello! I'm your AI assistant. How can I help you today?", "assistant")
        
        # Focus on input
        self.user_input.focus()

    def send_message(self, event=None):
        """Send user message to AI and display response"""
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        # Display user message
        self.display_message("You", user_text, "user")
        self.user_input.delete(0, tk.END)

        # Show thinking indicator
        self.display_message("AI Assistant", "Thinking...", "system")
        self.chat_display.see(tk.END)
        self.chat_display.update()
        
        # Get AI response
        try:
            result = ai_assistant.query_ai(user_text)
            ai_response = result['response']
            
            # Remove thinking indicator and show actual response
            self.chat_display.config(state=tk.NORMAL)
            # Delete last line (thinking indicator)
            self.chat_display.delete("end-2l", "end-1l")
            self.chat_display.config(state=tk.DISABLED)
            
            self.display_message("AI Assistant", ai_response, "assistant")
        except Exception as e:
            # Remove thinking indicator and show error
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("end-2l", "end-1l")
            self.chat_display.config(state=tk.DISABLED)
            
            self.display_message("AI Assistant", f"Sorry, I encountered an error: {str(e)}", "assistant")

    def display_message(self, sender, message, role):
        """Display a message in the chat window"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add sender tag with formatting
        if role == "user":
            self.chat_display.insert(tk.END, f"{sender}: ", "user_tag")
        elif role == "assistant":
            self.chat_display.insert(tk.END, f"{sender}: ", "assistant_tag")
        else:
            self.chat_display.insert(tk.END, f"{sender}: ", "system_tag")
            
        # Add message content
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)  # Scroll to bottom

    def clear_window(self):
        """Clear all widgets from the main window"""
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WatchDogGUI(root)
    root.mainloop()
