from django.contrib import admin
from .models import (
    AfterTradeEntry, PreTradeEntry, BacktestEntry, 
    StrategyTag, FilterPreset, LotSizeCalculation,
    ChoiceCategory, ChoiceOption, CommonMistakeLog, TradeTemplate
)


@admin.register(ChoiceCategory)
class ChoiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'journal_type', 'field_name', 'is_active', 'order']
    list_filter = ['journal_type', 'is_active']
    search_fields = ['name', 'display_name', 'field_name']
    ordering = ['journal_type', 'order', 'display_name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Journal Configuration', {
            'fields': ('journal_type', 'field_name'),
            'description': 'Select which journal type this category belongs to. If field_name is set, it will map to that specific form field. Leave field_name blank to create a new dynamic field.'
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
    )


@admin.register(ChoiceOption)
class ChoiceOptionAdmin(admin.ModelAdmin):
    list_display = ['display_label', 'category', 'value', 'is_active', 'order']
    list_filter = ['category', 'is_active']
    search_fields = ['display_label', 'value', 'category__name']
    ordering = ['category__order', 'order', 'display_label']
    fieldsets = (
        ('Basic Info', {
            'fields': ('category', 'value', 'display_label', 'description')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order', 'color')
        }),
    )


@admin.register(StrategyTag)
class StrategyTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    search_fields = ['name']


@admin.register(AfterTradeEntry)
class AfterTradeEntryAdmin(admin.ModelAdmin):
    list_display = ['pair', 'date', 'user', 'outcome', 'poi_quality_score', 'rr_ratio', 'created_at']
    list_filter = ['outcome', 'bias', 'session', 'market_condition', 'user', 'date', 'strategy_tags']
    search_fields = ['pair', 'observations', 'ai_summary', 'user__username']
    readonly_fields = ['rr_ratio', 'is_win', 'created_at', 'updated_at', 'summary_generated_at', 'ai_summary']
    filter_horizontal = ['strategy_tags']
    fieldsets = (
        ('Trade Info', {
            'fields': ('user', 'pair', 'date', 'session', 'bias', 'time_of_entry')
        }),
        ('Market Analysis', {
            'fields': ('market_condition', 'liquidity_analysis', 'lower_tf_confirmation', 'htf_mitigation')
        }),
        ('Trade Execution', {
            'fields': ('entry_quality', 'poi_quality_score', 'poi_performance', 'predicted_directional_bias')
        }),
        ('Risk & Outcome', {
            'fields': ('risk_percentage', 'risk_pips', 'reward_pips', 'rr_ratio', 'outcome', 'is_win')
        }),
        ('Market Behavior', {
            'fields': ('market_behaviour', 'risk_management_applied', 'high_impact_news', 'major_impact_news')
        }),
        ('Evaluation', {
            'fields': ('discipline_score', 'observations')
        }),
        ('Media & Tags', {
            'fields': ('chart_image', 'strategy_tags')
        }),
        ('AI Summary', {
            'fields': ('ai_summary', 'summary_generated_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PreTradeEntry)
class PreTradeEntryAdmin(admin.ModelAdmin):
    list_display = ['pair', 'date', 'user', 'bias', 'trade_taken', 'all_conditions_met']
    list_filter = ['bias', 'trade_taken', 'all_conditions_met', 'market_condition', 'user', 'date']
    search_fields = ['pair', 'notes', 'reason_for_taking_or_not', 'user__username']


@admin.register(BacktestEntry)
class BacktestEntryAdmin(admin.ModelAdmin):
    list_display = ['pair', 'date', 'user', 'htf_bias', 'outcome', 'day_of_week']
    list_filter = ['outcome', 'htf_bias', 'market_condition', 'day_of_week', 'user', 'date']
    search_fields = ['pair', 'notes', 'entry_trigger', 'user__username']


@admin.register(FilterPreset)
class FilterPresetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name', 'user__username']


@admin.register(LotSizeCalculation)
class LotSizeCalculationAdmin(admin.ModelAdmin):
    list_display = ['user', 'instrument', 'account_balance', 'risk_percentage', 'calculated_lot_size', 'created_at']
    list_filter = ['instrument', 'created_at', 'user']
    search_fields = ['user__username', 'instrument']
    readonly_fields = ['created_at']


@admin.register(CommonMistakeLog)
class CommonMistakeLogAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'severity', 'frequency_count', 'created_by', 'is_active', 'created_at']
    list_filter = ['category', 'severity', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'suggested_solution']
    list_editable = ['is_active', 'severity']
    fieldsets = (
        ('Mistake Info', {
            'fields': ('title', 'description', 'category', 'severity')
        }),
        ('Tracking', {
            'fields': ('frequency_count', 'is_active', 'created_by')
        }),
        ('Solution', {
            'fields': ('suggested_solution',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Restrict to superusers or allow all"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Non-superusers can only see their own mistakes
            qs = qs.filter(created_by=request.user)
        return qs


@admin.register(TradeTemplate)
class TradeTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'pair', 'session', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['name', 'pair', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

