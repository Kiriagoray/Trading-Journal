"""
Utility functions for getting choice options from Configuration models
"""
from .models import ChoiceOption


def get_choices(category_name, fallback_choices=None):
    """
    Get choices from ChoiceOption model or fallback to hardcoded choices
    
    Args:
        category_name: The category name (e.g., 'session', 'market_condition')
        fallback_choices: List of tuples as fallback if no config exists
        
    Returns:
        List of tuples (value, label) for form choices
    """
    choices = ChoiceOption.get_choices_for_category(category_name)
    
    if choices:
        return choices
    
    # Fallback to hardcoded choices if configuration doesn't exist
    if fallback_choices:
        return fallback_choices
    
    return []


# Helper functions for common categories
def get_session_choices():
    return get_choices('session', [
        ('Asian', 'Asian'),
        ('London', 'London'),
        ('NewYork', 'New York'),
    ])


def get_bias_choices():
    return get_choices('bias', [
        ('bullish', 'Bullish'),
        ('bearish', 'Bearish'),
    ])


def get_market_condition_choices():
    return get_choices('market_condition', [
        ('Trending Up', 'Trending Up'),
        ('Trending Down', 'Trending Down'),
        ('Consolidating', 'Consolidating'),
    ])


def get_liquidity_analysis_choices():
    return get_choices('liquidity_analysis', [
        ('buyside swept', 'Buyside Swept'),
        ('sellside swept', 'Sellside Swept'),
        ('neither', 'Neither'),
        ('both', 'Both'),
        ('london lows swept', 'London Lows Swept'),
    ])


def get_outcome_choices():
    return get_choices('outcome', [
        ('win', 'Win'),
        ('loss', 'Loss'),
    ])


def get_discipline_score_choices():
    return get_choices('discipline_score', [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor'),
        ('very poor', 'Very Poor'),
    ])


def get_entry_quality_choices():
    return get_choices('entry_quality', [
        ('perfect', 'Perfect'),
        ('chased', 'Chased'),
        ('early', 'Early'),
        ('late', 'Late'),
        ('stop loss issue', 'Stop Loss Issue'),
    ])


def get_market_behaviour_choices():
    return get_choices('market_behaviour', [
        ('as expected', 'As Expected'),
        ('choppy', 'Choppy'),
        ('surprise', 'Surprise'),
        ('opposite', 'Opposite'),
        ('hit stop then reversed', 'Hit Stop Then Reversed'),
    ])


def get_day_of_week_choices():
    return get_choices('day_of_week', [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ])


def get_backtest_outcome_choices():
    return get_choices('backtest_outcome', [
        ('no_setup', 'No Setup'),
        ('win', 'Win'),
        ('loss', 'Loss'),
    ])

