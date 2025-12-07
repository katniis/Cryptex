"""
Main Application Controller
Manages the flow between auth and main windows
"""

import customtkinter as ctk
from ui.windows.auth_window import AuthWindow
from ui.windows.main_window import MainWindow
from services.price_update_service import get_price_service


class CryptexApp:
    """
    Main application controller
    """
    
    def __init__(self):
        self.root = None
        self.main_window = None
        self.current_user = None
        self.price_service = get_price_service()
        
    def start(self):
        """Start the application"""
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create hidden root window
        self.root = ctk.CTk()
        self.root.withdraw()  # Hide main window
        
        # Show auth window
        self.show_auth()
        
        # Start main loop
        self.root.mainloop()
    
    def show_auth(self):
        """Show authentication window"""
        AuthWindow(
            self.root,
            on_auth_success=self.on_auth_success
        )
    
    def on_auth_success(self, user):
        """Handle successful authentication"""
        self.current_user = user
        self.root.destroy()  # Destroy hidden root
        
        # Create and show main window
        self.main_window = MainWindow(user)
        
        # Handle window close
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_main_window_close)
        
        self.main_window.mainloop()
    
    def on_main_window_close(self):
        """Handle main window close"""
        if self.main_window:
            # Stop price service
            self.price_service.stop()
            
            # Close window
            self.main_window.quit()


def main():
    """Entry point"""
    app = CryptexApp()
    app.start()


if __name__ == "__main__":
    main()