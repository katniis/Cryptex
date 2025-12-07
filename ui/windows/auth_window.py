"""
Authentication Window
Combined Login and Register in one window with tabs
"""

import customtkinter as ctk
from ui.styles.colors import COLORS
from ui.styles.fonts import FONTS
from models.user import User
import re


class AuthWindow(ctk.CTkToplevel):
    """
    Combined authentication window with Login and Register tabs
    """
    
    def __init__(self, parent, on_auth_success):
        super().__init__(parent)
        
        self.on_auth_success = on_auth_success
        
        # Window settings
        self.title("Cryptex - Welcome")
        self.geometry("450x650")
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
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Welcome Back",
            font=FONTS['title_large'],
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(0, 40))
        
        # Tab view
        self.tabview = ctk.CTkTabview(
            main_frame,
            fg_color=COLORS['bg_secondary'],
            segmented_button_fg_color=COLORS['bg_tertiary'],
            segmented_button_selected_color=COLORS['accent_primary'],
            segmented_button_selected_hover_color=COLORS['accent_hover']
        )
        self.tabview.pack(fill="both", expand=True)
        
        # Add tabs
        self.login_tab = self.tabview.add("Login")
        self.register_tab = self.tabview.add("Register")
        
        # Setup login tab
        self.setup_login_tab()
        
        # Setup register tab
        self.setup_register_tab()
    
    def setup_login_tab(self):
        """Setup login tab content"""
        
        # Username
        username_label = ctk.CTkLabel(
            self.login_tab,
            text="Username",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        username_label.pack(anchor="w", pady=(20, 5), padx=20)
        
        self.login_username_entry = ctk.CTkEntry(
            self.login_tab,
            placeholder_text="Enter your username",
            height=45,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.login_username_entry.pack(fill="x", pady=(0, 20), padx=20)
        
        # Password
        password_label = ctk.CTkLabel(
            self.login_tab,
            text="Password",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        password_label.pack(anchor="w", pady=(0, 5), padx=20)
        
        self.login_password_entry = ctk.CTkEntry(
            self.login_tab,
            placeholder_text="Enter your password",
            show="•",
            height=45,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.login_password_entry.pack(fill="x", pady=(0, 10), padx=20)
        
        
        # Error label
        self.login_error_label = ctk.CTkLabel(
            self.login_tab,
            text="",
            font=FONTS['body_small'],
            text_color=COLORS['danger']
        )
        self.login_error_label.pack(pady=(0, 20), padx=20)
        
        # Login button
        login_button = ctk.CTkButton(
            self.login_tab,
            text="Log in",
            command=self.handle_login,
            height=50,
            font=FONTS['button'],
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover']
        )
        login_button.pack(fill="x", pady=(0, 20), padx=20)
        
        # Sign up link
        signup_frame = ctk.CTkFrame(self.login_tab, fg_color="transparent")
        signup_frame.pack(pady=(20, 0))
        
        signup_label = ctk.CTkLabel(
            signup_frame,
            text="Don't have an account?",
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        )
        signup_label.pack(side="left", padx=(0, 5))
        
        signup_button = ctk.CTkButton(
            signup_frame,
            text="Sign up here",
            command=lambda: self.tabview.set("Register"),
            width=80,
            height=25,
            font=FONTS['body_small'],
            fg_color="transparent",
            hover_color=COLORS['bg_tertiary'],
            text_color=COLORS['accent_primary']
        )
        signup_button.pack(side="left")
        
        # Bind Enter key
        self.login_password_entry.bind("<Return>", lambda e: self.handle_login())
    
    def setup_register_tab(self):
        """Setup register tab content"""
        
        # Username
        username_label = ctk.CTkLabel(
            self.register_tab,
            text="Username",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        username_label.pack(anchor="w", pady=(20, 5), padx=20)
        
        self.register_username_entry = ctk.CTkEntry(
            self.register_tab,
            placeholder_text="Choose a username",
            height=45,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.register_username_entry.pack(fill="x", pady=(0, 15), padx=20)
        
        # Email
        email_label = ctk.CTkLabel(
            self.register_tab,
            text="Email Address",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        email_label.pack(anchor="w", pady=(0, 5), padx=20)
        
        self.register_email_entry = ctk.CTkEntry(
            self.register_tab,
            placeholder_text="Enter email",
            height=45,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.register_email_entry.pack(fill="x", pady=(0, 15), padx=20)
        
        # Password
        password_label = ctk.CTkLabel(
            self.register_tab,
            text="Password",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        password_label.pack(anchor="w", pady=(0, 5), padx=20)
        
        self.register_password_entry = ctk.CTkEntry(
            self.register_tab,
            placeholder_text="Create a password",
            show="•",
            height=45,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.register_password_entry.pack(fill="x", pady=(0, 15), padx=20)
        
        # Confirm Password
        confirm_label = ctk.CTkLabel(
            self.register_tab,
            text="Confirm Password",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        confirm_label.pack(anchor="w", pady=(0, 5), padx=20)
        
        self.register_confirm_entry = ctk.CTkEntry(
            self.register_tab,
            placeholder_text="Confirm your password",
            show="•",
            height=45,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.register_confirm_entry.pack(fill="x", pady=(0, 10), padx=20)
        
        # Error label
        self.register_error_label = ctk.CTkLabel(
            self.register_tab,
            text="",
            font=FONTS['body_small'],
            text_color=COLORS['danger']
        )
        self.register_error_label.pack(pady=(0, 20), padx=20)
        
        # Register button
        register_button = ctk.CTkButton(
            self.register_tab,
            text="Create Account",
            command=self.handle_register,
            height=50,
            font=FONTS['button'],
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover']
        )
        register_button.pack(fill="x", pady=(0, 20), padx=20)
        
        # Login link
        login_frame = ctk.CTkFrame(self.register_tab, fg_color="transparent")
        login_frame.pack(pady=(10, 0))
        
        login_label = ctk.CTkLabel(
            login_frame,
            text="Already have an account?",
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        )
        login_label.pack(side="left", padx=(0, 5))
        
        login_button = ctk.CTkButton(
            login_frame,
            text="Log in",
            command=lambda: self.tabview.set("Login"),
            width=60,
            height=25,
            font=FONTS['body_small'],
            fg_color="transparent",
            hover_color=COLORS['bg_tertiary'],
            text_color=COLORS['accent_primary']
        )
        login_button.pack(side="left")
        
        # Bind Enter key
        self.register_confirm_entry.bind("<Return>", lambda e: self.handle_register())
    
    def handle_login(self):
        """Handle login"""
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get()
        
        # Validate
        if not username or not password:
            self.show_login_error("Please enter username and password")
            return
        
        # Authenticate
        user = User.authenticate(username, password)
        
        if user:
            self.login_error_label.configure(text="")
            self.on_auth_success(user)
            self.destroy()
        else:
            self.show_login_error("Invalid username or password")
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def handle_register(self):
        """Handle registration"""
        username = self.register_username_entry.get().strip()
        email = self.register_email_entry.get().strip()
        password = self.register_password_entry.get()
        confirm = self.register_confirm_entry.get()
        
        # Validation
        if not username or not email or not password:
            self.show_register_error("All fields are required")
            return
        
        if len(username) < 3:
            self.show_register_error("Username must be at least 3 characters")
            return
        
        if not self.validate_email(email):
            self.show_register_error("Invalid email format")
            return
        
        if len(password) < 6:
            self.show_register_error("Password must be at least 6 characters")
            return
        
        if password != confirm:
            self.show_register_error("Passwords do not match")
            return
        
        # Create user
        user = User.create(username, password, email)
        
        if user:
            self.register_error_label.configure(text="")
            self.on_auth_success(user)
            self.destroy()
        else:
            self.show_register_error("Username already exists")
    
    def show_login_error(self, message):
        """Show login error"""
        self.login_error_label.configure(text=message)
    
    def show_register_error(self, message):
        """Show register error"""
        self.register_error_label.configure(text=message)


if __name__ == "__main__":
    # Test
    ctk.set_appearance_mode("dark")
    
    root = ctk.CTk()
    root.withdraw()
    
    def on_success(user):
        print(f"Auth successful: {user.username}")
        root.quit()
    
    auth_win = AuthWindow(root, on_success)
    
    root.mainloop()