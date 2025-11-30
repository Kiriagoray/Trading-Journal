"""
Instrument data for lot size calculator
Contains pip/point values for all trading instruments
"""

# Instrument data - pip values are in USD per standard lot
INSTRUMENTS = {
    # Major Forex Pairs
    'EURUSD': {'name': 'EUR/USD', 'pip_value': 10.0, 'pip_decimal': 4, 'type': 'forex'},
    'GBPUSD': {'name': 'GBP/USD', 'pip_value': 10.0, 'pip_decimal': 4, 'type': 'forex'},
    'USDJPY': {'name': 'USD/JPY', 'pip_value': 9.09, 'pip_decimal': 2, 'type': 'forex'},
    'USDCHF': {'name': 'USD/CHF', 'pip_value': 10.5, 'pip_decimal': 4, 'type': 'forex'},
    'AUDUSD': {'name': 'AUD/USD', 'pip_value': 10.0, 'pip_decimal': 4, 'type': 'forex'},
    'NZDUSD': {'name': 'NZD/USD', 'pip_value': 10.0, 'pip_decimal': 4, 'type': 'forex'},
    'USDCAD': {'name': 'USD/CAD', 'pip_value': 7.5, 'pip_decimal': 4, 'type': 'forex'},
    
    # Cross Pairs
    'EURGBP': {'name': 'EUR/GBP', 'pip_value': 10.0, 'pip_decimal': 4, 'type': 'forex'},
    'EURJPY': {'name': 'EUR/JPY', 'pip_value': 9.09, 'pip_decimal': 2, 'type': 'forex'},
    'GBPJPY': {'name': 'GBP/JPY', 'pip_value': 9.09, 'pip_decimal': 2, 'type': 'forex'},
    'AUDJPY': {'name': 'AUD/JPY', 'pip_value': 9.09, 'pip_decimal': 2, 'type': 'forex'},
    'NZDJPY': {'name': 'NZD/JPY', 'pip_value': 9.09, 'pip_decimal': 2, 'type': 'forex'},
    'EURAUD': {'name': 'EUR/AUD', 'pip_value': 10.0, 'pip_decimal': 4, 'type': 'forex'},
    'EURCAD': {'name': 'EUR/CAD', 'pip_value': 7.5, 'pip_decimal': 4, 'type': 'forex'},
    'GBPAUD': {'name': 'GBP/AUD', 'pip_value': 10.0, 'pip_decimal': 4, 'type': 'forex'},
    'GBPCAD': {'name': 'GBP/CAD', 'pip_value': 7.5, 'pip_decimal': 4, 'type': 'forex'},
    'AUDCAD': {'name': 'AUD/CAD', 'pip_value': 7.5, 'pip_decimal': 4, 'type': 'forex'},
    'AUDNZD': {'name': 'AUD/NZD', 'pip_value': 10.0, 'pip_decimal': 4, 'type': 'forex'},
    'NZDCAD': {'name': 'NZD/CAD', 'pip_value': 7.5, 'pip_decimal': 4, 'type': 'forex'},
    
    # Major Indices (contract size per point)
    'US30': {'name': 'US30 (Dow Jones)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'index', 'contract_size': 1},
    'NAS100': {'name': 'NAS100 (NASDAQ)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'index', 'contract_size': 1},
    'SPX500': {'name': 'SPX500 (S&P 500)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'index', 'contract_size': 1},
    'DE30': {'name': 'DE30 (DAX)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'index', 'contract_size': 1},
    'UK100': {'name': 'UK100 (FTSE)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'index', 'contract_size': 1},
    'FR40': {'name': 'FR40 (CAC 40)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'index', 'contract_size': 1},
    'JP225': {'name': 'JP225 (Nikkei)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'index', 'contract_size': 1},
    'AUS200': {'name': 'AUS200 (ASX)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'index', 'contract_size': 1},
    'EU50': {'name': 'EU50 (Euro Stoxx)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'index', 'contract_size': 1},
    
    # Commodities
    'XAUUSD': {'name': 'XAU/USD (Gold)', 'pip_value': 100.0, 'pip_decimal': 2, 'type': 'commodity'},  # $1 per 0.01 move
    'XAGUSD': {'name': 'XAG/USD (Silver)', 'pip_value': 50.0, 'pip_decimal': 3, 'type': 'commodity'},  # $0.50 per 0.01 move
    'USOIL': {'name': 'USOIL (WTI Crude)', 'pip_value': 10.0, 'pip_decimal': 2, 'type': 'commodity'},  # $10 per $0.01 move
    'UKOIL': {'name': 'UKOIL (Brent Crude)', 'pip_value': 10.0, 'pip_decimal': 2, 'type': 'commodity'},
    'NATGAS': {'name': 'NATGAS (Natural Gas)', 'pip_value': 10.0, 'pip_decimal': 3, 'type': 'commodity'},
    'COPPER': {'name': 'COPPER', 'pip_value': 25.0, 'pip_decimal': 3, 'type': 'commodity'},  # $25 per 0.01 move
    'XPTUSD': {'name': 'XPT/USD (Platinum)', 'pip_value': 100.0, 'pip_decimal': 2, 'type': 'commodity'},
    'XPDUSD': {'name': 'XPD/USD (Palladium)', 'pip_value': 100.0, 'pip_decimal': 2, 'type': 'commodity'},
    
    # Optional Cryptocurrencies
    'BTCUSD': {'name': 'BTC/USD (Bitcoin)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'crypto'},
    'ETHUSD': {'name': 'ETH/USD (Ethereum)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'crypto'},
    'LTCUSD': {'name': 'LTC/USD (Litecoin)', 'pip_value': 1.0, 'pip_decimal': 2, 'type': 'crypto'},
    'XRPUSD': {'name': 'XRP/USD (Ripple)', 'pip_value': 1.0, 'pip_decimal': 4, 'type': 'crypto'},
    
    # Additional Forex Pairs
    'EURCHF': {'name': 'EUR/CHF', 'pip_value': 10.5, 'pip_decimal': 4, 'type': 'forex'},
    'GBPCHF': {'name': 'GBP/CHF', 'pip_value': 10.5, 'pip_decimal': 4, 'type': 'forex'},
    'AUDCHF': {'name': 'AUD/CHF', 'pip_value': 10.5, 'pip_decimal': 4, 'type': 'forex'},
    'USDTRY': {'name': 'USD/TRY', 'pip_value': 0.1, 'pip_decimal': 4, 'type': 'forex'},
    'USDZAR': {'name': 'USD/ZAR', 'pip_value': 0.7, 'pip_decimal': 4, 'type': 'forex'},
    'USDMXN': {'name': 'USD/MXN', 'pip_value': 0.5, 'pip_decimal': 4, 'type': 'forex'},
}


def get_instrument_choices():
    """Get list of tuples for form choices"""
    return [(code, data['name']) for code, data in sorted(INSTRUMENTS.items(), key=lambda x: x[1]['name'])]


def get_instrument_data(instrument_code):
    """Get instrument data by code"""
    return INSTRUMENTS.get(instrument_code.upper())


def get_pip_value(instrument_code):
    """Get pip value for an instrument"""
    data = get_instrument_data(instrument_code)
    if data:
        return data['pip_value']
    return 10.00  # Default for unknown instruments


def search_instruments(query):
    """Search instruments by code or name"""
    query = query.upper().strip()
    results = []
    for code, data in INSTRUMENTS.items():
        if query in code or query in data['name'].upper():
            results.append({
                'code': code,
                'name': data['name'],
                'type': data['type']
            })
    return results

