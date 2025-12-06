"""
Main Dashboard Window
The main application interface after login
"""

import customtkinter as ctk
from ui.styles.colors import COLORS
from ui.styles.fonts import FONTS
from models.portfolio import Portfolio
from models.user import User


class MainWindow(ctk.CTk):
    """
    Main application window with sidebar and tabbed interface
    """
    
    def __init__(self, user):
        super().__init__()
        
        self.user = user
        self.current_portfolio = None
        self.portfolios = []
        
        # Window settings
        self.title("Cryptex - Portfolio Tracker")
        self.geometry("1400x800")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.setup_ui()
        self.load_portfolios()
        
    def setup_ui(self):
        """Setup main UI structure"""
        
        # ========== SIDEBAR ==========
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            fg_color=COLORS['bg_secondary'],
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)
        
        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🪙 Cryptex",
            font=FONTS['title'],
            text_color=COLORS['accent_primary']
        )
        logo_label.pack()
        
        # User info
        user_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS['bg_tertiary'])
        user_frame.grid(row=1, column=0, padx=15, pady=(0, 20), sticky="ew")
        
        user_label = ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.user.username}",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        user_label.pack(pady=10)
        
        # My Portfolios header
        portfolios_label = ctk.CTkLabel(
            self.sidebar,
            text="My Portfolios",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        )
        portfolios_label.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Portfolio list frame
        self.portfolio_list_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent"
        )
        self.portfolio_list_frame.grid(row=3, column=0, padx=15, pady=0, sticky="nsew")
        
        # Create Portfolio button
        create_portfolio_btn = ctk.CTkButton(
            self.sidebar,
            text="+ Create Portfolio",
            command=self.show_create_portfolio_dialog,
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover'],
            font=FONTS['button'],
            height=40
        )
        create_portfolio_btn.grid(row=4, column=0, padx=15, pady=15, sticky="ew")
        
        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").grid(row=5, column=0)
        
        # Logout button
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            command=self.handle_logout,
            fg_color="transparent",
            hover_color=COLORS['bg_tertiary'],
            border_width=1,
            border_color=COLORS['border'],
            font=FONTS['body'],
            height=35
        )
        logout_btn.grid(row=6, column=0, padx=15, pady=15, sticky="ew")
        
        # ========== MAIN CONTENT ==========
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_primary'],
            corner_radius=0
        )
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Top bar
        self.create_top_bar()
        
        # Content area (tabs will go here)
        self.content_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Show welcome message initially
        self.show_welcome_message()
    
    def create_top_bar(self):
        """Create top navigation bar"""
        top_bar = ctk.CTkFrame(
            self.main_frame,
            height=80,
            fg_color=COLORS['bg_secondary'],
            corner_radius=0
        )
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.grid_columnconfigure(1, weight=1)
        
        # Portfolio name
        self.portfolio_name_label = ctk.CTkLabel(
            top_bar,
            text="Select a portfolio",
            font=FONTS['title'],
            text_color=COLORS['text_primary']
        )
        self.portfolio_name_label.grid(row=0, column=0, padx=30, pady=20, sticky="w")
        
        # Portfolio value
        self.portfolio_value_label = ctk.CTkLabel(
            top_bar,
            text="$0.00",
            font=FONTS['heading'],
            text_color=COLORS['success']
        )
        self.portfolio_value_label.grid(row=0, column=1, padx=30, pady=20, sticky="e")
    
    def load_portfolios(self):
        """Load user's portfolios"""
        self.portfolios = Portfolio.get_by_user(self.user.user_id)
        self.update_portfolio_list()
        
        # Select first portfolio if available
        if self.portfolios:
            self.select_portfolio(self.portfolios[0])
    
    def update_portfolio_list(self):
        """Update portfolio list in sidebar"""
        # Clear existing
        for widget in self.portfolio_list_frame.winfo_children():
            widget.destroy()
        
        if not self.portfolios:
            empty_label = ctk.CTkLabel(
                self.portfolio_list_frame,
                text="No portfolios yet",
                font=FONTS['body_small'],
                text_color=COLORS['text_tertiary']
            )
            empty_label.pack(pady=20)
            return
        
        # Create portfolio cards
        for portfolio in self.portfolios:
            self.create_portfolio_card(portfolio)
    
    def create_portfolio_card(self, portfolio):
        """Create a portfolio card in sidebar"""
        is_selected = (self.current_portfolio and 
                      self.current_portfolio.portfolio_id == portfolio.portfolio_id)
        
        card = ctk.CTkButton(
            self.portfolio_list_frame,
            text=portfolio.portfolio_name,
            command=lambda p=portfolio: self.select_portfolio(p),
            fg_color=COLORS['accent_primary'] if is_selected else COLORS['bg_tertiary'],
            hover_color=COLORS['accent_hover'],
            font=FONTS['body'],
            height=50,
            anchor="w"
        )
        card.pack(fill="x", pady=5)
    
    def select_portfolio(self, portfolio):
        """Select and display a portfolio"""
        self.current_portfolio = portfolio
        self.portfolio_name_label.configure(text=portfolio.portfolio_name)
        
        # Update portfolio value
        total_value = portfolio.get_total_value()
        self.portfolio_value_label.configure(text=f"${total_value:,.2f}")
        
        # Update list to show selection
        self.update_portfolio_list()
        
        # Load portfolio content
        self.show_portfolio_content()
    
    def show_portfolio_content(self):
        """Show portfolio dashboard"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create tabview
        tabview = ctk.CTkTabview(
            self.content_frame,
            fg_color=COLORS['bg_secondary']
        )
        tabview.pack(fill="both", expand=True)
        
        # Add tabs
        tab_overview = tabview.add("Overview")
        tab_transactions = tabview.add("Transactions")
        tab_watchlist = tabview.add("Watchlist")
        tab_alerts = tabview.add("Alerts")
        
        # Overview tab content
        overview_label = ctk.CTkLabel(
            tab_overview,
            text="Overview Tab - Coming Soon",
            font=FONTS['heading']
        )
        overview_label.pack(pady=50)
        
        # Transactions tab content
        trans_label = ctk.CTkLabel(
            tab_transactions,
            text="Transactions Tab - Coming Soon",
            font=FONTS['heading']
        )
        trans_label.pack(pady=50)
        
        # Watchlist tab
        watch_label = ctk.CTkLabel(
            tab_watchlist,
            text="Watchlist Tab - Coming Soon",
            font=FONTS['heading']
        )
        watch_label.pack(pady=50)
        
        # Alerts tab
        alert_label = ctk.CTkLabel(
            tab_alerts,
            text="Alerts Tab - Coming Soon",
            font=FONTS['heading']
        )
        alert_label.pack(pady=50)
    
    def show_welcome_message(self):
        """Show welcome message when no portfolio selected"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        welcome_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        welcome_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text=f"Welcome, {self.user.username}! 👋",
            font=FONTS['title'],
            text_color=COLORS['text_primary']
        )
        welcome_label.pack(pady=20)
        
        if not self.portfolios:
            instruction_label = ctk.CTkLabel(
                welcome_frame,
                text="Create your first portfolio to get started",
                font=FONTS['body'],
                text_color=COLORS['text_secondary']
            )
            instruction_label.pack(pady=10)
            
            create_btn = ctk.CTkButton(
                welcome_frame,
                text="+ Create Portfolio",
                command=self.show_create_portfolio_dialog,
                fg_color=COLORS['accent_primary'],
                hover_color=COLORS['accent_hover'],
                font=FONTS['button'],
                height=45,
                width=200
            )
            create_btn.pack(pady=20)
    
    def show_create_portfolio_dialog(self):
        """Show dialog to create new portfolio"""
        dialog = ctk.CTkInputDialog(
            text="Enter portfolio name:",
            title="Create Portfolio"
        )
        portfolio_name = dialog.get_input()
        
        if portfolio_name:
            portfolio = Portfolio.create(
                user_id=self.user.user_id,
                portfolio_name=portfolio_name
            )
            
            if portfolio:
                self.portfolios.append(portfolio)
                self.update_portfolio_list()
                self.select_portfolio(portfolio)
    
    def handle_logout(self):
        """Handle logout"""
        self.destroy()


if __name__ == "__main__":
    # Test main window
    from models.user import User
    
    # Get or create test user
    user = User.get_by_username("testuser")
    if not user:
        user = User.create("testuser", "password", "test@example.com")
    
    app = MainWindow(user)
    app.mainloop()