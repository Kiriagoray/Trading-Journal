from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


# Choice constants
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


class Entry(models.Model):
    """Legacy entry model"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entries')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Entries'

    def __str__(self):
        return self.title


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
    chart_image = models.ImageField(upload_to='journal/after_trade/', blank=True, null=True)
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
    setup_image = models.ImageField(upload_to='journal/pre_trade/', blank=True, null=True)
    all_conditions_met = models.BooleanField(default=False)
    trade_taken = models.BooleanField(default=False)
    reason_for_taking_or_not = models.TextField()
    outcome_image = models.ImageField(upload_to='journal/pre_trade_outcomes/', blank=True, null=True)
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
    screenshot = models.ImageField(upload_to='journal/backtesting/', blank=True, null=True)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lot_calculations')
    account_balance = models.DecimalField(max_digits=12, decimal_places=2)
    risk_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    stop_loss_pips = models.DecimalField(max_digits=8, decimal_places=2)
    instrument = models.CharField(max_length=20)
    calculated_lot_size = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Lot Size Calculations'

    def __str__(self):
        return f"{self.instrument} - {self.calculated_lot_size} lots ({self.created_at.date()})"

