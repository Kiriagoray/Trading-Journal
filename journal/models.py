from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import os


def get_after_trade_upload_path(instance, filename):
    """Generate user-specific upload path for after trade chart images"""
    return f'journal/after_trade/user_{instance.user.id}/{filename}'


def get_pre_trade_upload_path(instance, filename):
    """Generate user-specific upload path for pre trade setup images"""
    return f'journal/pre_trade/user_{instance.user.id}/{filename}'


def get_pre_trade_outcome_upload_path(instance, filename):
    """Generate user-specific upload path for pre trade outcome images"""
    return f'journal/pre_trade_outcomes/user_{instance.user.id}/{filename}'


def get_backtest_upload_path(instance, filename):
    """Generate user-specific upload path for backtest screenshots"""
    return f'journal/backtesting/user_{instance.user.id}/{filename}'


# Choice constants - These are fallbacks if Configuration system is not set up
# The actual choices should come from ChoiceOption model via utils.get_choices()
SESSION_CHOICES = [
    ('Asian', 'Asian'),
    ('London', 'London'),
    ('NewYork', 'New York'),
]

BIAS_CHOICES = [
    ('bullish', 'Bullish'),
    ('bearish', 'Bearish'),
]

MARKET_CONDITION_CHOICES = [
    ('Trending Up', 'Trending Up'),
    ('Trending Down', 'Trending Down'),
    ('Consolidating', 'Consolidating'),
]

LOWER_TF_CONFIRMATION_CHOICES = [
    ('single', 'Single'),
    ('double', 'Double'),
]

PREDICTED_BIAS_CHOICES = [
    ('correct', 'Correct'),
    ('incorrect', 'Incorrect'),
    ('partial', 'Partial'),
]

POI_PERFORMANCE_CHOICES = [
    ('respected perfectly', 'Respected Perfectly'),
    ('overshot', 'Overshot'),
    ('partial fill', 'Partial Fill'),
    ('no htf poi', 'No HTF POI'),
    ('rejected', 'Rejected'),
]

OUTCOME_CHOICES = [
    ('win', 'Win'),
    ('loss', 'Loss'),
]

DISCIPLINE_SCORE_CHOICES = [
    ('excellent', 'Excellent'),
    ('good', 'Good'),
    ('average', 'Average'),
    ('poor', 'Poor'),
    ('very poor', 'Very Poor'),
]

ENTRY_QUALITY_CHOICES = [
    ('perfect', 'Perfect'),
    ('chased', 'Chased'),
    ('early', 'Early'),
    ('late', 'Late'),
    ('stop loss issue', 'Stop Loss Issue'),
]

MARKET_BEHAVIOUR_CHOICES = [
    ('as expected', 'As Expected'),
    ('choppy', 'Choppy'),
    ('surprise', 'Surprise'),
    ('opposite', 'Opposite'),
    ('hit stop then reversed', 'Hit Stop Then Reversed'),
]

LIQUIDITY_ANALYSIS_CHOICES = [
    ('buyside swept', 'Buyside Swept'),
    ('sellside swept', 'Sellside Swept'),
    ('neither', 'Neither'),
    ('both', 'Both'),
    ('london lows swept', 'London Lows Swept'),
]

BACKTEST_OUTCOME_CHOICES = [
    ('no_setup', 'No Setup'),
    ('win', 'Win'),
    ('loss', 'Loss'),
]

DAY_OF_WEEK_CHOICES = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
]


