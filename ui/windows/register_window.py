"""
Registration Window
"""

import customtkinter as ctk
from ui.styles.colors import COLORS
from ui.styles.fonts import FONTS
from models.user import User
import re


class RegisterWindow(ctk.CTkToplevel):
    """
    Registration window for new users
    """
    
    def __init__(self, parent, on_register_success, on_login_click):
        super().__init__(parent)
        
        self.on_register_success = on_register_success
        self.on_login_click = on_login_click
        
        # Window settings
        self.title("Cryptex - Register")
        self.geometry("400x600")
        self.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup UI elements"""
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'])
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Create Account",
            font=FONTS['title'],
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Join Cryptex today",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Username
        username_label = ctk.CTkLabel(
            main_frame,
            text="Username",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Choose a username",
            height=40,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Email
        email_label = ctk.CTkLabel(
            main_frame,
            text="Email",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="your@email.com",
            height=40,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.email_entry.pack(fill="x", pady=(0, 15))
        
        # Password
        password_label = ctk.CTkLabel(
            main_frame,
            text="Password",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Create a password",
            show="•",
            height=40,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.password_entry.pack(fill="x", pady=(0, 15))
        
        # Confirm Password
        confirm_label = ctk.CTkLabel(
            main_frame,
            text="Confirm Password",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        confirm_label.pack(anchor="w", pady=(0, 5))
        
        self.confirm_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Confirm your password",
            show="•",
            height=40,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.confirm_entry.pack(fill="x", pady=(0, 10))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=FONTS['body_small'],
            text_color=COLORS['danger']
        )
        self.error_label.pack(pady=(0, 15))
        
        # Register button
        register_button = ctk.CTkButton(
            main_frame,
            text="Create Account",
            command=self.handle_register,
            height=45,
            font=FONTS['button'],
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover']
        )
        register_button.pack(fill="x", pady=(0, 15))
        
        # Divider
        divider_frame = ctk.CTkFrame(main_frame, height=1, fg_color=COLORS['border'])
        divider_frame.pack(fill="x", pady=15)
        
        # Login section
        login_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        login_frame.pack()
        
        login_label = ctk.CTkLabel(
            login_frame,
            text="Already have an account?",
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        )
        login_label.pack(side="left", padx=(0, 5))
        
        login_button = ctk.CTkButton(
            login_frame,
            text="Login",
            command=self.handle_login_click,
            width=60,
            height=30,
            font=FONTS['body_small'],
            fg_color="transparent",
            hover_color=COLORS['bg_tertiary'],
            text_color=COLORS['accent_primary']
        )
        login_button.pack(side="left")
        
        # Bind Enter key
        self.confirm_entry.bind("<Return>", lambda e: self.handle_register())
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def handle_register(self):
        """Handle register button click"""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        # Validation
        if not username or not email or not password:
            self.show_error("All fields are required")
            return
        
        if len(username) < 3:
            self.show_error("Username must be at least 3 characters")
            return
        
        if not self.validate_email(email):
            self.show_error("Invalid email format")
            return
        
        if len(password) < 6:
            self.show_error("Password must be at least 6 characters")
            return
        
        if password != confirm:
            self.show_error("Passwords do not match")
            return
        
        # Create user
        user = User.create(username, password, email)
        
        if user:
            self.error_label.configure(text="")
            self.on_register_success(user)
            self.destroy()
        else:
            self.show_error("Username already exists")
    
    def handle_login_click(self):
        """Handle login button click"""
        self.destroy()
        self.on_login_click()
    
    def show_error(self, message):
        """Show error message"""
        self.error_label.configure(text=message)


if __name__ == "__main__":
    # Test the register window
    ctk.set_appearance_mode("dark")
    
    root = ctk.CTk()
    root.withdraw()
    
    def on_success(user):
        print(f"Registration successful: {user.username}")
        root.quit()
    
    def on_login():
        print("Login clicked")
    
    register_win = RegisterWindow(root, on_success, on_login)
    
    root.mainloop()