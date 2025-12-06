"""
Overview Tab Frame
Shows portfolio statistics, charts, and asset list
"""

import customtkinter as ctk
from ui.styles.colors import COLORS
from ui.styles.fonts import FONTS
from models.portfolio_holding import PortfolioHolding
from models.price import Price


class OverviewFrame(ctk.CTkFrame):
    """
    Overview tab showing portfolio summary and assets
    """
    
    def __init__(self, parent, portfolio, on_add_transaction):
        super().__init__(parent, fg_color="transparent")
        
        self.portfolio = portfolio
        self.on_add_transaction = on_add_transaction
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup UI elements"""
        
        # Main scrollable container
        main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_scroll.pack(fill="both", expand=True)
        
        # Configure grid inside scrollable frame
        main_scroll.grid_columnconfigure(0, weight=2)
        main_scroll.grid_columnconfigure(1, weight=1)
        
        # Stats cards row
        stats_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        stats_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Configure stats grid
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Total Value Card
        self.total_value_card = self.create_stat_card(
            stats_frame, "Total Value", "$0.00", COLORS['text_primary']
        )
        self.total_value_card.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        # Total Invested Card
        self.total_invested_card = self.create_stat_card(
            stats_frame, "Total Invested", "$0.00", COLORS['text_secondary']
        )
        self.total_invested_card.grid(row=0, column=1, padx=10, sticky="ew")
        
        # Profit/Loss Card
        self.profit_loss_card = self.create_stat_card(
            stats_frame, "Profit/Loss", "$0.00", COLORS['success']
        )
        self.profit_loss_card.grid(row=0, column=2, padx=10, sticky="ew")
        
        # Holdings Count Card
        self.holdings_count_card = self.create_stat_card(
            stats_frame, "Assets", "0", COLORS['accent_primary']
        )
        self.holdings_count_card.grid(row=0, column=3, padx=(10, 0), sticky="ew")
        
        # Charts row
        charts_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        charts_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        charts_frame.grid_columnconfigure(0, weight=2)
        charts_frame.grid_columnconfigure(1, weight=1)
        
        # History Chart (left)
        self.history_chart_frame = ctk.CTkFrame(
            charts_frame,
            fg_color=COLORS['bg_secondary'],
            height=300
        )
        self.history_chart_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.history_chart_frame.grid_propagate(False)
        
        # Pie Chart (right)
        self.pie_chart_frame = ctk.CTkFrame(
            charts_frame,
            fg_color=COLORS['bg_secondary'],
            height=300
        )
        self.pie_chart_frame.grid(row=0, column=1, sticky="ew")
        self.pie_chart_frame.grid_propagate(False)
        
        # Add Transaction Button
        add_btn_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        add_btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        add_transaction_btn = ctk.CTkButton(
            add_btn_frame,
            text="+ Add Transaction",
            command=self.on_add_transaction,
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_hover'],
            font=FONTS['button'],
            height=40
        )
        add_transaction_btn.pack(side="right")
        
        # Assets List
        assets_label = ctk.CTkLabel(
            main_scroll,
            text="Your Assets",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        )
        assets_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Assets table frame (NOT scrollable, inside the main scroll)
        self.assets_frame = ctk.CTkFrame(
            main_scroll,
            fg_color=COLORS['bg_secondary']
        )
        self.assets_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Table header
        self.create_assets_header()
    
    def create_stat_card(self, parent, title, value, value_color):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], height=100)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        )
        title_label.pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=FONTS['heading'],
            text_color=value_color
        )
        value_label.pack(pady=(0, 15))
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def create_assets_header(self):
        """Create assets table header"""
        header_frame = ctk.CTkFrame(
            self.assets_frame,
            fg_color=COLORS['bg_tertiary'],
            height=40
        )
        header_frame.pack(fill="x", pady=(0, 5))
        
        # Header columns
        headers = [
            ("Asset", 0.25),
            ("Quantity", 0.15),
            ("Avg Price", 0.15),
            ("Current Price", 0.15),
            ("Value", 0.15),
            ("Profit/Loss", 0.15)
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
    
    def load_data(self):
        """Load portfolio data"""
        # Get holdings
        holdings = PortfolioHolding.get_by_portfolio(self.portfolio.portfolio_id)
        
        # Update stats
        total_value = self.portfolio.get_total_value()
        total_invested = self.portfolio.get_total_invested()
        profit_loss = self.portfolio.get_profit_loss()
        
        self.total_value_card.value_label.configure(text=f"${total_value:,.2f}")
        self.total_invested_card.value_label.configure(text=f"${total_invested:,.2f}")
        
        pl_amount = profit_loss['amount']
        pl_percent = profit_loss['percentage']
        pl_color = COLORS['success'] if pl_amount >= 0 else COLORS['danger']
        pl_text = f"${abs(pl_amount):,.2f} ({pl_percent:+.2f}%)"
        
        self.profit_loss_card.value_label.configure(text=pl_text, text_color=pl_color)
        self.holdings_count_card.value_label.configure(text=str(len(holdings)))
        
        # Update charts
        self.update_charts(holdings)
        
        # Clear existing assets
        for widget in self.assets_frame.winfo_children():
            if widget != self.assets_frame.winfo_children()[0]:  # Keep header
                widget.destroy()
        
        # Show assets or empty message
        if not holdings:
            self.show_empty_message()
        else:
            for holding in holdings:
                self.create_asset_row(holding)
    
    def update_charts(self, holdings):
        """Update chart displays"""
        from charts.portfolio_charts import PortfolioCharts
        from models.transaction import Transaction
        
        # Clear existing charts
        for widget in self.history_chart_frame.winfo_children():
            widget.destroy()
        for widget in self.pie_chart_frame.winfo_children():
            widget.destroy()
        
        # Get transaction history
        transactions = Transaction.get_by_portfolio(self.portfolio.portfolio_id)
        
        # Create history chart
        history_canvas = PortfolioCharts.create_portfolio_history_chart(
            self.history_chart_frame,
            transactions
        )
        history_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create pie chart
        pie_canvas = PortfolioCharts.create_allocation_pie_chart(
            self.pie_chart_frame,
            holdings
        )
        pie_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def show_empty_message(self):
        """Show message when no assets"""
        empty_frame = ctk.CTkFrame(self.assets_frame, fg_color="transparent")
        empty_frame.pack(expand=True, pady=50)
        
        empty_label = ctk.CTkLabel(
            empty_frame,
            text="No assets yet",
            font=FONTS['heading'],
            text_color=COLORS['text_tertiary']
        )
        empty_label.pack(pady=10)
        
        instruction_label = ctk.CTkLabel(
            empty_frame,
            text="Add your first transaction to get started",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        instruction_label.pack()
    
    def create_asset_row(self, holding):
        """Create an asset row"""
        row_frame = ctk.CTkFrame(
            self.assets_frame,
            fg_color=COLORS['bg_tertiary'],
            height=60
        )
        row_frame.pack(fill="x", pady=2)
        
        # Get current price
        current_price = 0
        latest_price = Price.get_latest(holding['crypto_id'])
        if latest_price:
            current_price = float(latest_price.price)
        
        # Calculate values
        quantity = float(holding['quantity'])
        avg_price = float(holding['average_buy_price'])
        current_value = quantity * current_price
        profit_loss = current_value - float(holding['total_invested'])
        profit_loss_percent = (profit_loss / float(holding['total_invested']) * 100) if holding['total_invested'] > 0 else 0
        
        # Asset name with symbol
        asset_label = ctk.CTkLabel(
            row_frame,
            text=f" {holding['symbol']} • {holding['name']}",
            font=FONTS['body'],
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        asset_label.place(relx=0.10, rely=0.5, anchor="w", relwidth=0.25)
        
        # Quantity
        qty_label = ctk.CTkLabel(
            row_frame,
            text=f"{quantity:.4f}",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        qty_label.place(relx=0.25, rely=0.5, anchor="w", relwidth=0.15)
        
        # Average Price
        avg_label = ctk.CTkLabel(
            row_frame,
            text=f"${avg_price:,.2f}",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        avg_label.place(relx=0.40, rely=0.5, anchor="w", relwidth=0.15)
        
        # Current Price
        curr_label = ctk.CTkLabel(
            row_frame,
            text=f"${current_price:,.2f}",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        curr_label.place(relx=0.55, rely=0.5, anchor="w", relwidth=0.15)
        
        # Value
        value_label = ctk.CTkLabel(
            row_frame,
            text=f"${current_value:,.2f}",
            font=FONTS['body'],
            text_color=COLORS['text_primary']
        )
        value_label.place(relx=0.70, rely=0.5, anchor="w", relwidth=0.15)
        
        # Profit/Loss
        pl_color = COLORS['success'] if profit_loss >= 0 else COLORS['danger']
        pl_text = f"${abs(profit_loss):,.2f}\n({profit_loss_percent:+.2f}%)"
        
        pl_label = ctk.CTkLabel(
            row_frame,
            text=pl_text,
            font=FONTS['body_small'],
            text_color=pl_color
        )
        pl_label.place(relx=0.85, rely=0.5, anchor="w", relwidth=0.15)
    
    def refresh(self):
        """Refresh data"""
        self.load_data()


if __name__ == "__main__":
    # Test
    print("Overview frame created")