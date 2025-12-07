"""
Portfolio Charts
Matplotlib charts for portfolio visualization
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from ui.styles.colors import COLORS
import numpy as np


class PortfolioCharts:
    """
    Chart components for portfolio visualization
    """
    
    @staticmethod
    def create_allocation_pie_chart(parent, holdings_data):
        """
        Create a pie chart showing portfolio allocation
        
        Args:
            parent: Parent widget
            holdings_data: List of holdings with quantity and value
            
        Returns:
            FigureCanvasTkAgg: Canvas with the chart
        """
        # Create figure with dark background - SMALLER SIZE
        fig = Figure(figsize=(4, 3.5), facecolor='#0A0E27', dpi=80)
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0A0E27')
        
        if not holdings_data or len(holdings_data) == 0:
            # Show empty state
            ax.text(0.5, 0.5, 'No data to display', 
                   ha='center', va='center',
                   fontsize=14, color='#8B92B0',
                   transform=ax.transAxes)
            ax.axis('off')
        else:
            # Prepare data
            labels = []
            sizes = []
            colors_list = []
            
            # Color palette
            color_palette = [
                '#3B82F6',  # Blue
                '#10B981',  # Green
                '#F59E0B',  # Orange
                '#8B5CF6',  # Purple
                '#EF4444',  # Red
                '#06B6D4',  # Cyan
                '#EC4899',  # Pink
                '#84CC16',  # Lime
            ]
            
            for i, holding in enumerate(holdings_data):
                symbol = holding.get('symbol', 'Unknown')
                quantity = float(holding.get('quantity', 0))
                avg_price = float(holding.get('average_buy_price', 0))
                value = quantity * avg_price
                
                if value > 0:
                    labels.append(symbol)
                    sizes.append(value)
                    colors_list.append(color_palette[i % len(color_palette)])
            
            if sizes:
                # Create pie chart
                wedges, texts, autotexts = ax.pie(
                    sizes,
                    labels=None,  # We'll add custom legend
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=colors_list,
                    textprops={'color': 'white', 'fontsize': 10}
                )
                
                # Equal aspect ratio ensures circular pie
                ax.axis('equal')
                
                # Create custom legend
                legend_labels = [f'{label}: ${size:,.0f}' for label, size in zip(labels, sizes)]
                ax.legend(
                    wedges, 
                    legend_labels,
                    loc="center left",
                    bbox_to_anchor=(1, 0, 0.5, 1),
                    frameon=False,
                    fontsize=8,
                    labelcolor='white'
                )
            else:
                ax.text(0.5, 0.5, 'No data to display', 
                       ha='center', va='center',
                       fontsize=14, color='#8B92B0',
                       transform=ax.transAxes)
                ax.axis('off')
        
        # Add title
        ax.set_title('Portfolio Allocation', 
                    color='white', 
                    fontsize=12, 
                    fontweight='bold',
                    pad=10)
        
        fig.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        
        return canvas
    
    @staticmethod
    def create_portfolio_history_chart(parent, transactions_data):
        """
        Create a line chart showing portfolio value over time
        
        Args:
            parent: Parent widget
            transactions_data: List of transactions with dates and values
            
        Returns:
            FigureCanvasTkAgg: Canvas with the chart
        """
        # Create figure with dark background - SMALLER SIZE
        fig = Figure(figsize=(8, 3.5), facecolor='#0A0E27', dpi=80)
        ax = fig.add_subplot(111)
        ax.set_facecolor('#141C3A')
        
        if not transactions_data or len(transactions_data) == 0:
            # Show empty state
            ax.text(0.5, 0.5, 'No transaction history', 
                   ha='center', va='center',
                   fontsize=14, color='#8B92B0',
                   transform=ax.transAxes)
            ax.axis('off')
        else:
            # Sort transactions by date
            sorted_tx = sorted(transactions_data, key=lambda x: x.get('timestamp'))
            
            # Calculate cumulative invested value over time
            dates = []
            values = []
            cumulative = 0
            
            for tx in sorted_tx:
                date = tx.get('timestamp')
                quantity = float(tx.get('quantity', 0))
                price = float(tx.get('price_per_unit', 0))
                tx_type = tx.get('type', 'buy')
                
                if tx_type == 'buy':
                    cumulative += quantity * price
                else:
                    cumulative -= quantity * price
                
                dates.append(date)
                values.append(cumulative)
            
            if dates and values:
                # Plot line
                ax.plot(dates, values, 
                       color='#3B82F6', 
                       linewidth=2.5,
                       marker='o',
                       markersize=4,
                       markerfacecolor='#3B82F6',
                       markeredgecolor='white',
                       markeredgewidth=1)
                
                # Fill area under curve
                ax.fill_between(dates, values, 
                               alpha=0.3, 
                               color='#3B82F6')
                
                # Styling
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#2D3748')
                ax.spines['bottom'].set_color('#2D3748')
                
                ax.tick_params(colors='#8B92B0', labelsize=8)
                ax.grid(True, alpha=0.1, color='#8B92B0', linestyle='--')
                
                # Format y-axis as currency
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                
                # Format x-axis dates with time
                import matplotlib.dates as mdates
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                
                # Rotate date labels
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
                
                # Add title
                ax.set_title('Portfolio Value History', 
                           color='white', 
                           fontsize=12, 
                           fontweight='bold',
                           pad=10)
                ax.set_xlabel('Date', color='#8B92B0', fontsize=9)
                ax.set_ylabel('Total Invested ($)', color='#8B92B0', fontsize=9)
            else:
                ax.text(0.5, 0.5, 'No data to display', 
                       ha='center', va='center',
                       fontsize=14, color='#8B92B0',
                       transform=ax.transAxes)
                ax.axis('off')
        
        fig.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        
        return canvas
    
    @staticmethod
    def create_performance_chart(parent, holdings_data):
        """
        Create a bar chart showing performance by asset
        
        Args:
            parent: Parent widget
            holdings_data: List of holdings with profit/loss data
            
        Returns:
            FigureCanvasTkAgg: Canvas with the chart
        """
        # Create figure
        fig = Figure(figsize=(8, 4), facecolor='#0A0E27')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#141C3A')
        
        if not holdings_data or len(holdings_data) == 0:
            ax.text(0.5, 0.5, 'No data to display', 
                   ha='center', va='center',
                   fontsize=14, color='#8B92B0',
                   transform=ax.transAxes)
            ax.axis('off')
        else:
            # Prepare data
            symbols = []
            returns = []
            colors = []
            
            for holding in holdings_data:
                symbol = holding.get('symbol', 'Unknown')
                quantity = float(holding.get('quantity', 0))
                avg_price = float(holding.get('average_buy_price', 0))
                total_invested = float(holding.get('total_invested', 0))
                
                # Calculate return percentage
                if total_invested > 0:
                    current_value = quantity * avg_price  # This should use current price
                    return_pct = ((current_value - total_invested) / total_invested) * 100
                    
                    symbols.append(symbol)
                    returns.append(return_pct)
                    colors.append('#10B981' if return_pct >= 0 else '#EF4444')
            
            if symbols:
                # Create horizontal bar chart
                y_pos = np.arange(len(symbols))
                ax.barh(y_pos, returns, color=colors, alpha=0.8)
                
                ax.set_yticks(y_pos)
                ax.set_yticklabels(symbols)
                ax.invert_yaxis()  # Labels read top-to-bottom
                
                # Styling
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#2D3748')
                ax.spines['bottom'].set_color('#2D3748')
                
                ax.tick_params(colors='#8B92B0', labelsize=10)
                ax.grid(True, alpha=0.1, color='#8B92B0', linestyle='--', axis='x')
                
                # Add vertical line at 0
                ax.axvline(0, color='#8B92B0', linewidth=1, linestyle='-', alpha=0.3)
                
                # Format x-axis
                ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.1f}%'))
                
                ax.set_title('Performance by Asset', 
                           color='white', 
                           fontsize=14, 
                           fontweight='bold',
                           pad=15)
                ax.set_xlabel('Return (%)', color='#8B92B0', fontsize=10)
        
        fig.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        
        return canvas


if __name__ == "__main__":
    print("Chart components created")