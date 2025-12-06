"""
Alerts Tab Frame
Manage price alerts for cryptocurrencies
"""

import customtkinter as ctk
from ui.styles.colors import COLORS
from ui.styles.fonts import FONTS
from models.alert import Alert
from models.cryptocurrency import CryptoCurrency


class AlertsFrame(ctk.CTkFrame):
    """
    Alerts tab for price notifications
    """
    
    def __init__(self, parent, user):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        
        self.setup_ui()
        self.load_alerts()
    
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
            text="Price Alerts",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Create Alert button
        add_btn = ctk.CTkButton(
            top_bar,
            text="+ Create Alert",
            command=self.show_create_dialog,
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover'],
            font=FONTS['button'],
            height=40
        )
        add_btn.grid(row=0, column=2, sticky="e")
        
        # Alerts list frame
        self.alerts_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_secondary']
        )
        self.alerts_frame.grid(row=1, column=0, sticky="nsew")
        
        # Table header
        self.create_header()
    
    def create_header(self):
        """Create alerts table header"""
        header_frame = ctk.CTkFrame(
            self.alerts_frame,
            fg_color=COLORS['bg_tertiary'],
            height=40
        )
        header_frame.pack(fill="x", pady=(0, 5))
        
        headers = [
            ("Asset", 0.20),
            ("Condition", 0.15),
            ("Target Price", 0.15),
            ("Current Price", 0.15),
            ("Status", 0.15),
            ("Actions", 0.20)
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
    
    def load_alerts(self):
        """Load alerts"""
        # Clear existing
        for widget in self.alerts_frame.winfo_children():
            if widget != self.alerts_frame.winfo_children()[0]:  # Keep header
                widget.destroy()
        
        # Get alerts
        alerts = Alert.get_by_user(self.user.user_id, active_only=False)
        
        if not alerts:
            self.show_empty_message()
        else:
            for alert in alerts:
                self.create_alert_row(alert)
    
    def show_empty_message(self):
        """Show empty message"""
        empty_frame = ctk.CTkFrame(self.alerts_frame, fg_color="transparent")
        empty_frame.pack(expand=True, pady=50)
        
        empty_label = ctk.CTkLabel(
            empty_frame,
            text="No alerts set",
            font=FONTS['heading'],
            text_color=COLORS['text_tertiary']
        )
        empty_label.pack(pady=10)
        
        instruction_label = ctk.CTkLabel(
            empty_frame,
            text="Create alerts to get notified when prices change",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        instruction_label.pack()
    
    def create_alert_row(self, alert):
        """Create an alert row"""
        row_frame = ctk.CTkFrame(
            self.alerts_frame,
            fg_color=COLORS['bg_tertiary'],
            height=60
        )
        row_frame.pack(fill="x", pady=2)
        
        # Asset
        asset_label = ctk.CTkLabel(
            row_frame,
            text=f"{alert['symbol']} • {alert['name']}",
            font=FONTS['body'],
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        asset_label.place(relx=0, rely=0.5, anchor="w", relwidth=0.20)
        
        # Condition
        condition_text = f"Price {alert['condition']}"
        condition_label = ctk.CTkLabel(
            row_frame,
            text=condition_text,
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        condition_label.place(relx=0.20, rely=0.5, anchor="w", relwidth=0.15)
        
        # Target Price
        target_label = ctk.CTkLabel(
            row_frame,
            text=f"${alert['target_price']:,.2f}",
            font=FONTS['body'],
            text_color=COLORS['accent_primary']
        )
        target_label.place(relx=0.35, rely=0.5, anchor="w", relwidth=0.15)
        
        # Current Price
        current_price = alert.get('current_price', 0)
        curr_label = ctk.CTkLabel(
            row_frame,
            text=f"${current_price:,.2f}" if current_price else "N/A",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        curr_label.place(relx=0.50, rely=0.5, anchor="w", relwidth=0.15)
        
        # Status
        is_active = alert['is_active']
        is_triggered = False
        if current_price and is_active:
            if alert['condition'] == 'above':
                is_triggered = current_price >= alert['target_price']
            else:
                is_triggered = current_price <= alert['target_price']
        
        if is_triggered:
            status_text = "🔔 Triggered"
            status_color = COLORS['warning']
        elif is_active:
            status_text = "✓ Active"
            status_color = COLORS['success']
        else:
            status_text = "○ Inactive"
            status_color = COLORS['text_tertiary']
        
        status_label = ctk.CTkLabel(
            row_frame,
            text=status_text,
            font=FONTS['body_small'],
            text_color=status_color
        )
        status_label.place(relx=0.65, rely=0.5, anchor="w", relwidth=0.15)
        
        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.place(relx=0.80, rely=0.5, anchor="w", relwidth=0.20)
        
        # Toggle button
        toggle_text = "Disable" if is_active else "Enable"
        toggle_btn = ctk.CTkButton(
            actions_frame,
            text=toggle_text,
            command=lambda: self.toggle_alert(alert),
            width=70,
            height=30,
            fg_color=COLORS['bg_primary'],
            hover_color=COLORS['border'],
            font=FONTS['body_small']
        )
        toggle_btn.pack(side="left", padx=(0, 5))
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="✕",
            command=lambda: self.delete_alert(alert['alert_id']),
            width=30,
            height=30,
            fg_color=COLORS['danger'],
            hover_color=COLORS['danger_bg'],
            font=FONTS['body']
        )
        delete_btn.pack(side="left")
    
    def show_create_dialog(self):
        """Show create alert dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create Alert")
        dialog.geometry("450x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f'450x500+{x}+{y}')
        
        main_frame = ctk.CTkFrame(dialog, fg_color=COLORS['bg_primary'])
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Create Price Alert",
            font=FONTS['title'],
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(0, 30))
        
        # Crypto selection
        crypto_label = ctk.CTkLabel(
            main_frame,
            text="Cryptocurrency",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        crypto_label.pack(anchor="w", pady=(0, 5))
        
        all_cryptos = CryptoCurrency.get_all()
        crypto_names = [f"{c.symbol} - {c.name}" for c in all_cryptos]
        
        crypto_dropdown = ctk.CTkComboBox(
            main_frame,
            values=crypto_names,
            font=FONTS['body']
        )
        crypto_dropdown.pack(fill="x", pady=(0, 20))
        crypto_dropdown.set("Select cryptocurrency")
        
        # Condition
        condition_label = ctk.CTkLabel(
            main_frame,
            text="Alert When Price Goes",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        condition_label.pack(anchor="w", pady=(0, 5))
        
        condition_var = ctk.StringVar(value="above")
        condition_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        condition_frame.pack(fill="x", pady=(0, 20))
        
        above_radio = ctk.CTkRadioButton(
            condition_frame,
            text="Above",
            variable=condition_var,
            value="above",
            font=FONTS['body']
        )
        above_radio.pack(side="left", padx=(0, 20))
        
        below_radio = ctk.CTkRadioButton(
            condition_frame,
            text="Below",
            variable=condition_var,
            value="below",
            font=FONTS['body']
        )
        below_radio.pack(side="left")
        
        # Target Price
        price_label = ctk.CTkLabel(
            main_frame,
            text="Target Price (USD)",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        price_label.pack(anchor="w", pady=(0, 5))
        
        price_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="0.00",
            height=45,
            font=FONTS['body']
        )
        price_entry.pack(fill="x", pady=(0, 30))
        
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
        
        create_btn = ctk.CTkButton(
            button_frame,
            text="Create Alert",
            command=lambda: self.create_alert(
                crypto_dropdown.get(),
                all_cryptos,
                condition_var.get(),
                price_entry.get(),
                dialog
            ),
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover']
        )
        create_btn.pack(side="right", expand=True, fill="x")
    
    def create_alert(self, selection, cryptos, condition, target_price, dialog):
        """Create new alert"""
        if selection == "Select cryptocurrency":
            return
        
        try:
            target = float(target_price)
        except ValueError:
            return
        
        symbol = selection.split(" - ")[0]
        crypto = next((c for c in cryptos if c.symbol == symbol), None)
        
        if crypto and target > 0:
            Alert.create(
                user_id=self.user.user_id,
                crypto_id=crypto.crypto_id,
                condition=condition,
                target_price=target
            )
            dialog.destroy()
            self.load_alerts()
    
    def toggle_alert(self, alert):
        """Toggle alert active status"""
        alert_obj = Alert.get_by_id(alert['alert_id'])
        if alert_obj:
            if alert['is_active']:
                alert_obj.deactivate()
            else:
                alert_obj.activate()
            self.load_alerts()
    
    def delete_alert(self, alert_id):
        """Delete alert"""
        alert = Alert.get_by_id(alert_id)
        if alert:
            alert.delete()
            self.load_alerts()
    
    def refresh(self):
        """Refresh alerts"""
        self.load_alerts()


if __name__ == "__main__":
    print("Alerts frame created")