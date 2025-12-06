"""
Main Application Controller
Manages the flow between login, register, and main windows
"""

import customtkinter as ctk
from ui.windows.login_window import LoginWindow
from ui.windows.register_window import RegisterWindow
from ui.windows.main_window import MainWindow
from models.user import User


class CryptexApp:
    """
    Main application controller
    """
    
    def __init__(self):
        self.root = None
        self.main_window = None
        self.current_user = None
        
    def start(self):
        """Start the application"""
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create hidden root window
        self.root = ctk.CTk()
        self.root.withdraw()  # Hide main window
        
        # If no users exist in the database, force registration first.
        try:
            users = User.get_all()
        except Exception:
            users = None

        if not users:
            # No users — require registration before login
            self.show_register()
        else:
            # Users exist — proceed to login as normal
            self.show_login()
        
        # Start main loop
        self.root.mainloop()
    
    def show_login(self):
        """Show login window"""
        LoginWindow(
            self.root,
            on_login_success=self.on_login_success,
            on_register_click=self.show_register
        )
    
    def show_register(self):
        """Show registration window"""
        RegisterWindow(
            self.root,
            on_register_success=self.on_register_success,
            on_login_click=self.show_login
        )
    
    def on_login_success(self, user):
        """Handle successful login"""
        self.current_user = user
        self.root.destroy()  # Destroy hidden root
        
        # Create and show main window
        self.main_window = MainWindow(user)
        
        # Handle window close
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_main_window_close)
        
        self.main_window.mainloop()
    
    def on_register_success(self, user):
        """Handle successful registration"""
        # Same as login success
        self.on_login_success(user)
    
    def on_main_window_close(self):
        """Handle main window close"""
        if self.main_window:
            self.main_window.quit()


def main():
    """Entry point"""
    app = CryptexApp()
    app.start()


if __name__ == "__main__":
    main()