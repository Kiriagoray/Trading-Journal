from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from decimal import Decimal
from .models import AfterTradeEntry, PreTradeEntry, BacktestEntry, StrategyTag, FilterPreset, LotSizeCalculation
from .utils import (
    get_session_choices, get_bias_choices, get_market_condition_choices,
    get_liquidity_analysis_choices, get_outcome_choices, get_discipline_score_choices,
    get_entry_quality_choices, get_market_behaviour_choices, get_day_of_week_choices,
    get_backtest_outcome_choices, get_predicted_htf_direction_choices,
    get_lower_tf_confirmation_choices, get_predicted_directional_bias_choices,
    get_poi_performance_choices, get_htf_poi_type_choices, get_high_impact_news_choices,
    get_behaviour_choices, get_pair_choices,
    get_user_journal_fields, create_dynamic_form_field, get_field_value_for_entry
)


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class AfterTradeEntryForm(forms.ModelForm):
    """Dynamic form - only shows system fields + user-defined custom fields"""
    class Meta:
        model = AfterTradeEntry
        # System fields only: pair, date, outcome (direction), chart_image (screenshot), observations (notes)
        fields = ['pair', 'date', 'outcome', 'chart_image', 'observations']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pair': forms.Select(attrs={'class': 'form-select'}),
            'outcome': forms.Select(attrs={'class': 'form-select'}),
            'chart_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # System fields setup
        pair_choices = get_pair_choices()
        self.fields['pair'] = forms.ChoiceField(
            choices=pair_choices,
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=True,
            label='Pair'
        )
        self.fields['outcome'].choices = get_outcome_choices()
        self.fields['outcome'].label = 'Direction/Outcome'
        
        # Add dynamic custom fields if user is provided
        if user:
            try:
                custom_fields = get_user_journal_fields(user, 'after_trade')
                for field in custom_fields:
                    try:
                        form_field = create_dynamic_form_field(field)
                        if form_field is None:
                            continue
                        # Set initial value if editing existing entry
                        if self.instance and self.instance.pk:
                            try:
                                value_obj = get_field_value_for_entry(self.instance, field)
                                if value_obj:
                                    if field.field_type == 'checkbox':
                                        form_field.initial = value_obj.value_boolean
                                    elif field.field_type in ['number', 'decimal']:
                                        form_field.initial = value_obj.value_number
                                    elif field.field_type == 'date':
                                        form_field.initial = value_obj.value_date
                                    elif field.field_type == 'datetime':
                                        form_field.initial = value_obj.value_datetime
                                    elif field.field_type == 'multiselect':
                                        # Multi-select stored as comma-separated
                                        form_field.initial = value_obj.value_text.split(',') if value_obj.value_text else []
                                    else:
                                        form_field.initial = value_obj.value_text
                            except Exception as e:
                                # Skip if we can't get the value
                                pass
                        self.fields[f'custom_{field.name}'] = form_field
                    except Exception as e:
                        # Skip fields that can't be created
                        continue
            except Exception as e:
                # If we can't get custom fields, continue without them
                pass


