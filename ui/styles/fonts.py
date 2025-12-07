"""
Font Configuration
"""

# Font families
FONT_FAMILY = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"

# Font sizes
FONT_SIZES = {
    'xxl': 32,      # Big titles
    'xl': 24,       # Page titles
    'large': 18,    # Section headers
    'medium': 14,   # Normal text
    'small': 12,    # Small text
    'xs': 10,       # Very small text
}

# Font styles (family, size, weight)
FONTS = {
    'title_large': (FONT_FAMILY, FONT_SIZES['xxl'], 'bold'),
    'title': (FONT_FAMILY, FONT_SIZES['xl'], 'bold'),
    'heading': (FONT_FAMILY, FONT_SIZES['large'], 'bold'),
    'subheading': (FONT_FAMILY, FONT_SIZES['medium'], 'bold'),
    'body': (FONT_FAMILY, FONT_SIZES['medium'], 'normal'),
    'body_small': (FONT_FAMILY, FONT_SIZES['small'], 'normal'),
    'caption': (FONT_FAMILY, FONT_SIZES['xs'], 'normal'),
    'button': (FONT_FAMILY, FONT_SIZES['medium'], 'bold'),
    'mono': (FONT_FAMILY_MONO, FONT_SIZES['small'], 'normal'),
}