class StrategyTag(models.Model):
    """Strategy tags for categorizing trades"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#3b82f6', help_text='Hex color code')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Strategy Tags'

    def __str__(self):
        return self.name


class AfterTradeEntry(models.Model):
    """After Trade Journal Entry"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='after_trade_entries')
    pair = models.CharField(max_length=20)
    date = models.DateField()
    session = models.CharField(max_length=20, choices=SESSION_CHOICES)
    bias = models.CharField(max_length=10, choices=BIAS_CHOICES)
    htf_mitigation = models.BooleanField(default=False)
    liquidity_analysis = models.CharField(max_length=50, choices=LIQUIDITY_ANALYSIS_CHOICES)
    market_condition = models.CharField(max_length=20, choices=MARKET_CONDITION_CHOICES)
    lower_tf_confirmation = models.CharField(max_length=10, choices=LOWER_TF_CONFIRMATION_CHOICES)
    risk_management_applied = models.BooleanField(default=False)
    high_impact_news = models.BooleanField(default=False)
    major_impact_news = models.CharField(max_length=200, blank=True)
    predicted_directional_bias = models.CharField(max_length=10, choices=PREDICTED_BIAS_CHOICES)
    poi_performance = models.CharField(max_length=20, choices=POI_PERFORMANCE_CHOICES)
    risk_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    market_behaviour = models.CharField(max_length=30, choices=MARKET_BEHAVIOUR_CHOICES)
    entry_quality = models.CharField(max_length=20, choices=ENTRY_QUALITY_CHOICES)
    poi_quality_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    time_of_entry = models.TimeField()
    outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES)
    is_win = models.BooleanField(default=False, editable=False)
    discipline_score = models.CharField(max_length=20, choices=DISCIPLINE_SCORE_CHOICES)
    chart_image = models.ImageField(upload_to=get_after_trade_upload_path, blank=True, null=True)
    observations = models.TextField()
    # RR Tracking fields
    risk_pips = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text='Stop loss in pips')
    reward_pips = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text='Take profit in pips')
    rr_ratio = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, editable=False, help_text='Auto-calculated Risk:Reward ratio')
    # Strategy tagging
    strategy_tags = models.ManyToManyField(StrategyTag, blank=True, related_name='after_trade_entries')
    # AI-generated summary
    ai_summary = models.TextField(blank=True, null=True, help_text='Auto-generated trade summary')
    summary_generated_at = models.DateTimeField(blank=True, null=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time_of_entry']
        verbose_name_plural = 'After Trade Entries'

    def __str__(self):
        return f"{self.pair} - {self.date} - {self.outcome}"

    def save(self, *args, **kwargs):
        """Auto-compute is_win and rr_ratio"""
        self.is_win = (self.outcome == 'win')
        if self.risk_pips and self.reward_pips and self.risk_pips > 0:
            self.rr_ratio = self.reward_pips / self.risk_pips
        super().save(*args, **kwargs)


class PreTradeEntry(models.Model):
    """Pre Trade Journal Entry"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pre_trade_entries')
    pair = models.CharField(max_length=20)
    date = models.DateField()
    bias = models.CharField(max_length=10, choices=BIAS_CHOICES)
    predicted_htf_direction = models.CharField(max_length=10, choices=BIAS_CHOICES)
    market_condition = models.CharField(max_length=20, choices=MARKET_CONDITION_CHOICES)
    liquidity_analysis = models.CharField(max_length=50, choices=LIQUIDITY_ANALYSIS_CHOICES)
    htf_poi_type = models.CharField(max_length=100)
    session_target = models.CharField(max_length=20, choices=SESSION_CHOICES)
    htf_draws = models.TextField()
    lower_tf_confirmation = models.TextField()
    setup_image = models.ImageField(upload_to=get_pre_trade_upload_path, blank=True, null=True)
    all_conditions_met = models.BooleanField(default=False)
    trade_taken = models.BooleanField(default=False)
    reason_for_taking_or_not = models.TextField()
    outcome_image = models.ImageField(upload_to=get_pre_trade_outcome_upload_path, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = 'Pre Trade Entries'

    def __str__(self):
        return f"{self.pair} - {self.date}"


class BacktestEntry(models.Model):
    """Backtesting Journal Entry"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='backtest_entries')
    pair = models.CharField(max_length=20)
    date = models.DateField()
    htf_bias = models.CharField(max_length=10, choices=BIAS_CHOICES)
    day_of_week = models.CharField(max_length=10, choices=DAY_OF_WEEK_CHOICES)
    market_condition = models.CharField(max_length=20, choices=MARKET_CONDITION_CHOICES)
    price_within_htf_poi = models.BooleanField(default=False)
    liquidity_analysis = models.CharField(max_length=50, choices=LIQUIDITY_ANALYSIS_CHOICES)
    lower_tf_bos = models.CharField(max_length=50)
    fvg_present = models.BooleanField(default=False)
    ifvg = models.BooleanField(default=False)
    retest_into_ob = models.BooleanField(default=False)
    session_time = models.CharField(max_length=20, choices=SESSION_CHOICES)
    entry_time = models.TimeField(blank=True, null=True)
    setup_present = models.BooleanField(default=False)
    high_impact_news = models.CharField(max_length=200, blank=True)
    entry_trigger = models.CharField(max_length=200)
    behaviour_based_on_previous_moves = models.TextField()
    outcome = models.CharField(max_length=20, choices=BACKTEST_OUTCOME_CHOICES)
    screenshot = models.ImageField(upload_to=get_backtest_upload_path, blank=True, null=True)
    notes = models.TextField(blank=True)
    chasing_long_on = models.BooleanField(default=False)
    overnight = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = 'Backtest Entries'

    def __str__(self):
        return f"{self.pair} - {self.date} - {self.outcome}"


class ChoiceCategory(models.Model):
    """Category for grouping choices"""
    JOURNAL_TYPE_CHOICES = [
        ('after_trade', 'After Trade'),
        ('pre_trade', 'Pre Trade'),
        ('backtest', 'Backtest'),
        ('all', 'All Journals'),
    ]
    
    name = models.CharField(max_length=50, unique=True, help_text='Internal name (e.g., session, market_condition)')
    display_name = models.CharField(max_length=100, help_text='Display name (e.g., Trading Session)')
    description = models.TextField(blank=True, help_text='Description of this category')
    journal_type = models.CharField(max_length=20, choices=JOURNAL_TYPE_CHOICES, default='all', help_text='Which journal type this category belongs to')
    field_name = models.CharField(max_length=50, blank=True, help_text='Form field name to map this category to (e.g., session, bias). Leave blank for dynamic fields.')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text='Display order')
    
    class Meta:
        verbose_name_plural = 'Choice Categories'
        ordering = ['journal_type', 'order', 'display_name']
    
    def __str__(self):
        journal_label = dict(self.JOURNAL_TYPE_CHOICES).get(self.journal_type, self.journal_type)
        return f"{self.display_name} ({journal_label})"