class PreTradeEntryForm(forms.ModelForm):
    """Dynamic form - only shows system fields + user-defined custom fields"""
    class Meta:
        model = PreTradeEntry
        # System fields only: pair, date, bias (direction), setup_image (screenshot), notes
        fields = ['pair', 'date', 'bias', 'setup_image', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pair': forms.Select(attrs={'class': 'form-select'}),
            'bias': forms.Select(attrs={'class': 'form-select'}),
            'setup_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # System fields setup
        pair_choices = get_pair_choices()
        self.fields['pair'] = forms.ChoiceField(
            choices=pair_choices,
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=True,
            label='Pair'
        )
        self.fields['bias'].choices = get_bias_choices()
        self.fields['bias'].label = 'Direction/Bias'
        
        # Add dynamic custom fields if user is provided
        if user:
            try:
                custom_fields = get_user_journal_fields(user, 'pre_trade')
                for field in custom_fields:
                    try:
                        form_field = create_dynamic_form_field(field)
                        if form_field is None:
                            continue
                        # Set initial value if editing existing entry
                        if self.instance and self.instance.pk:
                            try:
                                value_obj = get_field_value_for_entry(self.instance, field)
                                if value_obj:
                                    if field.field_type == 'checkbox':
                                        form_field.initial = value_obj.value_boolean
                                    elif field.field_type in ['number', 'decimal']:
                                        form_field.initial = value_obj.value_number
                                    elif field.field_type == 'date':
                                        form_field.initial = value_obj.value_date
                                    elif field.field_type == 'datetime':
                                        form_field.initial = value_obj.value_datetime
                                    elif field.field_type == 'multiselect':
                                        # Multi-select stored as comma-separated
                                        form_field.initial = value_obj.value_text.split(',') if value_obj.value_text else []
                                    else:
                                        form_field.initial = value_obj.value_text
                            except Exception as e:
                                # Skip if we can't get the value
                                pass
                        self.fields[f'custom_{field.name}'] = form_field
                    except Exception as e:
                        # Skip fields that can't be created
                        continue
            except Exception as e:
                # If we can't get custom fields, continue without them
                pass


class BacktestEntryForm(forms.ModelForm):
    """Dynamic form - only shows system fields + user-defined custom fields"""
    class Meta:
        model = BacktestEntry
        # System fields only: pair, date, htf_bias (direction), screenshot, notes
        fields = ['pair', 'date', 'htf_bias', 'screenshot', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pair': forms.Select(attrs={'class': 'form-select'}),
            'htf_bias': forms.Select(attrs={'class': 'form-select'}),
            'screenshot': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # System fields setup
        pair_choices = get_pair_choices()
        self.fields['pair'] = forms.ChoiceField(
            choices=pair_choices,
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=True,
            label='Pair'
        )
        self.fields['htf_bias'].choices = get_bias_choices()
        self.fields['htf_bias'].label = 'Direction/Bias'
        
        # Add dynamic custom fields if user is provided
        if user:
            try:
                custom_fields = get_user_journal_fields(user, 'backtest')
                for field in custom_fields:
                    try:
                        form_field = create_dynamic_form_field(field)
                        if form_field is None:
                            continue
                        # Set initial value if editing existing entry
                        if self.instance and self.instance.pk:
                            try:
                                value_obj = get_field_value_for_entry(self.instance, field)
                                if value_obj:
                                    if field.field_type == 'checkbox':
                                        form_field.initial = value_obj.value_boolean
                                    elif field.field_type in ['number', 'decimal']:
                                        form_field.initial = value_obj.value_number
                                    elif field.field_type == 'date':
                                        form_field.initial = value_obj.value_date
                                    elif field.field_type == 'datetime':
                                        form_field.initial = value_obj.value_datetime
                                    elif field.field_type == 'multiselect':
                                        # Multi-select stored as comma-separated
                                        form_field.initial = value_obj.value_text.split(',') if value_obj.value_text else []
                                    else:
                                        form_field.initial = value_obj.value_text
                            except Exception as e:
                                # Skip if we can't get the value
                                pass
                        self.fields[f'custom_{field.name}'] = form_field
                    except Exception as e:
                        # Skip fields that can't be created
                        continue
            except Exception as e:
                # If we can't get custom fields, continue without them
                pass


class LotSizeCalculatorForm(forms.Form):
    account_balance = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'account_balance'}),
        help_text='Account balance amount'
    )
    account_currency = forms.ChoiceField(
        choices=[
            ('USD', 'USD (US Dollar)'),
            ('EUR', 'EUR (Euro)'),
            ('GBP', 'GBP (British Pound)'),
            ('JPY', 'JPY (Japanese Yen)'),
            ('AUD', 'AUD (Australian Dollar)'),
            ('CAD', 'CAD (Canadian Dollar)'),
            ('CHF', 'CHF (Swiss Franc)'),
            ('NZD', 'NZD (New Zealand Dollar)'),
        ],
        initial='USD',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'account_currency'}),
        help_text='Account currency'
    )
    risk_percentage = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'risk_percentage'}),
        help_text='Risk percentage (e.g., 1 for 1%)'
    )
    stop_loss_pips = forms.DecimalField(
        max_digits=8, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'stop_loss_pips'}),
        help_text='Stop loss in pips/points'
    )
    instrument = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'instrument_select'}),
        help_text='Trading instrument'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get instruments from instrument_data
        from .instrument_data import get_instrument_choices
        self.fields['instrument'].choices = get_instrument_choices()
    
    def calculate_lot_size(self):
        """
        Calculate lot size using the standard formula:
        Lot Size = (Account Risk $) / (Stop Loss × Pip/Point Value)
        """
        from .instrument_data import get_instrument_data, get_pip_value
        
        account_balance = self.cleaned_data.get('account_balance')
        risk_percentage = self.cleaned_data.get('risk_percentage')
        stop_loss_pips = self.cleaned_data.get('stop_loss_pips')
        instrument_code = self.cleaned_data.get('instrument', 'EURUSD')
        
        if not all([account_balance, risk_percentage, stop_loss_pips]):
            return None
        
        # Convert to Decimal for consistent calculations
        account_balance = Decimal(str(account_balance))
        risk_percentage = Decimal(str(risk_percentage))
        stop_loss_pips = Decimal(str(stop_loss_pips))
        
        # Risk amount in USD
        risk_amount = account_balance * (risk_percentage / Decimal('100'))
        
        # Get pip/point value for the selected instrument
        pip_value = Decimal(str(get_pip_value(instrument_code)))
        
        # Calculate lot size using standard formula
        # Lot Size = Risk Amount / (Stop Loss × Pip Value)
        if stop_loss_pips > 0 and pip_value > 0:
            lot_size = risk_amount / (stop_loss_pips * pip_value)
        else:
            return None
        
        return float(round(lot_size, 2))


class FilterPresetForm(forms.ModelForm):
    class Meta:
        model = FilterPreset
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }
