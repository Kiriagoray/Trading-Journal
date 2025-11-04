"""
Utility functions for getting choice options from Configuration models
"""
from django.db import models
from .models import ChoiceOption, ChoiceCategory


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


# Additional utility functions for all choice categories used in forms
def get_predicted_htf_direction_choices():
    return get_choices('predicted_htf_direction', [
        ('bullish', 'Bullish'),
        ('bearish', 'Bearish'),
        ('neutral', 'Neutral'),
    ])


def get_lower_tf_confirmation_choices():
    return get_choices('lower_tf_confirmation', [
        ('single', 'Single'),
        ('double', 'Double'),
        ('15M BOS + Retest', '15M BOS + Retest'),
        ('5M BOS + Retest', '5M BOS + Retest'),
        ('OB entry', 'OB entry'),
        ('FVG Fill', 'FVG Fill'),
        ('Retest of HTF POI', 'Retest of HTF POI'),
    ])


def get_predicted_directional_bias_choices():
    return get_choices('predicted_directional_bias', [
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect'),
        ('partial', 'Partial'),
    ])


def get_poi_performance_choices():
    return get_choices('poi_performance', [
        ('respected perfectly', 'Respected Perfectly'),
        ('overshot', 'Overshot'),
        ('partial fill', 'Partial Fill'),
        ('no htf poi', 'No HTF POI'),
        ('rejected', 'Rejected'),
    ])


def get_htf_poi_type_choices():
    return get_choices('htf_poi_type', [
        ('1H FVG', '1H FVG'),
        ('1H OB', '1H OB'),
        ('4H FVG', '4H FVG'),
        ('4H OB', '4H OB'),
        ('Daily FVG', 'Daily FVG'),
        ('Daily OB', 'Daily OB'),
    ])


def get_pair_choices():
    """Get currency pair choices from backend or fallback"""
    return get_choices('pair', [
        ('AUD/JPY', 'AUD/JPY'),
        ('AUD/USD', 'AUD/USD'),
        ('EUR/AUD', 'EUR/AUD'),
        ('EUR/CAD', 'EUR/CAD'),
        ('EUR/GBP', 'EUR/GBP'),
        ('EUR/JPY', 'EUR/JPY'),
        ('EUR/USD', 'EUR/USD'),
        ('GBP/CHF', 'GBP/CHF'),
        ('GBP/JPY', 'GBP/JPY'),
        ('GBP/USD', 'GBP/USD'),
        ('NZD/USD', 'NZD/USD'),
        ('USD/CAD', 'USD/CAD'),
        ('USD/CHF', 'USD/CHF'),
        ('USD/JPY', 'USD/JPY'),
        ('USD/HKD', 'USD/HKD'),
        ('USD/SGD', 'USD/SGD'),
        ('USD/TRY', 'USD/TRY'),
        ('USD/ZAR', 'USD/ZAR'),
        ('XAU/USD', 'XAU/USD (Gold)'),
    ])


def get_high_impact_news_choices():
    return get_choices('high_impact_news', [
        ('None', 'None'),
        ('NFP', 'NFP'),
        ('CPI', 'CPI'),
        ('FOMC', 'FOMC'),
        ('GDP', 'GDP'),
        ('Other', 'Other'),
    ])


def get_behaviour_choices():
    return get_choices('behaviour', [
        ('London consolidation', 'London consolidation'),
        ('NY manipulation', 'NY manipulation'),
        ('Reversal', 'Reversal'),
        ('Breakout', 'Breakout'),
        ('Trend continuation', 'Trend continuation'),
    ])


def get_categories_for_journal(journal_type):
    """
    Get all active categories for a specific journal type
    Returns a list of categories with their choices
    """
    categories = ChoiceCategory.objects.filter(
        is_active=True
    ).filter(
        models.Q(journal_type=journal_type) | models.Q(journal_type='all')
    ).order_by('order', 'display_name')
    
    result = {}
    for category in categories:
        choices = ChoiceOption.get_choices_for_category(category.name)
        if choices:
            result[category] = choices
    
    return result


def apply_dynamic_categories_to_form(form, journal_type):
    """
    Apply dynamic categories to a form instance
    - If category has field_name, update that field's choices
    - If category has no field_name, add it as a new field dynamically
    """
    from django import forms
    
    categories = get_categories_for_journal(journal_type)
    
    for category, choices in categories.items():
        if category.field_name:
            # Map to existing field
            if category.field_name in form.fields:
                # Update choices only, don't change label (preserve original label)
                form.fields[category.field_name].choices = choices
                # Only update help_text if category has description and field doesn't have one
                if category.description and not form.fields[category.field_name].help_text:
                    form.fields[category.field_name].help_text = category.description
            else:
                # Field doesn't exist, add it dynamically
                form.fields[category.field_name] = forms.ChoiceField(
                    choices=choices,
                    required=False,
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    label=category.display_name,
                    help_text=category.description if category.description else ''
                )
        else:
            # Create new dynamic field using category name as field name
            field_name = category.name
            # Only create if field doesn't exist AND it's not in the form's Meta.fields
            # (to avoid creating duplicates of existing model fields)
            if field_name not in form.fields:
                # Check if this field exists in the model's Meta.fields
                if hasattr(form.Meta, 'fields') and field_name in form.Meta.fields:
                    # Field exists in model but not in form.fields yet - skip to avoid duplicate
                    # This can happen if a category name matches a model field name
                    continue
                form.fields[field_name] = forms.ChoiceField(
                    choices=choices,
                    required=False,
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    label=category.display_name,
                    help_text=category.description if category.description else ''
                )

