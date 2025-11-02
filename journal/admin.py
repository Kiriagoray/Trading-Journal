from django.contrib import admin
from .models import (
    AfterTradeEntry, PreTradeEntry, BacktestEntry, 
    StrategyTag, FilterPreset, LotSizeCalculation,
    ChoiceCategory, ChoiceOption
)


@admin.register(ChoiceCategory)
class ChoiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'display_name']
    ordering = ['order', 'display_name']


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

