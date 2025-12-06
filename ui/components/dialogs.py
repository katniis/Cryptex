"""
Dialogs and Modal Windows
"""

import customtkinter as ctk
from ui.styles.colors import COLORS
from ui.styles.fonts import FONTS
from models.cryptocurrency import CryptoCurrency
from models.transaction import Transaction
from models.price import Price
from datetime import datetime


class AddTransactionDialog(ctk.CTkToplevel):
    """
    Dialog for adding a new transaction
    """
    
    def __init__(self, parent, user, portfolio, on_success):
        super().__init__(parent)
        
        self.user = user
        self.portfolio = portfolio
        self.on_success = on_success
        self.selected_crypto = None
        
        # Window settings
        self.title("Add Transaction")
        self.geometry("500x700")
        self.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def center_window(self):
        """Center window"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Setup UI"""
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'])
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Add Transaction",
            font=FONTS['title'],
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(0, 30))
        
        # Transaction Type
        type_label = ctk.CTkLabel(
            main_frame,
            text="Transaction Type",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        type_label.pack(anchor="w", pady=(0, 5))
        
        self.type_var = ctk.StringVar(value="buy")
        type_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=(0, 20))
        
        buy_radio = ctk.CTkRadioButton(
            type_frame,
            text="Buy",
            variable=self.type_var,
            value="buy",
            font=FONTS['body'],
            fg_color=COLORS['success'],
            hover_color=COLORS['success']
        )
        buy_radio.pack(side="left", padx=(0, 20))
        
        sell_radio = ctk.CTkRadioButton(
            type_frame,
            text="Sell",
            variable=self.type_var,
            value="sell",
            font=FONTS['body'],
            fg_color=COLORS['danger'],
            hover_color=COLORS['danger']
        )
        sell_radio.pack(side="left")
        
        # Cryptocurrency Selection
        crypto_label = ctk.CTkLabel(
            main_frame,
            text="Cryptocurrency",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        crypto_label.pack(anchor="w", pady=(0, 5))
        
        # Get all cryptos
        all_cryptos = CryptoCurrency.get_all()
        crypto_names = [f"{c.symbol} - {c.name}" for c in all_cryptos]
        
        self.crypto_dropdown = ctk.CTkComboBox(
            main_frame,
            values=crypto_names,
            font=FONTS['body'],
            dropdown_font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border'],
            button_color=COLORS['accent_primary'],
            button_hover_color=COLORS['accent_hover'],
            command=self.on_crypto_selected
        )
        self.crypto_dropdown.pack(fill="x", pady=(0, 20))
        self.crypto_dropdown.set("Select cryptocurrency")
        
        # Store cryptos for lookup
        self.cryptos = all_cryptos
        
        # Quantity
        qty_label = ctk.CTkLabel(
            main_frame,
            text="Quantity",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        qty_label.pack(anchor="w", pady=(0, 5))
        
        self.quantity_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="0.00",
            height=45,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.quantity_entry.pack(fill="x", pady=(0, 20))
        self.quantity_entry.bind("<KeyRelease>", self.calculate_total)
        
        # Price per unit
        price_label = ctk.CTkLabel(
            main_frame,
            text="Price per Unit (USD)",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        price_label.pack(anchor="w", pady=(0, 5))
        
        self.price_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Current: $0.00",
            height=45,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.price_entry.pack(fill="x", pady=(0, 20))
        self.price_entry.bind("<KeyRelease>", self.calculate_total)
        
        # Fee (optional)
        fee_label = ctk.CTkLabel(
            main_frame,
            text="Fee (Optional)",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        fee_label.pack(anchor="w", pady=(0, 5))
        
        self.fee_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="0.00",
            height=45,
            font=FONTS['body'],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.fee_entry.pack(fill="x", pady=(0, 20))
        
        # Total
        self.total_label = ctk.CTkLabel(
            main_frame,
            text="Total: $0.00",
            font=FONTS['heading'],
            text_color=COLORS['accent_primary']
        )
        self.total_label.pack(pady=(0, 20))
        
        # Error label
        self.error_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=FONTS['body_small'],
            text_color=COLORS['danger']
        )
        self.error_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            height=45,
            font=FONTS['button'],
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['border']
        )
        cancel_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="Add Transaction",
            command=self.handle_add,
            height=45,
            font=FONTS['button'],
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover']
        )
        add_btn.pack(side="right", expand=True, fill="x")
    
    def on_crypto_selected(self, choice):
        """Handle cryptocurrency selection"""
        # Find the selected crypto
        symbol = choice.split(" - ")[0]
        self.selected_crypto = next((c for c in self.cryptos if c.symbol == symbol), None)
        
        if self.selected_crypto:
            # Get latest price
            latest_price = Price.get_latest(self.selected_crypto.crypto_id)
            if latest_price:
                self.price_entry.delete(0, 'end')
                self.price_entry.insert(0, str(latest_price.price))
                self.calculate_total()
    
    def calculate_total(self, event=None):
        """Calculate and display total"""
        try:
            quantity = float(self.quantity_entry.get() or 0)
            price = float(self.price_entry.get() or 0)
            fee = float(self.fee_entry.get() or 0)
            
            total = (quantity * price) + fee
            self.total_label.configure(text=f"Total: ${total:,.2f}")
        except ValueError:
            self.total_label.configure(text="Total: $0.00")
    
    def handle_add(self):
        """Handle add transaction"""
        # Validate
        if not self.selected_crypto:
            self.show_error("Please select a cryptocurrency")
            return
        
        try:
            quantity = float(self.quantity_entry.get())
            price = float(self.price_entry.get())
            fee = float(self.fee_entry.get() or 0)
        except ValueError:
            self.show_error("Please enter valid numbers")
            return
        
        if quantity <= 0:
            self.show_error("Quantity must be greater than 0")
            return
        
        if price <= 0:
            self.show_error("Price must be greater than 0")
            return
        
        # Create transaction
        transaction = Transaction.create(
            user_id=self.user.user_id,
            portfolio_id=self.portfolio.portfolio_id,
            crypto_id=self.selected_crypto.crypto_id,
            transaction_type=self.type_var.get(),
            quantity=quantity,
            price_per_unit=price,
            fee=fee
        )
        
        if transaction:
            self.on_success()
            self.destroy()
        else:
            self.show_error("Failed to create transaction. Check if you have enough to sell.")
    
    def show_error(self, message):
        """Show error message"""
        self.error_label.configure(text=message)


if __name__ == "__main__":
    print("Dialogs created")