class ChoiceOption(models.Model):
    """Individual option within a choice category"""
    category = models.ForeignKey(ChoiceCategory, on_delete=models.CASCADE, related_name='options')
    value = models.CharField(max_length=100, help_text='Value stored in database')
    display_label = models.CharField(max_length=100, help_text='Label shown to users')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text='Display order within category')
    color = models.CharField(max_length=7, default='#6c757d', help_text='Hex color for badges (optional)')
    
    class Meta:
        ordering = ['category__order', 'category__name', 'order', 'display_label']
        unique_together = [['category', 'value']]
    
    def __str__(self):
        return f"{self.category.display_name}: {self.display_label}"
    
    @classmethod
    def get_choices_for_category(cls, category_name):
        """Get choices tuple list for a category name"""
        try:
            category = ChoiceCategory.objects.get(name=category_name, is_active=True)
            options = cls.objects.filter(category=category, is_active=True).order_by('order', 'display_label')
            return [(opt.value, opt.display_label) for opt in options]
        except ChoiceCategory.DoesNotExist:
            return []


class FilterPreset(models.Model):
    """Saved filter presets for quick access"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='filter_presets')
    name = models.CharField(max_length=100)
    filters = models.JSONField(default=dict, help_text='Stored filter parameters')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']

    def __str__(self):
        return self.name


class LotSizeCalculation(models.Model):
    """Lot size calculation history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lot_size_calculations')
    instrument = models.CharField(max_length=100, help_text='Instrument name (e.g., EUR/USD)')
    account_balance = models.DecimalField(max_digits=12, decimal_places=2)
    account_currency = models.CharField(max_length=10, default='USD', help_text='Account currency')
    risk_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    stop_loss_pips = models.DecimalField(max_digits=8, decimal_places=2)
    calculated_lot_size = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Lot Size Calculations'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.instrument} - {self.calculated_lot_size} lots ({self.created_at.date()})"


class CommonMistakeLog(models.Model):
    """Model for tracking common user mistakes"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('entry', 'Entry Mistakes'),
        ('exit', 'Exit Mistakes'),
        ('risk', 'Risk Management'),
        ('psychology', 'Psychology'),
        ('analysis', 'Market Analysis'),
        ('other', 'Other'),
    ], default='other')
    frequency_count = models.IntegerField(default=1, help_text='How many times this mistake has been observed')
    severity = models.CharField(max_length=20, choices=[
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ], default='medium')
    suggested_solution = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='logged_mistakes')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-frequency_count', '-created_at']
        verbose_name = 'Common Mistake'
        verbose_name_plural = 'Common Mistakes'
    
    def __str__(self):
        return f"{self.title} ({self.frequency_count}x)"


class TradeTemplate(models.Model):
    """Template for quick trade entry creation"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trade_templates')
    name = models.CharField(max_length=100, help_text='Template name')
    pair = models.CharField(max_length=20, blank=True)
    session = models.CharField(max_length=20, blank=True)
    bias = models.CharField(max_length=10, blank=True)
    market_condition = models.CharField(max_length=20, blank=True)
    liquidity_analysis = models.CharField(max_length=50, blank=True)
    risk_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


