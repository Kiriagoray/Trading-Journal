from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from decimal import Decimal
from .models import AfterTradeEntry, PreTradeEntry, BacktestEntry, StrategyTag, FilterPreset, LotSizeCalculation


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
            'pair': forms.TextInput(attrs={'class': 'form-control'}),
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


PREDICTED_HTF_DIRECTION_CHOICES = [
    ('bullish', 'Bullish'),
    ('bearish', 'Bearish'),
    ('neutral', 'Neutral'),
]

MARKET_CONDITION_CHOICES_EXTENDED = [
    ('Trending', 'Trending'),
    ('Ranging', 'Ranging'),
    ('Consolidating', 'Consolidating'),
]

HTF_POI_TYPE_CHOICES = [
    ('1H FVG', '1H FVG'),
    ('1H OB', '1H OB'),
    ('4H FVG', '4H FVG'),
    ('4H OB', '4H OB'),
    ('Daily FVG', 'Daily FVG'),
    ('Daily OB', 'Daily OB'),
]

SESSION_TARGET_CHOICES = [
    ('Morning (7-11 AM)', 'Morning (7-11 AM)'),
    ('Afternoon', 'Afternoon'),
    ('NY Killzone', 'NY Killzone'),
]

LOWER_TF_CONFIRMATION_CHOICES_DETAILED = [
    ('15M BOS + Retest', '15M BOS + Retest'),
    ('5M BOS + Retest', '5M BOS + Retest'),
    ('OB entry', 'OB entry'),
    ('FVG Fill', 'FVG Fill'),
    ('Retest of HTF POI', 'Retest of HTF POI'),
]

SESSION_TIME_CHOICES = [
    ('7-10', '7-10'),
    ('10-12', '10-12'),
    ('12-2', '12-2'),
    ('2-4', '2-4'),
    ('4-6', '4-6'),
]

HIGH_IMPACT_NEWS_CHOICES = [
    ('None', 'None'),
    ('NFP', 'NFP'),
    ('CPI', 'CPI'),
    ('FOMC', 'FOMC'),
    ('GDP', 'GDP'),
    ('Other', 'Other'),
]

BEHAVIOUR_CHOICES = [
    ('London consolidation', 'London consolidation'),
    ('NY manipulation', 'NY manipulation'),
    ('Reversal', 'Reversal'),
    ('Breakout', 'Breakout'),
    ('Trend continuation', 'Trend continuation'),
]


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
            'pair': forms.TextInput(attrs={'class': 'form-control'}),
            'bias': forms.Select(attrs={'class': 'form-select'}),
            'predicted_htf_direction': forms.Select(choices=PREDICTED_HTF_DIRECTION_CHOICES, attrs={'class': 'form-select'}),
            'market_condition': forms.Select(choices=MARKET_CONDITION_CHOICES_EXTENDED, attrs={'class': 'form-select'}),
            'liquidity_analysis': forms.Select(attrs={'class': 'form-select'}),
            'htf_poi_type': forms.Select(choices=HTF_POI_TYPE_CHOICES, attrs={'class': 'form-select'}),
            'session_target': forms.Select(choices=SESSION_TARGET_CHOICES, attrs={'class': 'form-select'}),
            'htf_draws': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'e.g., Resting London lows, Asian lows, HTF FVG'}),
            'lower_tf_confirmation': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'e.g., 15M BOS + Retest, 5M BOS + Retest, OB entry'}),
            'reason_for_taking_or_not': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'setup_image': forms.FileInput(attrs={'class': 'form-control'}),
            'outcome_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


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
            'pair': forms.TextInput(attrs={'class': 'form-control'}),
            'htf_bias': forms.Select(attrs={'class': 'form-select'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'market_condition': forms.Select(choices=MARKET_CONDITION_CHOICES_EXTENDED, attrs={'class': 'form-select'}),
            'liquidity_analysis': forms.Select(attrs={'class': 'form-select'}),
            'session_time': forms.Select(choices=SESSION_TIME_CHOICES, attrs={'class': 'form-select'}),
            'outcome': forms.Select(attrs={'class': 'form-select'}),
            'lower_tf_bos': forms.Select(choices=LOWER_TF_CONFIRMATION_CHOICES_DETAILED, attrs={'class': 'form-select'}),
            'entry_trigger': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 15M BOS + Retest'}),
            'high_impact_news': forms.Select(choices=HIGH_IMPACT_NEWS_CHOICES, attrs={'class': 'form-select'}),
            'behaviour_based_on_previous_moves': forms.Select(choices=BEHAVIOUR_CHOICES, attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'screenshot': forms.FileInput(attrs={'class': 'form-control'}),
        }


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
        choices=[
            ('EUR/USD', 'EUR/USD'),
            ('GBP/USD', 'GBP/USD'),
            ('USD/JPY', 'USD/JPY'),
            ('GBP/JPY', 'GBP/JPY'),
            ('XAU/USD', 'XAU/USD (Gold)'),
            ('BTC/USD', 'BTC/USD'),
            ('ETH/USD', 'ETH/USD'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Trading instrument'
    )
    
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
        pip_value_map = {
            'EUR/USD': Decimal('10.00'),
            'GBP/USD': Decimal('10.00'),
            'USD/JPY': Decimal('9.09'),
            'GBP/JPY': Decimal('9.09'),
            'XAU/USD': Decimal('100.00'),
            'BTC/USD': Decimal('10.00'),
            'ETH/USD': Decimal('10.00'),
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
