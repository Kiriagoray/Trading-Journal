"""
Utility functions for getting choice options from Configuration models
"""
from django.db import models
from django.db.models import Q
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


# Dynamic Field System Utilities
def get_user_journal_fields(user, journal_type):
    """Get all active custom fields for a user's journal type"""
    from .models import JournalField
    return JournalField.objects.filter(
        user=user,
        journal_type=journal_type,
        is_active=True
    ).order_by('order', 'display_name')


def search_entries_with_custom_fields(queryset, search_term, journal_type, user):
    """
    Search entries across system fields and all custom fields
    
    Args:
        queryset: The base queryset to filter
        search_term: The search string
        journal_type: 'after_trade', 'pre_trade', or 'backtest'
        user: The user whose entries to search
        
    Returns:
        Filtered queryset
    """
    from .models import JournalFieldValue
    
    if not search_term:
        return queryset
    
    # Build Q object for system fields (varies by journal type)
    system_q = Q()
    
    if journal_type == 'after_trade':
        system_q = Q(
            Q(pair__icontains=search_term) |
            Q(outcome__icontains=search_term) |
            Q(observations__icontains=search_term)
        )
    elif journal_type == 'pre_trade':
        system_q = Q(
            Q(pair__icontains=search_term) |
            Q(bias__icontains=search_term) |
            Q(notes__icontains=search_term)
        )
    elif journal_type == 'backtest':
        system_q = Q(
            Q(pair__icontains=search_term) |
            Q(htf_bias__icontains=search_term) |
            Q(notes__icontains=search_term)
        )
    
    # Get custom fields for this journal type
    custom_fields = get_user_journal_fields(user, journal_type)
    
    # Search in custom field values
    matching_entry_ids = set()
    if custom_fields:
        entry_ids = list(queryset.values_list('id', flat=True))
        if entry_ids:
            # Search in all text-based custom fields
            field_ids = list(custom_fields.values_list('id', flat=True))
            matching_values = JournalFieldValue.objects.filter(
                field_id__in=field_ids,
                entry_id__in=entry_ids,
                value_text__icontains=search_term
            )
            matching_entry_ids = set(matching_values.values_list('entry_id', flat=True))
    
    # Combine system and custom field searches
    if matching_entry_ids:
        return queryset.filter(system_q | Q(id__in=matching_entry_ids))
    else:
        return queryset.filter(system_q)


def filter_entries_by_custom_field(queryset, field, filter_value, journal_type):
    """
    Filter entries by a custom field value
    
    Args:
        queryset: The base queryset to filter
        field: JournalField instance
        filter_value: The value to filter by (format depends on field type)
        journal_type: 'after_trade', 'pre_trade', or 'backtest'
        
    Returns:
        Filtered queryset
    """
    from .models import JournalFieldValue
    
    if not filter_value:
        return queryset
    
    entry_ids = list(queryset.values_list('id', flat=True))
    if not entry_ids:
        return queryset.none()
    
    field_values = JournalFieldValue.objects.filter(
        field=field,
        entry_id__in=entry_ids
    )
    
    if field.field_type == 'select':
        # Exact match for select
        field_values = field_values.filter(value_text=filter_value)
    elif field.field_type == 'multi_select':
        # Contains check for multi-select (stored as comma-separated or JSON)
        field_values = field_values.filter(
            Q(value_text__icontains=filter_value) |
            Q(value_text__startswith=f"{filter_value},") |
            Q(value_text__endswith=f",{filter_value}")
        )
    elif field.field_type == 'checkbox':
        # Boolean match
        bool_value = str(filter_value).lower() in ['true', '1', 'yes']
        field_values = field_values.filter(value_boolean=bool_value)
    elif field.field_type in ['number', 'decimal']:
        # Numeric range (filter_value should be min or max)
        try:
            num_value = float(filter_value)
            if 'min' in str(filter_value):
                field_values = field_values.filter(value_number__gte=num_value)
            elif 'max' in str(filter_value):
                field_values = field_values.filter(value_number__lte=num_value)
            else:
                field_values = field_values.filter(value_number=num_value)
        except ValueError:
            pass
    elif field.field_type == 'date':
        # Date range
        field_values = field_values.filter(value_date=filter_value)
    elif field.field_type in ['text', 'textarea']:
        # Text contains
        field_values = field_values.filter(value_text__icontains=filter_value)
    
    matching_entry_ids = list(field_values.values_list('entry_id', flat=True))
    if matching_entry_ids:
        return queryset.filter(id__in=matching_entry_ids)
    else:
        return queryset.none()