# Dynamic Field System Models
class JournalField(models.Model):
    """User-defined custom field for journal entries"""
    FIELD_TYPE_CHOICES = [
        ('text', 'Text'),
        ('textarea', 'Long Text'),
        ('number', 'Number'),
        ('decimal', 'Decimal'),
        ('select', 'Select (Single Choice)'),
        ('multiselect', 'Multi-Select (Multiple Choices)'),
        ('checkbox', 'Checkbox'),
        ('date', 'Date'),
        ('time', 'Time'),
        ('datetime', 'Date & Time'),
        ('url', 'URL'),
        ('email', 'Email'),
    ]
    
    JOURNAL_TYPE_CHOICES = [
        ('after_trade', 'After Trade'),
        ('pre_trade', 'Pre Trade'),
        ('backtest', 'Backtest'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_fields')
    journal_type = models.CharField(max_length=20, choices=JOURNAL_TYPE_CHOICES)
    name = models.CharField(max_length=100, help_text='Field name (internal identifier, e.g., "smt_confirmation")')
    display_name = models.CharField(max_length=200, help_text='Display name (e.g., "SMT Confirmation")')
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default='text')
    is_required = models.BooleanField(default=False)
    order = models.IntegerField(default=0, help_text='Display order (lower numbers appear first)')
    is_active = models.BooleanField(default=True)
    help_text = models.TextField(blank=True, help_text='Help text shown to users')
    default_value = models.TextField(blank=True, help_text='Default value for this field')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['journal_type', 'order', 'display_name']
        unique_together = ['user', 'journal_type', 'name']
        verbose_name = 'Journal Field'
        verbose_name_plural = 'Journal Fields'
    
    def __str__(self):
        return f"{self.get_journal_type_display()}: {self.display_name} ({self.user.username})"


class JournalFieldOption(models.Model):
    """Options for select/multi-select fields"""
    field = models.ForeignKey(JournalField, on_delete=models.CASCADE, related_name='options')
    value = models.CharField(max_length=200, help_text='Value stored in database')
    display_label = models.CharField(max_length=200, help_text='Label shown to users')
    order = models.IntegerField(default=0, help_text='Display order')
    color = models.CharField(max_length=7, default='#6c757d', help_text='Hex color for badges')
    
    class Meta:
        ordering = ['field', 'order', 'display_label']
        unique_together = ['field', 'value']
    
    def __str__(self):
        return f"{self.field.display_name}: {self.display_label}"


class JournalFieldValue(models.Model):
    """Stores values for user-defined fields in journal entries"""
    # Generic foreign key approach - store entry type and ID
    entry_type = models.CharField(max_length=20, choices=[
        ('after_trade', 'After Trade'),
        ('pre_trade', 'Pre Trade'),
        ('backtest', 'Backtest'),
    ])
    entry_id = models.IntegerField(help_text='ID of the journal entry')
    field = models.ForeignKey(JournalField, on_delete=models.CASCADE, related_name='values')
    # Store value as text - we'll parse based on field_type
    value_text = models.TextField(blank=True, help_text='Stored as text, parsed by field type')
    value_number = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    value_boolean = models.BooleanField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)
    value_datetime = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['field__order', 'field__display_name']
        unique_together = ['entry_type', 'entry_id', 'field']
        verbose_name = 'Journal Field Value'
        verbose_name_plural = 'Journal Field Values'
    
    def __str__(self):
        return f"{self.field.display_name}: {self.get_value_display()}"
    
    def get_value_display(self):
        """Get the value formatted for display based on field type"""
        if self.field.field_type == 'checkbox':
            return 'Yes' if self.value_boolean else 'No'
        elif self.field.field_type in ['number', 'decimal']:
            return str(self.value_number) if self.value_number is not None else ''
        elif self.field.field_type == 'date':
            return str(self.value_date) if self.value_date else ''
        elif self.field.field_type == 'datetime':
            return str(self.value_datetime) if self.value_datetime else ''
        elif self.field.field_type == 'multiselect':
            # Multi-select values are stored as comma-separated in value_text
            return self.value_text
        else:
            return self.value_text
    
    def set_value(self, value):
        """Set the value based on field type"""
        if self.field.field_type == 'checkbox':
            self.value_boolean = bool(value)
            self.value_text = str(value)
        elif self.field.field_type in ['number', 'decimal']:
            try:
                self.value_number = Decimal(str(value))
                self.value_text = str(value)
            except:
                self.value_text = str(value)
        elif self.field.field_type == 'date':
            if isinstance(value, str):
                from django.utils.dateparse import parse_date
                self.value_date = parse_date(value)
            else:
                self.value_date = value
            self.value_text = str(value) if value else ''
        elif self.field.field_type == 'datetime':
            if isinstance(value, str):
                from django.utils.dateparse import parse_datetime
                self.value_datetime = parse_datetime(value)
            else:
                self.value_datetime = value
            self.value_text = str(value) if value else ''
        else:
            self.value_text = str(value) if value else ''

