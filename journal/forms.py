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
    get_behaviour_choices, get_pair_choices
)


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class AfterTradeEntryForm(forms.ModelForm):
    class Meta:
        model = AfterTradeEntry
        fields = [
            'pair', 'date', 'session', 'bias', 'htf_mitigation', 'liquidity_analysis',
            'market_condition', 'lower_tf_confirmation', 'risk_management_applied',
            'high_impact_news', 'major_impact_news', 'predicted_directional_bias',
            'poi_performance', 'risk_percentage', 'market_behaviour', 'entry_quality',
            'poi_quality_score', 'time_of_entry', 'outcome', 'discipline_score',
            'risk_pips', 'reward_pips', 'chart_image', 'observations'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_of_entry': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'pair': forms.Select(attrs={'class': 'form-select'}),
            'session': forms.Select(attrs={'class': 'form-select'}),
            'bias': forms.Select(attrs={'class': 'form-select'}),
            'liquidity_analysis': forms.Select(attrs={'class': 'form-select'}),
            'market_condition': forms.Select(attrs={'class': 'form-select'}),
            'lower_tf_confirmation': forms.Select(attrs={'class': 'form-select'}),
            'predicted_directional_bias': forms.Select(attrs={'class': 'form-select'}),
            'poi_performance': forms.Select(attrs={'class': 'form-select'}),
            'market_behaviour': forms.Select(attrs={'class': 'form-select'}),
            'entry_quality': forms.Select(attrs={'class': 'form-select'}),
            'outcome': forms.Select(attrs={'class': 'form-select'}),
            'discipline_score': forms.Select(attrs={'class': 'form-select'}),
            'poi_quality_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'risk_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'risk_pips': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reward_pips': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'major_impact_news': forms.TextInput(attrs={'class': 'form-control'}),
            'chart_image': forms.FileInput(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert pair field to ChoiceField for dropdown
        from django import forms
        pair_choices = get_pair_choices()
        self.fields['pair'] = forms.ChoiceField(
            choices=pair_choices,
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=True,
            label='Pair'
        )
        # Dynamically set choices for each field that needs them
        # This ensures choices are fetched fresh from the database each time the form is instantiated
        self.fields['session'].choices = get_session_choices()
        self.fields['bias'].choices = get_bias_choices()
        self.fields['liquidity_analysis'].choices = get_liquidity_analysis_choices()
        self.fields['market_condition'].choices = get_market_condition_choices()
        self.fields['lower_tf_confirmation'].choices = get_lower_tf_confirmation_choices()
        self.fields['predicted_directional_bias'].choices = get_predicted_directional_bias_choices()
        self.fields['poi_performance'].choices = get_poi_performance_choices()
        self.fields['market_behaviour'].choices = get_market_behaviour_choices()
        self.fields['entry_quality'].choices = get_entry_quality_choices()
        self.fields['outcome'].choices = get_outcome_choices()
        self.fields['discipline_score'].choices = get_discipline_score_choices()
        
        # Apply dynamic categories for after_trade journal
        from .utils import apply_dynamic_categories_to_form
        apply_dynamic_categories_to_form(self, 'after_trade')


class PreTradeEntryForm(forms.ModelForm):
    class Meta:
        model = PreTradeEntry
        fields = [
            'pair', 'date', 'bias', 'predicted_htf_direction', 'market_condition',
            'liquidity_analysis', 'htf_poi_type', 'session_target', 'htf_draws',
            'lower_tf_confirmation', 'setup_image', 'all_conditions_met',
            'trade_taken', 'reason_for_taking_or_not', 'outcome_image', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pair': forms.Select(attrs={'class': 'form-select'}),
            'bias': forms.Select(attrs={'class': 'form-select'}),
            'predicted_htf_direction': forms.Select(attrs={'class': 'form-select'}),
            'market_condition': forms.Select(attrs={'class': 'form-select'}),
            'liquidity_analysis': forms.Select(attrs={'class': 'form-select'}),
            'htf_poi_type': forms.Select(attrs={'class': 'form-select'}),
            'session_target': forms.Select(attrs={'class': 'form-select'}),
            'htf_draws': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'e.g., Resting London lows, Asian lows, HTF FVG'}),
            'lower_tf_confirmation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'e.g., 15M BOS + Retest, 5M BOS + Retest, OB entry'}),
            'reason_for_taking_or_not': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'setup_image': forms.FileInput(attrs={'class': 'form-control'}),
            'outcome_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert pair field to ChoiceField for dropdown
        from django import forms
        pair_choices = get_pair_choices()
        self.fields['pair'] = forms.ChoiceField(
            choices=pair_choices,
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=True,
            label='Pair'
        )
        # Dynamically set choices for each field that needs them
        self.fields['bias'].choices = get_bias_choices()
        self.fields['predicted_htf_direction'].choices = get_predicted_htf_direction_choices()
        self.fields['market_condition'].choices = get_market_condition_choices()
        self.fields['liquidity_analysis'].choices = get_liquidity_analysis_choices()
        self.fields['htf_poi_type'].choices = get_htf_poi_type_choices()
        self.fields['session_target'].choices = get_session_choices()
        
        # Apply dynamic categories for pre_trade journal
        from .utils import apply_dynamic_categories_to_form
        apply_dynamic_categories_to_form(self, 'pre_trade')


class BacktestEntryForm(forms.ModelForm):
    class Meta:
        model = BacktestEntry
        fields = [
            'pair', 'date', 'htf_bias', 'day_of_week', 'market_condition',
            'price_within_htf_poi', 'liquidity_analysis', 'lower_tf_bos',
            'fvg_present', 'ifvg', 'retest_into_ob', 'session_time',
            'entry_time', 'setup_present', 'high_impact_news', 'entry_trigger',
            'behaviour_based_on_previous_moves', 'outcome', 'screenshot',
            'notes', 'chasing_long_on', 'overnight'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'entry_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'pair': forms.Select(attrs={'class': 'form-select'}),
            'htf_bias': forms.Select(attrs={'class': 'form-select'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'market_condition': forms.Select(attrs={'class': 'form-select'}),
            'liquidity_analysis': forms.Select(attrs={'class': 'form-select'}),
            'session_time': forms.Select(attrs={'class': 'form-select'}),
            'outcome': forms.Select(attrs={'class': 'form-select'}),
            'lower_tf_bos': forms.Select(attrs={'class': 'form-select'}),
            'entry_trigger': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 15M BOS + Retest'}),
            'high_impact_news': forms.Select(attrs={'class': 'form-select'}),
            'behaviour_based_on_previous_moves': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'screenshot': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert pair field to ChoiceField for dropdown
        from django import forms
        pair_choices = get_pair_choices()
        self.fields['pair'] = forms.ChoiceField(
            choices=pair_choices,
            widget=forms.Select(attrs={'class': 'form-select'}),
            required=True,
            label='Pair'
        )
        # Dynamically set choices for each field that needs them
        self.fields['htf_bias'].choices = get_bias_choices()
        self.fields['day_of_week'].choices = get_day_of_week_choices()
        self.fields['market_condition'].choices = get_market_condition_choices()
        self.fields['liquidity_analysis'].choices = get_liquidity_analysis_choices()
        self.fields['session_time'].choices = get_session_choices()
        self.fields['outcome'].choices = get_backtest_outcome_choices()
        self.fields['lower_tf_bos'].choices = get_lower_tf_confirmation_choices()
        self.fields['high_impact_news'].choices = get_high_impact_news_choices()
        self.fields['behaviour_based_on_previous_moves'].choices = get_behaviour_choices()
        
        # Apply dynamic categories for backtest journal
        from .utils import apply_dynamic_categories_to_form
        apply_dynamic_categories_to_form(self, 'backtest')


class LotSizeCalculatorForm(forms.Form):
    account_balance = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        help_text='Account balance in USD'
    )
    risk_percentage = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        help_text='Risk percentage (e.g., 1 for 1%)'
    )
    stop_loss_pips = forms.DecimalField(
        max_digits=8, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        help_text='Stop loss in pips'
    )
    instrument = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Trading instrument'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get pairs from backend categories
        self.fields['instrument'].choices = get_pair_choices()
    
    def calculate_lot_size(self):
        """Calculate lot size based on Deriv broker format"""
        account_balance = self.cleaned_data.get('account_balance')
        risk_percentage = self.cleaned_data.get('risk_percentage')
        stop_loss_pips = self.cleaned_data.get('stop_loss_pips')
        instrument = self.cleaned_data.get('instrument', 'EUR/USD')
        
        if not all([account_balance, risk_percentage, stop_loss_pips]):
            return None
        
        # Convert to Decimal for consistent calculations
        account_balance = Decimal(str(account_balance))
        risk_percentage = Decimal(str(risk_percentage))
        stop_loss_pips = Decimal(str(stop_loss_pips))
        
        # Risk amount in USD
        risk_amount = account_balance * (risk_percentage / Decimal('100'))
        
        # Pip value in USD per pip per standard lot
        # For major pairs: $10 per pip per standard lot
        # For JPY pairs: $9.09 per pip (when USD/JPY ≈ 110)
        # For CAD pairs: ~$7.5-8 per pip
        # For CHF pairs: ~$10-11 per pip
        # For Gold: $100 per pip per standard lot (1 oz = $1 per pip)
        # For exotic pairs: approximate values
        pip_value_map = {
            # Major pairs - $10 per pip
            'EUR/USD': Decimal('10.00'),
            'GBP/USD': Decimal('10.00'),
            'AUD/USD': Decimal('10.00'),
            'NZD/USD': Decimal('10.00'),
            # JPY pairs - ~$9.09 per pip (when USD/JPY ≈ 110)
            'USD/JPY': Decimal('9.09'),
            'EUR/JPY': Decimal('9.09'),
            'GBP/JPY': Decimal('9.09'),
            'AUD/JPY': Decimal('9.09'),
            # CAD pairs - ~$7.5 per pip
            'USD/CAD': Decimal('7.50'),
            'EUR/CAD': Decimal('7.50'),
            # CHF pairs - ~$10.50 per pip
            'USD/CHF': Decimal('10.50'),
            'GBP/CHF': Decimal('10.50'),
            # Cross pairs
            'EUR/GBP': Decimal('10.00'),
            'EUR/AUD': Decimal('10.00'),
            # Exotic pairs - approximate values
            'USD/HKD': Decimal('1.28'),  # ~7.8 HKD per USD
            'USD/SGD': Decimal('7.40'),  # ~1.35 SGD per USD
            'USD/TRY': Decimal('0.10'),  # ~10 TRY per USD (varies significantly)
            'USD/ZAR': Decimal('0.70'),  # ~14 ZAR per USD
            # Gold
            'XAU/USD': Decimal('100.00'),  # $100 per pip per standard lot (1 oz)
        }
        
        pip_value = pip_value_map.get(instrument, Decimal('10.00'))
        
        # Calculate lot size
        if stop_loss_pips > 0:
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
