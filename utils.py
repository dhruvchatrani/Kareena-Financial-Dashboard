import pandas as pd


def clean_numeric(val):
    """Strip currency symbols, commas, and handle parenthetical negatives."""
    if pd.isna(val) or val == '':
        return 0.0
    val_str = str(val).replace('₹', '').replace(',', '').strip()
    if val_str.startswith('(') and val_str.endswith(')'):
        val_str = '-' + val_str[1:-1]
    try:
        return float(val_str)
    except ValueError:
        return 0.0
