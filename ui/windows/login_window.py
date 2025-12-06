"""
Login Window
"""

import customtkinter as ctk
from ui.styles.colors import COLORS
from ui.styles.fonts import FONTS
from models.user import User


class LoginWindow(ctk.CTkToplevel):
    """
    Login window for user authentication
    """
    
    def __init__(self, parent, on_login_success, on_register_click):
        super().__init__(parent)
        
        self.on_login_success = on_login_success
        self.on_register_click = on_register_click
        
        # Window settings
        self.title("Cryptex - Login")
        self.geometry("400x500")
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
            text="🪙 Cryptex",
            font=FONTS['title_large'],
            text_color=COLORS['accent_primary']
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Portfolio Tracker",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        subtitle_label.pack(pady=(0, 40))
        
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
            placeholder_text="Enter your username",
            height=40,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.username_entry.pack(fill="x", pady=(0, 20))
        
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
            placeholder_text="Enter your password",
            show="•",
            height=40,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.password_entry.pack(fill="x", pady=(0, 10))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=FONTS['body_small'],
            text_color=COLORS['danger']
        )
        self.error_label.pack(pady=(0, 20))
        
        # Login button
        login_button = ctk.CTkButton(
            main_frame,
            text="Login",
            command=self.handle_login,
            height=45,
            font=FONTS['button'],
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover']
        )
        login_button.pack(fill="x", pady=(0, 15))
        
        # Divider
        divider_frame = ctk.CTkFrame(main_frame, height=1, fg_color=COLORS['border'])
        divider_frame.pack(fill="x", pady=20)
        
        # Register section
        register_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        register_frame.pack()
        
        register_label = ctk.CTkLabel(
            register_frame,
            text="Don't have an account?",
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        )
        register_label.pack(side="left", padx=(0, 5))
        
        register_button = ctk.CTkButton(
            register_frame,
            text="Register",
            command=self.handle_register_click,
            width=80,
            height=30,
            font=FONTS['body_small'],
            fg_color="transparent",
            hover_color=COLORS['bg_tertiary'],
            text_color=COLORS['accent_primary']
        )
        register_button.pack(side="left")
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validate input
        if not username or not password:
            self.show_error("Please enter username and password")
            return
        
        # Authenticate
        user = User.authenticate(username, password)
        
        if user:
            self.error_label.configure(text="")
            self.on_login_success(user)
            self.destroy()
        else:
            self.show_error("Invalid username or password")
    
    def handle_register_click(self):
        """Handle register button click"""
        self.destroy()
        self.on_register_click()
    
    def show_error(self, message):
        """Show error message"""
        self.error_label.configure(text=message)


if __name__ == "__main__":
    # Test the login window
    ctk.set_appearance_mode("dark")
    
    root = ctk.CTk()
    root.withdraw()  # Hide main window
    
    def on_success(user):
        print(f"Login successful: {user.username}")
        root.quit()
    
    def on_register():
        print("Register clicked")
    
    login_win = LoginWindow(root, on_success, on_register)
    
    root.mainloop()