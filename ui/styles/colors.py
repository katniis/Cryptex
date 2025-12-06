"""
Color Scheme for Crypto Portfolio Tracker
Dark theme inspired by modern crypto platforms
"""

# Main Colors
COLORS = {
    # Background colors
    'bg_primary': '#0A0E27',        # Very dark blue (main background)
    'bg_secondary': '#141C3A',      # Dark blue (cards, sidebars)
    'bg_tertiary': '#1E2A4A',       # Medium dark blue (hover states)
    'bg_input': '#1A2238',          # Input fields background
    
    # Text colors
    'text_primary': '#FFFFFF',      # White (main text)
    'text_secondary': '#8B92B0',    # Light gray (secondary text)
    'text_tertiary': '#5A607F',     # Darker gray (disabled text)
    
    # Accent colors
    'accent_primary': '#3B82F6',    # Blue (primary buttons, links)
    'accent_secondary': '#8B5CF6',  # Purple (secondary accents)
    'accent_hover': '#2563EB',      # Darker blue (hover state)
    
    # Status colors
    'success': '#10B981',           # Green (profit, success)
    'success_bg': '#064E3B',        # Dark green background
    'danger': '#EF4444',            # Red (loss, error)
    'danger_bg': '#7F1D1D',         # Dark red background
    'warning': '#F59E0B',           # Orange (warning)
    'warning_bg': '#78350F',        # Dark orange background
    'info': '#06B6D4',              # Cyan (info)
    
    # Border colors
    'border': '#2D3748',            # Dark gray border
    'border_light': '#374151',      # Lighter border
    
    # Special
    'overlay': 'rgba(0, 0, 0, 0.5)', # Semi-transparent overlay
}

# Color shortcuts for common use cases
BG_DARK = COLORS['bg_primary']
BG_CARD = COLORS['bg_secondary']
TEXT_WHITE = COLORS['text_primary']
TEXT_GRAY = COLORS['text_secondary']
BLUE = COLORS['accent_primary']
GREEN = COLORS['success']
RED = COLORS['danger']
PURPLE = COLORS['accent_secondary']

# Gradient colors
GRADIENT_START = '#3B82F6'
GRADIENT_END = '#8B5CF6'