def sort_entries_by_custom_field(queryset, field, order='asc', journal_type='after_trade'):
    """
    Sort entries by a custom field or system field
    
    Args:
        queryset: The base queryset to sort
        field: JournalField instance (or None/empty string for system field)
        order: 'asc' or 'desc'
        journal_type: 'after_trade', 'pre_trade', or 'backtest'
        
    Returns:
        Sorted queryset
    """
    from .models import JournalFieldValue
    
    if not field or field == '':
        # System field sorting
        if journal_type == 'after_trade':
            return queryset.order_by(f'-date' if order == 'desc' else 'date')
        else:
            return queryset.order_by(f'-date' if order == 'desc' else 'date')
    
    # For custom fields, we'll sort in Python after fetching
    # This is simpler and works for all field types
    entry_ids = list(queryset.values_list('id', flat=True))
    if not entry_ids:
        return queryset
    
    # Get field values for sorting
    field_values = JournalFieldValue.objects.filter(
        field=field,
        entry_id__in=entry_ids
    )
    
    # Create mapping of entry_id -> sort value
    sort_map = {}
    for fv in field_values:
        if field.field_type in ['number', 'decimal']:
            sort_map[fv.entry_id] = fv.value_number or 0
        elif field.field_type == 'date':
            sort_map[fv.entry_id] = fv.value_date or ''
        else:
            sort_map[fv.entry_id] = (fv.value_text or '').lower()
    
    # Sort entry IDs by their values
    sorted_ids = sorted(
        entry_ids,
        key=lambda eid: sort_map.get(eid, '' if field.field_type in ['text', 'textarea', 'select'] else 0),
        reverse=(order == 'desc')
    )
    
    # Preserve order using a Case/When expression would be complex
    # Instead, return in the sorted order
    # Note: This approach works but may not be the most efficient for large datasets
    # For production, consider using database-level sorting with annotations
    
    # For now, return queryset ordered by ID (we'll handle custom sorting in view)
    return queryset.filter(id__in=sorted_ids).order_by('id')


def get_field_value_for_entry(entry, field):
    """Get the value for a specific field from an entry"""
    from .models import JournalFieldValue
    entry_type_map = {
        'AfterTradeEntry': 'after_trade',
        'PreTradeEntry': 'pre_trade',
        'BacktestEntry': 'backtest',
    }
    entry_type = entry_type_map.get(entry.__class__.__name__, '')
    
    try:
        value_obj = JournalFieldValue.objects.get(
            entry_type=entry_type,
            entry_id=entry.pk,
            field=field
        )
        return value_obj
    except JournalFieldValue.DoesNotExist:
        return None


def get_all_field_values_for_entry(entry):
    """Get all custom field values for an entry"""
    from .models import JournalField, JournalFieldValue
    entry_type_map = {
        'AfterTradeEntry': 'after_trade',
        'PreTradeEntry': 'pre_trade',
        'BacktestEntry': 'backtest',
    }
    entry_type = entry_type_map.get(entry.__class__.__name__, '')
    
    fields = get_user_journal_fields(entry.user, entry_type)
    values = {}
    for field in fields:
        value_obj = get_field_value_for_entry(entry, field)
        values[field] = value_obj
    return values


def save_field_value_for_entry(entry, field, value):
    """Save a field value for an entry"""
    from .models import JournalFieldValue
    entry_type_map = {
        'AfterTradeEntry': 'after_trade',
        'PreTradeEntry': 'pre_trade',
        'BacktestEntry': 'backtest',
    }
    entry_type = entry_type_map.get(entry.__class__.__name__, '')
    
    value_obj, created = JournalFieldValue.objects.get_or_create(
        entry_type=entry_type,
        entry_id=entry.pk,
        field=field,
        defaults={}
    )
    value_obj.set_value(value)
    value_obj.save()
    return value_obj


def create_dynamic_form_field(field):
    """Create a Django form field from a JournalField"""
    from django import forms
    
    field_kwargs = {
        'label': field.display_name,
        'required': field.is_required,
        'help_text': field.help_text,
    }
    
    if field.default_value:
        field_kwargs['initial'] = field.default_value
    
    if field.field_type == 'text':
        return forms.CharField(
            max_length=500,
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            **field_kwargs
        )
    elif field.field_type == 'textarea':
        return forms.CharField(
            widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            **field_kwargs
        )
    elif field.field_type == 'number':
        return forms.IntegerField(
            widget=forms.NumberInput(attrs={'class': 'form-control'}),
            **field_kwargs
        )
    elif field.field_type == 'decimal':
        return forms.DecimalField(
            max_digits=20,
            decimal_places=10,
            widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            **field_kwargs
        )
    elif field.field_type == 'select':
        choices = [(opt.value, opt.display_label) for opt in field.options.all().order_by('order')]
        return forms.ChoiceField(
            choices=choices,
            widget=forms.Select(attrs={'class': 'form-select'}),
            **field_kwargs
        )
    elif field.field_type == 'multiselect':
        choices = [(opt.value, opt.display_label) for opt in field.options.all().order_by('order')]
        return forms.MultipleChoiceField(
            choices=choices,
            widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
            **field_kwargs
        )
    elif field.field_type == 'checkbox':
        return forms.BooleanField(
            required=False,
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            **field_kwargs
        )
    elif field.field_type == 'date':
        return forms.DateField(
            widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            **field_kwargs
        )
    elif field.field_type == 'time':
        return forms.TimeField(
            widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            **field_kwargs
        )
    elif field.field_type == 'datetime':
        return forms.DateTimeField(
            widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            **field_kwargs
        )
    elif field.field_type == 'url':
        return forms.URLField(
            widget=forms.URLInput(attrs={'class': 'form-control'}),
            **field_kwargs
        )
    elif field.field_type == 'email':
        return forms.EmailField(
            widget=forms.EmailInput(attrs={'class': 'form-control'}),
            **field_kwargs
        )
    else:
        # Default to text
        return forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            **field_kwargs
        )

