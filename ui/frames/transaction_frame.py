"""
Transactions Tab Frame
Shows transaction history with filter and edit capabilities
"""

import customtkinter as ctk
from ui.styles.colors import COLORS
from ui.styles.fonts import FONTS
from models.transaction import Transaction
from datetime import datetime


class TransactionFrame(ctk.CTkFrame):
    """
    Transactions tab showing transaction history
    """
    
    def __init__(self, parent, portfolio, on_add_transaction, on_edit_transaction):
        super().__init__(parent, fg_color="transparent")
        
        self.portfolio = portfolio
        self.on_add_transaction = on_add_transaction
        self.on_edit_transaction = on_edit_transaction
        
        self.setup_ui()
        self.load_transactions()
    
    def setup_ui(self):
        """Setup UI elements"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Top bar with filters and add button
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        top_bar.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            top_bar,
            text="Transaction History",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Add Transaction button
        add_btn = ctk.CTkButton(
            top_bar,
            text="+ Add Transaction",
            command=self.on_add_transaction,
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover'],
            font=FONTS['button'],
            height=40
        )
        add_btn.grid(row=0, column=2, sticky="e")
        
        # Filter frame
        filter_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'])
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # Type filter
        type_label = ctk.CTkLabel(
            filter_frame,
            text="Type:",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        type_label.pack(side="left", padx=(15, 5))
        
        self.type_filter = ctk.CTkSegmentedButton(
            filter_frame,
            values=["All", "Buy", "Sell"],
            command=self.apply_filters,
            fg_color=COLORS['bg_tertiary'],
            selected_color=COLORS['accent_primary'],
            selected_hover_color=COLORS['accent_hover']
        )
        self.type_filter.set("All")
        self.type_filter.pack(side="left", padx=10, pady=10)
        
        # Transactions list
        self.transactions_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_secondary']
        )
        self.transactions_frame.grid(row=2, column=0, sticky="nsew")
        
        # Table header
        self.create_header()
    
    def create_header(self):
        """Create transactions table header"""
        header_frame = ctk.CTkFrame(
            self.transactions_frame,
            fg_color=COLORS['bg_tertiary'],
            height=40
        )
        header_frame.pack(fill="x", pady=(0, 5))
        
        headers = [
            ("Type", 0.10),
            ("Date", 0.15),
            ("Asset", 0.15),
            ("Quantity", 0.12),
            ("Price", 0.12),
            ("Fee", 0.10),
            ("Total", 0.12),
            ("Exchange", 0.14)
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
    
    def load_transactions(self):
        """Load transactions"""
        # Clear existing
        for widget in self.transactions_frame.winfo_children():
            if widget != self.transactions_frame.winfo_children()[0]:  # Keep header
                widget.destroy()
        
        # Get transactions
        transactions = Transaction.get_by_portfolio(self.portfolio.portfolio_id)
        
        if not transactions:
            self.show_empty_message()
        else:
            for tx in transactions:
                self.create_transaction_row(tx)
    
    def show_empty_message(self):
        """Show empty message"""
        empty_frame = ctk.CTkFrame(self.transactions_frame, fg_color="transparent")
        empty_frame.pack(expand=True, pady=50)
        
        empty_label = ctk.CTkLabel(
            empty_frame,
            text="No transactions yet",
            font=FONTS['heading'],
            text_color=COLORS['text_tertiary']
        )
        empty_label.pack(pady=10)
        
        instruction_label = ctk.CTkLabel(
            empty_frame,
            text="Add your first transaction to start tracking",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        instruction_label.pack()
    
    def create_transaction_row(self, tx):
        """Create a transaction row"""
        row_frame = ctk.CTkFrame(
            self.transactions_frame,
            fg_color=COLORS['bg_tertiary'],
            height=60
        )
        row_frame.pack(fill="x", pady=2)
        
        # Type badge
        type_color = COLORS['success'] if tx['type'] == 'buy' else COLORS['danger']
        type_label = ctk.CTkLabel(
            row_frame,
            text=tx['type'].upper(),
            font=FONTS['body_small'],
            text_color=type_color,
            fg_color=COLORS['bg_primary'],
            corner_radius=5,
            width=50,
            height=25
        )
        type_label.place(relx=0.02, rely=0.5, anchor="w")
        
        # Date
        date_str = tx['timestamp'].strftime("%b %d, %Y") if tx['timestamp'] else "N/A"
        date_label = ctk.CTkLabel(
            row_frame,
            text=date_str,
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        )
        date_label.place(relx=0.10, rely=0.5, anchor="w", relwidth=0.15)
        
        # Asset
        asset_label = ctk.CTkLabel(
            row_frame,
            text=f"{tx['symbol']}",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        asset_label.place(relx=0.25, rely=0.5, anchor="w", relwidth=0.15)
        
        # Quantity
        qty_label = ctk.CTkLabel(
            row_frame,
            text=f"{tx['quantity']:.4f}",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        qty_label.place(relx=0.40, rely=0.5, anchor="w", relwidth=0.12)
        
        # Price per unit
        price_label = ctk.CTkLabel(
            row_frame,
            text=f"${tx['price_per_unit']:,.2f}",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        price_label.place(relx=0.52, rely=0.5, anchor="w", relwidth=0.12)
        
        # Fee
        fee_label = ctk.CTkLabel(
            row_frame,
            text=f"${tx['fee']:,.2f}" if tx['fee'] else "$0.00",
            font=FONTS['body_small'],
            text_color=COLORS['text_tertiary']
        )
        fee_label.place(relx=0.64, rely=0.5, anchor="w", relwidth=0.10)
        
        # Total
        total = tx['quantity'] * tx['price_per_unit']
        total_label = ctk.CTkLabel(
            row_frame,
            text=f"${total:,.2f}",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        total_label.place(relx=0.74, rely=0.5, anchor="w", relwidth=0.12)
        
        # Exchange
        exchange_text = tx['exchange'] if tx.get('exchange') else "N/A"
        exchange_label = ctk.CTkLabel(
            row_frame,
            text=exchange_text,
            font=FONTS['body_small'],
            text_color=COLORS['text_tertiary']
        )
        exchange_label.place(relx=0.86, rely=0.5, anchor="w", relwidth=0.14)
    
    def apply_filters(self, value):
        """Apply filter based on selected type"""
        # Reload transactions with filter
        self.load_transactions()
    
    def refresh(self):
        """Refresh transactions list"""
        self.load_transactions()


if __name__ == "__main__":
    print("Transaction frame created")