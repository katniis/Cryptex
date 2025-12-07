"""
Watchlist Tab Frame
Track cryptocurrencies without owning them
"""

import customtkinter as ctk
from ui.styles.colors import COLORS
from ui.styles.fonts import FONTS
from models.watchlist import Watchlist
from models.cryptocurrency import CryptoCurrency
from models.price import Price


class WatchlistFrame(ctk.CTkFrame):
    """
    Watchlist tab for tracking cryptocurrencies
    """
    
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        
        self.setup_ui()
        self.load_watchlist()
    
    def setup_ui(self):
        """Setup UI elements"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Top bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        top_bar.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            top_bar,
            text="Watchlist",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Add to Watchlist button
        add_btn = ctk.CTkButton(
            top_bar,
            text="+ Add to Watchlist",
            command=self.show_add_dialog,
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover'],
            font=FONTS['button'],
            height=40
        )
        add_btn.grid(row=0, column=2, sticky="e")
        
        # Watchlist items frame
        self.watchlist_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_secondary']
        )
        self.watchlist_frame.grid(row=1, column=0, sticky="nsew")
        
        # Table header
        self.create_header()
    
    def create_header(self):
        """Create watchlist table header"""
        header_frame = ctk.CTkFrame(
            self.watchlist_frame,
            fg_color=COLORS['bg_tertiary'],
            height=40
        )
        header_frame.pack(fill="x", pady=(0, 5))
        
        headers = [
            ("Asset", 0.25),
            ("Symbol", 0.15),
            ("Current Price", 0.20),
            ("24h Change", 0.15),
            ("Market Cap Rank", 0.15),
            ("Actions", 0.10)
        ]
        
        for text, relwidth in headers:
            label = ctk.CTkLabel(
                header_frame,
                text=text,
                font=FONTS['subheading'],
                text_color=COLORS['text_primary']
            )
            label.place(relx=sum(h[1] for h in headers[:headers.index((text, relwidth))]),
                       rely=0.5, anchor="w", relwidth=relwidth)
    
    def load_watchlist(self):
        """Load watchlist items"""
        # Clear existing
        for widget in self.watchlist_frame.winfo_children():
            if widget != self.watchlist_frame.winfo_children()[0]:  # Keep header
                widget.destroy()
        
        # Get watchlist
        watchlist_items = Watchlist.get_by_user(self.user.user_id)
        
        if not watchlist_items:
            self.show_empty_message()
        else:
            for item in watchlist_items:
                self.create_watchlist_row(item)
    
    def show_empty_message(self):
        """Show empty message"""
        empty_frame = ctk.CTkFrame(self.watchlist_frame, fg_color="transparent")
        empty_frame.pack(expand=True, pady=50)
        
        empty_label = ctk.CTkLabel(
            empty_frame,
            text="Your watchlist is empty",
            font=FONTS['heading'],
            text_color=COLORS['text_tertiary']
        )
        empty_label.pack(pady=10)
        
        instruction_label = ctk.CTkLabel(
            empty_frame,
            text="Add cryptocurrencies to track their prices",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        instruction_label.pack()
    
    def create_watchlist_row(self, item):
        """Create a watchlist row"""
        row_frame = ctk.CTkFrame(
            self.watchlist_frame,
            fg_color=COLORS['bg_tertiary'],
            height=60
        )
        row_frame.pack(fill="x", pady=2)
        
        # Asset name
        name_label = ctk.CTkLabel(
            row_frame,
            text=item['name'],
            font=FONTS['body'],
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        name_label.place(relx=0.10, rely=0.5, anchor="w", relwidth=0.25)
        
        # Symbol
        symbol_label = ctk.CTkLabel(
            row_frame,
            text=item['symbol'],
            font=FONTS['body'],
            text_color=COLORS['accent_primary']
        )
        symbol_label.place(relx=0.25, rely=0.5, anchor="w", relwidth=0.15)
        
        # Current Price
        current_price = item.get('current_price', 0)
        price_label = ctk.CTkLabel(
            row_frame,
            text=f"${current_price:,.2f}" if current_price else "N/A",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        price_label.place(relx=0.40, rely=0.5, anchor="w", relwidth=0.20)
        
        # 24h Change (placeholder - would need historical data)
        change_label = ctk.CTkLabel(
            row_frame,
            text="--",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        change_label.place(relx=0.60, rely=0.5, anchor="w", relwidth=0.15)
        
        # Market Cap Rank
        rank = item.get('market_cap_rank', 'N/A')
        rank_label = ctk.CTkLabel(
            row_frame,
            text=f"#{rank}" if rank != 'N/A' else "N/A",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        rank_label.place(relx=0.75, rely=0.5, anchor="w", relwidth=0.15)
        
        # Remove button
        remove_btn = ctk.CTkButton(
            row_frame,
            text="✕",
            command=lambda: self.remove_from_watchlist(item['crypto_id']),
            width=40,
            height=30,
            fg_color=COLORS['danger'],
            hover_color=COLORS['danger_bg'],
            font=FONTS['body']
        )
        remove_btn.place(relx=0.92, rely=0.5, anchor="center")
    
    def show_add_dialog(self):
        """Show add to watchlist dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add to Watchlist")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f'400x300+{x}+{y}')
        
        main_frame = ctk.CTkFrame(dialog, fg_color=COLORS['bg_primary'])
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Add to Watchlist",
            font=FONTS['title'],
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(0, 30))
        
        # Crypto selection
        crypto_label = ctk.CTkLabel(
            main_frame,
            text="Select Cryptocurrency",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        crypto_label.pack(anchor="w", pady=(0, 5))
        
        # Get all cryptos
        all_cryptos = CryptoCurrency.get_all()
        crypto_names = [f"{c.symbol} - {c.name}" for c in all_cryptos]
        
        crypto_dropdown = ctk.CTkComboBox(
            main_frame,
            values=crypto_names,
            font=FONTS['body']
        )
        crypto_dropdown.pack(fill="x", pady=(0, 30))
        crypto_dropdown.set("Select cryptocurrency")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['border']
        )
        cancel_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="Add",
            command=lambda: self.add_to_watchlist(crypto_dropdown.get(), all_cryptos, dialog),
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover']
        )
        add_btn.pack(side="right", expand=True, fill="x")
    
    def add_to_watchlist(self, selection, cryptos, dialog):
        """Add crypto to watchlist"""
        if selection == "Select cryptocurrency":
            return
        
        symbol = selection.split(" - ")[0]
        crypto = next((c for c in cryptos if c.symbol == symbol), None)
        
        if crypto:
            Watchlist.add(self.user.user_id, crypto.crypto_id)
            dialog.destroy()
            self.load_watchlist()
    
    def remove_from_watchlist(self, crypto_id):
        """Remove crypto from watchlist"""
        Watchlist.remove_by_ids(self.user.user_id, crypto_id)
        self.load_watchlist()
    
    def refresh(self):
        """Refresh watchlist"""
        self.load_watchlist()


if __name__ == "__main__":
    print("Watchlist frame created")