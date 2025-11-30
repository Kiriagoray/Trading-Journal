from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg, Sum, Case, When, IntegerField, Max
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings
from datetime import datetime, timedelta
from urllib.parse import urlencode
import csv
from .models import (
    AfterTradeEntry, PreTradeEntry, BacktestEntry, StrategyTag, FilterPreset, 
    LotSizeCalculation, JournalField, JournalFieldOption, JournalFieldValue
)


# Authentication Views
def register(request):
    """User registration"""
    from .forms import UserRegistrationForm
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'journal/register.html', {'form': form})


@login_required
def dashboard(request):
    """Dashboard view with KPIs and charts"""
    # Get user's entries
    after_trades = AfterTradeEntry.objects.filter(user=request.user)
    
    # Calculate KPIs
    total_entries = after_trades.count()
    total_trades = after_trades.count()
    wins = after_trades.filter(outcome='win').count()
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    # Correct bias percentage
    correct_bias = after_trades.filter(predicted_directional_bias='correct').count()
    correct_bias_pct = (correct_bias / total_trades * 100) if total_trades > 0 else 0
    
    # Avg POI score
    avg_poi_score = after_trades.aggregate(Avg('poi_quality_score'))['poi_quality_score__avg'] or 0
    
    # Current streak
    recent_trades = after_trades.order_by('-date', '-time_of_entry')[:10]
    current_streak = 0
    streak_abs = 0
    streak_type = ''
    if recent_trades:
        first_outcome = recent_trades[0].outcome
        for trade in recent_trades:
            if trade.outcome == first_outcome:
                current_streak += 1
            else:
                break
        streak_abs = abs(current_streak)
        if first_outcome == 'loss':
            streak_type = 'loss'
        else:
            streak_type = 'win'
    
    # Last 7 days win rate
    week_ago = timezone.now().date() - timedelta(days=7)
    week_trades = after_trades.filter(date__gte=week_ago)
    week_wins = week_trades.filter(outcome='win').count()
    week_win_rate = (week_wins / week_trades.count() * 100) if week_trades.count() > 0 else 0
    
    # Chart data (simplified) - ensure JSON serializable
    chart_data = {
        'win_rate_weeks': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'win_rate_values': [float(win_rate)] * 4,
        'market_conditions': ['Trending Up', 'Trending Down', 'Consolidating'],
        'market_condition_counts': [
            int(after_trades.filter(market_condition='Trending Up').count()),
            int(after_trades.filter(market_condition='Trending Down').count()),
            int(after_trades.filter(market_condition='Consolidating').count()),
        ],
        'poi_months': ['Jan', 'Feb', 'Mar'],
        'poi_avg_scores': [float(avg_poi_score)] * 3,
    }
    
    # Recent entries
    recent_after = after_trades.order_by('-date')[:5]
    recent_pre = PreTradeEntry.objects.filter(user=request.user).order_by('-date')[:5]
    recent_backtest = BacktestEntry.objects.filter(user=request.user).order_by('-date')[:5]
    
    context = {
        'total_entries': total_entries,
        'total_trades': total_trades,
        'win_rate': round(win_rate, 1),
        'correct_bias_pct': round(correct_bias_pct, 1),
        'avg_poi_score': round(avg_poi_score, 1),
        'streak_abs': streak_abs,
        'streak_type': streak_type,
        'week_win_rate': round(week_win_rate, 1),
        'chart_data': chart_data,
        'recent_after': recent_after,
        'recent_pre': recent_pre,
        'recent_backtest': recent_backtest,
    }
    
    return render(request, 'journal/dashboard.html', context)


# After Trade Views
@login_required
def after_trade_list(request):
    """List after trade entries with advanced filtering, search, and sorting"""
    from .utils import get_user_journal_fields, search_entries_with_custom_fields, filter_entries_by_custom_field
    from .models import JournalFieldValue
    from datetime import datetime
    
    entries = AfterTradeEntry.objects.filter(user=request.user)
    
    # Get custom fields for this journal type
    custom_fields = get_user_journal_fields(request.user, 'after_trade')
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        entries = search_entries_with_custom_fields(entries, search, 'after_trade', request.user)
    
    # System field filters
    pair_filter = request.GET.get('pair', '').strip()
    if pair_filter:
        entries = entries.filter(pair__icontains=pair_filter)
    
    outcome_filter = request.GET.get('outcome', '').strip()
    if outcome_filter:
        entries = entries.filter(outcome=outcome_filter)
    
    date_from = request.GET.get('date_from', '').strip()
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            entries = entries.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    date_to = request.GET.get('date_to', '').strip()
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            entries = entries.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Custom field filters
    for field in custom_fields:
        field_name = f'custom_{field.name}'
        filter_value = request.GET.get(field_name, '').strip()
        
        if filter_value:
            if field.field_type in ['select', 'multi_select']:
                entries = filter_entries_by_custom_field(entries, field, filter_value, 'after_trade')
            elif field.field_type in ['number', 'decimal']:
                min_val = request.GET.get(f'{field_name}_min', '').strip()
                max_val = request.GET.get(f'{field_name}_max', '').strip()
                if min_val or max_val:
                    entry_ids = list(entries.values_list('id', flat=True))
                    if entry_ids:
                        field_values = JournalFieldValue.objects.filter(
                            field=field,
                            entry_id__in=entry_ids
                        )
                        if min_val:
                            try:
                                field_values = field_values.filter(value_number__gte=float(min_val))
                            except ValueError:
                                pass
                        if max_val:
                            try:
                                field_values = field_values.filter(value_number__lte=float(max_val))
                            except ValueError:
                                pass
                        matching_ids = list(field_values.values_list('entry_id', flat=True))
                        entries = entries.filter(id__in=matching_ids)
            elif field.field_type == 'date':
                date_min = request.GET.get(f'{field_name}_min', '').strip()
                date_max = request.GET.get(f'{field_name}_max', '').strip()
                if date_min or date_max:
                    entry_ids = list(entries.values_list('id', flat=True))
                    if entry_ids:
                        field_values = JournalFieldValue.objects.filter(
                            field=field,
                            entry_id__in=entry_ids
                        )
                        if date_min:
                            try:
                                date_min_obj = datetime.strptime(date_min, '%Y-%m-%d').date()
                                field_values = field_values.filter(value_date__gte=date_min_obj)
                            except ValueError:
                                pass
                        if date_max:
                            try:
                                date_max_obj = datetime.strptime(date_max, '%Y-%m-%d').date()
                                field_values = field_values.filter(value_date__lte=date_max_obj)
                            except ValueError:
                                pass
                        matching_ids = list(field_values.values_list('entry_id', flat=True))
                        entries = entries.filter(id__in=matching_ids)
            elif field.field_type == 'checkbox':
                if filter_value.lower() in ['true', '1', 'yes']:
                    entry_ids = list(entries.values_list('id', flat=True))
                    if entry_ids:
                        matching_ids = list(JournalFieldValue.objects.filter(
                            field=field,
                            entry_id__in=entry_ids,
                            value_boolean=True
                        ).values_list('entry_id', flat=True))
                        entries = entries.filter(id__in=matching_ids)
    
    # Sorting
    sort_by = request.GET.get('sort', 'date_desc').strip()
    sort_field = None
    sort_order = 'desc'
    
    if sort_by:
        if '_' in sort_by:
            sort_field_name, sort_order = sort_by.rsplit('_', 1)
        else:
            sort_field_name = sort_by
            sort_order = 'desc'
        
        if sort_field_name == 'date':
            entries = entries.order_by(f'-date' if sort_order == 'desc' else 'date')
        elif sort_field_name == 'pair':
            entries = entries.order_by(f'-pair' if sort_order == 'desc' else 'pair')
        elif sort_field_name == 'outcome':
            entries = entries.order_by(f'-outcome' if sort_order == 'desc' else 'outcome')
        elif sort_field_name.startswith('custom_'):
            # Custom field sorting
            field_name = sort_field_name.replace('custom_', '')
            try:
                field = custom_fields.get(name=field_name)
                if field and field.field_type in ['text', 'textarea', 'select', 'number', 'decimal', 'date']:
                    entry_ids = list(entries.values_list('id', flat=True))
                    if entry_ids:
                        field_values = JournalFieldValue.objects.filter(
                            field=field,
                            entry_id__in=entry_ids
                        )
                        if field.field_type in ['number', 'decimal']:
                            sorted_values = field_values.order_by(f'-value_number' if sort_order == 'desc' else 'value_number')
                        elif field.field_type == 'date':
                            sorted_values = field_values.order_by(f'-value_date' if sort_order == 'desc' else 'value_date')
                        else:
                            sorted_values = field_values.order_by(f'-value_text' if sort_order == 'desc' else 'value_text')
                        sorted_ids = list(sorted_values.values_list('entry_id', flat=True))
                        # Preserve order by creating a mapping
                        id_order = {eid: idx for idx, eid in enumerate(sorted_ids)}
                        entries_list = list(entries)
                        entries_list.sort(key=lambda e: id_order.get(e.id, 999999))
                        # Convert back to queryset (this is a limitation, but works for pagination)
                        entries = entries.filter(id__in=sorted_ids)
            except Exception:
                pass
    
    # Get unique pairs for filter dropdown
    unique_pairs = sorted(set(AfterTradeEntry.objects.filter(user=request.user).values_list('pair', flat=True).distinct()))
    
    # Pagination
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Build filter context
    filters = {
        'search': search,
        'pair': pair_filter,
        'outcome': outcome_filter,
        'date_from': date_from,
        'date_to': date_to,
        'sort': sort_by,
    }
    
    # Add custom field filter values
    for field in custom_fields:
        field_name = f'custom_{field.name}'
        filters[field_name] = request.GET.get(field_name, '').strip()
        if field.field_type in ['number', 'decimal', 'date']:
            filters[f'{field_name}_min'] = request.GET.get(f'{field_name}_min', '').strip()
            filters[f'{field_name}_max'] = request.GET.get(f'{field_name}_max', '').strip()
    
    context = {
        'page_obj': page_obj,
        'filters': filters,
        'custom_fields': custom_fields,
        'unique_pairs': unique_pairs,
        'total_results': paginator.count,
    }
    return render(request, 'journal/after_trade_list.html', context)


@login_required
def after_trade_create(request):
    """Create after trade entry"""
    from .forms import AfterTradeEntryForm
    from .utils import save_field_value_for_entry, get_user_journal_fields
    
    if request.method == 'POST':
        form = AfterTradeEntryForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Save custom field values
            custom_fields = get_user_journal_fields(request.user, 'after_trade')
            for field in custom_fields:
                field_key = f'custom_{field.name}'
                if field_key in form.cleaned_data:
                    value = form.cleaned_data[field_key]
                    save_field_value_for_entry(entry, field, value)
            
            # Auto-generate AI summary
            try:
                from .services import TradeSummaryGenerator
                TradeSummaryGenerator.generate_and_save_summary(entry)
                messages.success(request, 'After Trade entry created successfully! AI summary generated.')
            except Exception as e:
                messages.success(request, 'After Trade entry created successfully!')
            return redirect('after_trade_detail', pk=entry.pk)
    else:
        form = AfterTradeEntryForm(user=request.user)
    return render(request, 'journal/after_trade_form.html', {'form': form})


@login_required
def after_trade_detail(request, pk):
    """View after trade entry detail"""
    from .utils import get_all_field_values_for_entry
    entry = get_object_or_404(AfterTradeEntry, pk=pk, user=request.user)
    # Get related entries (same pair)
    related = AfterTradeEntry.objects.filter(
        user=request.user,
        pair=entry.pair
    ).exclude(pk=entry.pk).order_by('-date')[:5]
    # Get custom field values
    custom_field_values = get_all_field_values_for_entry(entry)
    return render(request, 'journal/after_trade_detail.html', {
        'entry': entry,
        'related': related,
        'custom_field_values': custom_field_values
    })


@login_required
def after_trade_edit(request, pk):
    """Edit after trade entry"""
    from .forms import AfterTradeEntryForm
    from .utils import save_field_value_for_entry, get_user_journal_fields
    entry = get_object_or_404(AfterTradeEntry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AfterTradeEntryForm(request.POST, request.FILES, instance=entry, user=request.user)
        if form.is_valid():
            entry = form.save()
            form.save_m2m()
            
            # Save custom field values
            custom_fields = get_user_journal_fields(request.user, 'after_trade')
            for field in custom_fields:
                field_key = f'custom_{field.name}'
                if field_key in form.cleaned_data:
                    value = form.cleaned_data[field_key]
                    save_field_value_for_entry(entry, field, value)
            
            messages.success(request, 'Entry updated successfully!')
            return redirect('after_trade_detail', pk=entry.pk)
    else:
        form = AfterTradeEntryForm(instance=entry, user=request.user)
    return render(request, 'journal/after_trade_form.html', {'form': form, 'entry': entry})


@login_required
def after_trade_delete(request, pk):
    """Delete after trade entry"""
    entry = get_object_or_404(AfterTradeEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Entry deleted successfully!')
        return redirect('after_trade_list')
    return render(request, 'journal/after_trade_delete.html', {'entry': entry})


@login_required
def regenerate_summary(request, pk):
    """Regenerate AI summary for a trade entry"""
    from .services import TradeSummaryGenerator
    entry = get_object_or_404(AfterTradeEntry, pk=pk, user=request.user)
    TradeSummaryGenerator.generate_and_save_summary(entry, regenerate=True)
    messages.success(request, 'AI summary regenerated!')
    return redirect('after_trade_detail', pk=entry.pk)


@login_required
def after_trade_export_csv(request):
    """Export after trade entries to CSV"""
    entries = AfterTradeEntry.objects.filter(user=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="after_trade_entries.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Pair', 'Session', 'Bias', 'Outcome', 'POI Score', 'RR Ratio', 'Risk %', 'Observations'])
    
    for entry in entries:
        writer.writerow([
            entry.date,
            entry.pair,
            entry.session,
            entry.bias,
            entry.outcome,
            entry.poi_quality_score,
            entry.rr_ratio or '',
            entry.risk_percentage,
            entry.observations[:100]  # Truncate long observations
        ])
    
    return response


# Pre Trade Views
@login_required
def pre_trade_list(request):
    """List pre trade entries with advanced filtering, search, and sorting"""
    from .utils import get_user_journal_fields, search_entries_with_custom_fields, filter_entries_by_custom_field
    from .models import JournalFieldValue
    from datetime import datetime
    
    entries = PreTradeEntry.objects.filter(user=request.user)
    
    # Get custom fields for this journal type
    custom_fields = get_user_journal_fields(request.user, 'pre_trade')
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        entries = search_entries_with_custom_fields(entries, search, 'pre_trade', request.user)
    
    # System field filters
    pair_filter = request.GET.get('pair', '').strip()
    if pair_filter:
        entries = entries.filter(pair__icontains=pair_filter)
    
    bias_filter = request.GET.get('bias', '').strip()
    if bias_filter:
        entries = entries.filter(bias=bias_filter)
    
    date_from = request.GET.get('date_from', '').strip()
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            entries = entries.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    date_to = request.GET.get('date_to', '').strip()
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            entries = entries.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Custom field filters (same logic as after_trade_list)
    for field in custom_fields:
        field_name = f'custom_{field.name}'
        filter_value = request.GET.get(field_name, '').strip()
        
        if filter_value:
            if field.field_type in ['select', 'multi_select']:
                entries = filter_entries_by_custom_field(entries, field, filter_value, 'pre_trade')
            elif field.field_type in ['number', 'decimal']:
                min_val = request.GET.get(f'{field_name}_min', '').strip()
                max_val = request.GET.get(f'{field_name}_max', '').strip()
                if min_val or max_val:
                    entry_ids = list(entries.values_list('id', flat=True))
                    if entry_ids:
                        field_values = JournalFieldValue.objects.filter(
                            field=field,
                            entry_id__in=entry_ids
                        )
                        if min_val:
                            try:
                                field_values = field_values.filter(value_number__gte=float(min_val))
                            except ValueError:
                                pass
                        if max_val:
                            try:
                                field_values = field_values.filter(value_number__lte=float(max_val))
                            except ValueError:
                                pass
                        matching_ids = list(field_values.values_list('entry_id', flat=True))
                        entries = entries.filter(id__in=matching_ids)
            elif field.field_type == 'date':
                date_min = request.GET.get(f'{field_name}_min', '').strip()
                date_max = request.GET.get(f'{field_name}_max', '').strip()
                if date_min or date_max:
                    entry_ids = list(entries.values_list('id', flat=True))
                    if entry_ids:
                        field_values = JournalFieldValue.objects.filter(
                            field=field,
                            entry_id__in=entry_ids
                        )
                        if date_min:
                            try:
                                date_min_obj = datetime.strptime(date_min, '%Y-%m-%d').date()
                                field_values = field_values.filter(value_date__gte=date_min_obj)
                            except ValueError:
                                pass
                        if date_max:
                            try:
                                date_max_obj = datetime.strptime(date_max, '%Y-%m-%d').date()
                                field_values = field_values.filter(value_date__lte=date_max_obj)
                            except ValueError:
                                pass
                        matching_ids = list(field_values.values_list('entry_id', flat=True))
                        entries = entries.filter(id__in=matching_ids)
            elif field.field_type == 'checkbox':
                if filter_value.lower() in ['true', '1', 'yes']:
                    entry_ids = list(entries.values_list('id', flat=True))
                    if entry_ids:
                        matching_ids = list(JournalFieldValue.objects.filter(
                            field=field,
                            entry_id__in=entry_ids,
                            value_boolean=True
                        ).values_list('entry_id', flat=True))
                        entries = entries.filter(id__in=matching_ids)
    
    # Sorting
    sort_by = request.GET.get('sort', 'date_desc').strip()
    if sort_by:
        if '_' in sort_by:
            sort_field_name, sort_order = sort_by.rsplit('_', 1)
        else:
            sort_field_name = sort_by
            sort_order = 'desc'
        
        if sort_field_name == 'date':
            entries = entries.order_by(f'-date' if sort_order == 'desc' else 'date')
        elif sort_field_name == 'pair':
            entries = entries.order_by(f'-pair' if sort_order == 'desc' else 'pair')
        elif sort_field_name == 'bias':
            entries = entries.order_by(f'-bias' if sort_order == 'desc' else 'bias')
    
    # Get unique pairs for filter dropdown
    unique_pairs = sorted(set(PreTradeEntry.objects.filter(user=request.user).values_list('pair', flat=True).distinct()))
    
    # Pagination
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Build filter context
    filters = {
        'search': search,
        'pair': pair_filter,
        'bias': bias_filter,
        'date_from': date_from,
        'date_to': date_to,
        'sort': sort_by,
    }
    
    # Add custom field filter values
    for field in custom_fields:
        field_name = f'custom_{field.name}'
        filters[field_name] = request.GET.get(field_name, '').strip()
        if field.field_type in ['number', 'decimal', 'date']:
            filters[f'{field_name}_min'] = request.GET.get(f'{field_name}_min', '').strip()
            filters[f'{field_name}_max'] = request.GET.get(f'{field_name}_max', '').strip()
    
    context = {
        'page_obj': page_obj,
        'filters': filters,
        'custom_fields': custom_fields,
        'unique_pairs': unique_pairs,
        'total_results': paginator.count,
    }
    return render(request, 'journal/pre_trade_list.html', context)


@login_required
def pre_trade_create(request):
    """Create pre trade entry"""
    from .forms import PreTradeEntryForm
    from .utils import save_field_value_for_entry, get_user_journal_fields
    
    if request.method == 'POST':
        form = PreTradeEntryForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            
            # Save custom field values
            custom_fields = get_user_journal_fields(request.user, 'pre_trade')
            for field in custom_fields:
                field_key = f'custom_{field.name}'
                if field_key in form.cleaned_data:
                    value = form.cleaned_data[field_key]
                    save_field_value_for_entry(entry, field, value)
            
            messages.success(request, 'Pre Trade entry created successfully!')
            return redirect('pre_trade_detail', pk=entry.pk)
    else:
        form = PreTradeEntryForm(user=request.user)
    return render(request, 'journal/pre_trade_form.html', {'form': form})


@login_required
def pre_trade_detail(request, pk):
    """View pre trade entry detail"""
    from .utils import get_all_field_values_for_entry
    entry = get_object_or_404(PreTradeEntry, pk=pk, user=request.user)
    # Get custom field values
    custom_field_values = get_all_field_values_for_entry(entry)
    return render(request, 'journal/pre_trade_detail.html', {
        'entry': entry,
        'custom_field_values': custom_field_values
    })


@login_required
def pre_trade_edit(request, pk):
    """Edit pre trade entry"""
    from .forms import PreTradeEntryForm
    from .utils import save_field_value_for_entry, get_user_journal_fields
    entry = get_object_or_404(PreTradeEntry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PreTradeEntryForm(request.POST, request.FILES, instance=entry, user=request.user)
        if form.is_valid():
            entry = form.save()
            
            # Save custom field values
            custom_fields = get_user_journal_fields(request.user, 'pre_trade')
            for field in custom_fields:
                field_key = f'custom_{field.name}'
                if field_key in form.cleaned_data:
                    value = form.cleaned_data[field_key]
                    save_field_value_for_entry(entry, field, value)
            
            messages.success(request, 'Entry updated successfully!')
            return redirect('pre_trade_detail', pk=entry.pk)
    else:
        form = PreTradeEntryForm(instance=entry, user=request.user)
    return render(request, 'journal/pre_trade_form.html', {'form': form, 'entry': entry})


@login_required
def pre_trade_delete(request, pk):
    """Delete pre trade entry"""
    entry = get_object_or_404(PreTradeEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Entry deleted successfully!')
        return redirect('pre_trade_list')
    return render(request, 'journal/pre_trade_delete.html', {'entry': entry})


@login_required
def pre_trade_export_csv(request):
    """Export pre trade entries to CSV"""
    entries = PreTradeEntry.objects.filter(user=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pre_trade_entries.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Pair', 'Bias', 'Trade Taken', 'All Conditions Met', 'Notes'])
    
    for entry in entries:
        writer.writerow([
            entry.date,
            entry.pair,
            entry.bias,
            entry.trade_taken,
            entry.all_conditions_met,
            entry.notes[:100]
        ])
    
    return response


# Backtest Views
@login_required
def backtest_list(request):
    """List backtest entries with advanced filtering, search, and sorting"""
    from .utils import get_user_journal_fields, search_entries_with_custom_fields, filter_entries_by_custom_field
    from .models import JournalFieldValue
    from datetime import datetime
    
    entries = BacktestEntry.objects.filter(user=request.user)
    
    # Get custom fields for this journal type
    custom_fields = get_user_journal_fields(request.user, 'backtest')
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        entries = search_entries_with_custom_fields(entries, search, 'backtest', request.user)
    
    # System field filters
    pair_filter = request.GET.get('pair', '').strip()
    if pair_filter:
        entries = entries.filter(pair__icontains=pair_filter)
    
    bias_filter = request.GET.get('bias', '').strip()
    if bias_filter:
        entries = entries.filter(htf_bias=bias_filter)
    
    date_from = request.GET.get('date_from', '').strip()
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            entries = entries.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    date_to = request.GET.get('date_to', '').strip()
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            entries = entries.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Custom field filters (same logic as after_trade_list)
    for field in custom_fields:
        field_name = f'custom_{field.name}'
        filter_value = request.GET.get(field_name, '').strip()
        
        if filter_value:
            if field.field_type in ['select', 'multi_select']:
                entries = filter_entries_by_custom_field(entries, field, filter_value, 'backtest')
            elif field.field_type in ['number', 'decimal']:
                min_val = request.GET.get(f'{field_name}_min', '').strip()
                max_val = request.GET.get(f'{field_name}_max', '').strip()
                if min_val or max_val:
                    entry_ids = list(entries.values_list('id', flat=True))
                    if entry_ids:
                        field_values = JournalFieldValue.objects.filter(
                            field=field,
                            entry_id__in=entry_ids
                        )
                        if min_val:
                            try:
                                field_values = field_values.filter(value_number__gte=float(min_val))
                            except ValueError:
                                pass
                        if max_val:
                            try:
                                field_values = field_values.filter(value_number__lte=float(max_val))
                            except ValueError:
                                pass
                        matching_ids = list(field_values.values_list('entry_id', flat=True))
                        entries = entries.filter(id__in=matching_ids)
            elif field.field_type == 'date':
                date_min = request.GET.get(f'{field_name}_min', '').strip()
                date_max = request.GET.get(f'{field_name}_max', '').strip()
                if date_min or date_max:
                    entry_ids = list(entries.values_list('id', flat=True))
                    if entry_ids:
                        field_values = JournalFieldValue.objects.filter(
                            field=field,
                            entry_id__in=entry_ids
                        )
                        if date_min:
                            try:
                                date_min_obj = datetime.strptime(date_min, '%Y-%m-%d').date()
                                field_values = field_values.filter(value_date__gte=date_min_obj)
                            except ValueError:
                                pass
                        if date_max:
                            try:
                                date_max_obj = datetime.strptime(date_max, '%Y-%m-%d').date()
                                field_values = field_values.filter(value_date__lte=date_max_obj)
                            except ValueError:
                                pass
                        matching_ids = list(field_values.values_list('entry_id', flat=True))
                        entries = entries.filter(id__in=matching_ids)
            elif field.field_type == 'checkbox':
                if filter_value.lower() in ['true', '1', 'yes']:
                    entry_ids = list(entries.values_list('id', flat=True))
                    if entry_ids:
                        matching_ids = list(JournalFieldValue.objects.filter(
                            field=field,
                            entry_id__in=entry_ids,
                            value_boolean=True
                        ).values_list('entry_id', flat=True))
                        entries = entries.filter(id__in=matching_ids)
    
    # Sorting
    sort_by = request.GET.get('sort', 'date_desc').strip()
    if sort_by:
        if '_' in sort_by:
            sort_field_name, sort_order = sort_by.rsplit('_', 1)
        else:
            sort_field_name = sort_by
            sort_order = 'desc'
        
        if sort_field_name == 'date':
            entries = entries.order_by(f'-date' if sort_order == 'desc' else 'date')
        elif sort_field_name == 'pair':
            entries = entries.order_by(f'-pair' if sort_order == 'desc' else 'pair')
        elif sort_field_name == 'bias':
            entries = entries.order_by(f'-htf_bias' if sort_order == 'desc' else 'htf_bias')
    
    # Get unique pairs for filter dropdown
    unique_pairs = sorted(set(BacktestEntry.objects.filter(user=request.user).values_list('pair', flat=True).distinct()))
    
    # Pagination
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Build filter context
    filters = {
        'search': search,
        'pair': pair_filter,
        'bias': bias_filter,
        'date_from': date_from,
        'date_to': date_to,
        'sort': sort_by,
    }
    
    # Add custom field filter values
    for field in custom_fields:
        field_name = f'custom_{field.name}'
        filters[field_name] = request.GET.get(field_name, '').strip()
        if field.field_type in ['number', 'decimal', 'date']:
            filters[f'{field_name}_min'] = request.GET.get(f'{field_name}_min', '').strip()
            filters[f'{field_name}_max'] = request.GET.get(f'{field_name}_max', '').strip()
    
    context = {
        'page_obj': page_obj,
        'filters': filters,
        'custom_fields': custom_fields,
        'unique_pairs': unique_pairs,
        'total_results': paginator.count,
    }
    return render(request, 'journal/backtest_list.html', context)


@login_required
def backtest_create(request):
    """Create backtest entry"""
    from .forms import BacktestEntryForm
    from .utils import save_field_value_for_entry, get_user_journal_fields
    
    if request.method == 'POST':
        form = BacktestEntryForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            
            # Save custom field values
            custom_fields = get_user_journal_fields(request.user, 'backtest')
            for field in custom_fields:
                field_key = f'custom_{field.name}'
                if field_key in form.cleaned_data:
                    value = form.cleaned_data[field_key]
                    save_field_value_for_entry(entry, field, value)
            
            messages.success(request, 'Backtest entry created successfully!')
            return redirect('backtest_detail', pk=entry.pk)
    else:
        form = BacktestEntryForm(user=request.user)
    return render(request, 'journal/backtest_form.html', {'form': form})


@login_required
def backtest_detail(request, pk):
    """View backtest entry detail"""
    from .utils import get_all_field_values_for_entry
    entry = get_object_or_404(BacktestEntry, pk=pk, user=request.user)
    # Get custom field values
    custom_field_values = get_all_field_values_for_entry(entry)
    return render(request, 'journal/backtest_detail.html', {
        'entry': entry,
        'custom_field_values': custom_field_values
    })


@login_required
def backtest_edit(request, pk):
    """Edit backtest entry"""
    from .forms import BacktestEntryForm
    from .utils import save_field_value_for_entry, get_user_journal_fields
    entry = get_object_or_404(BacktestEntry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BacktestEntryForm(request.POST, request.FILES, instance=entry, user=request.user)
        if form.is_valid():
            entry = form.save()
            
            # Save custom field values
            custom_fields = get_user_journal_fields(request.user, 'backtest')
            for field in custom_fields:
                field_key = f'custom_{field.name}'
                if field_key in form.cleaned_data:
                    value = form.cleaned_data[field_key]
                    save_field_value_for_entry(entry, field, value)
            
            messages.success(request, 'Entry updated successfully!')
            return redirect('backtest_detail', pk=entry.pk)
    else:
        form = BacktestEntryForm(instance=entry, user=request.user)
    return render(request, 'journal/backtest_form.html', {'form': form, 'entry': entry})


@login_required
def backtest_delete(request, pk):
    """Delete backtest entry"""
    entry = get_object_or_404(BacktestEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Entry deleted successfully!')
        return redirect('backtest_list')
    return render(request, 'journal/backtest_delete.html', {'entry': entry})


@login_required
def backtest_export_csv(request):
    """Export backtest entries to CSV"""
    entries = BacktestEntry.objects.filter(user=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="backtest_entries.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Pair', 'Outcome', 'Strategy Name', 'Notes'])
    
    for entry in entries:
        writer.writerow([
            entry.date,
            entry.pair,
            entry.outcome,
            entry.strategy_name or '',
            entry.notes[:100]
        ])
    
    return response


# Calendar and Daily Summary
@login_required
def journal_calendar(request):
    """Calendar view of all journal entries"""
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    
    after_trades = AfterTradeEntry.objects.filter(user=request.user, date__year=year, date__month=month)
    pre_trades = PreTradeEntry.objects.filter(user=request.user, date__year=year, date__month=month)
    backtests = BacktestEntry.objects.filter(user=request.user, date__year=year, date__month=month)
    
    context = {
        'year': int(year),
        'month': int(month),
        'after_trades': after_trades,
        'pre_trades': pre_trades,
        'backtests': backtests,
    }
    return render(request, 'journal/calendar.html', context)


@login_required
def daily_summary(request, year, month, day):
    """Daily summary of all trades"""
    date = datetime(year, month, day).date()
    
    after_trades = AfterTradeEntry.objects.filter(user=request.user, date=date)
    pre_trades = PreTradeEntry.objects.filter(user=request.user, date=date)
    backtests = BacktestEntry.objects.filter(user=request.user, date=date)
    
    context = {
        'date': date,
        'after_trades': after_trades,
        'pre_trades': pre_trades,
        'backtests': backtests,
    }
    return render(request, 'journal/daily_summary.html', context)


# Enhanced Features
@login_required
def lot_size_calculator(request):
    """Lot size calculator tool"""
    from .forms import LotSizeCalculatorForm
    from .instrument_data import INSTRUMENTS, get_instrument_data
    import json
    
    if request.method == 'POST':
        form = LotSizeCalculatorForm(request.POST)
        if form.is_valid():
            result = form.calculate_lot_size()
            instrument_code = form.cleaned_data.get('instrument', 'EURUSD')
            instrument_data = get_instrument_data(instrument_code)
            
            # Save calculation history
            if result:
                LotSizeCalculation.objects.create(
                    user=request.user,
                    instrument=instrument_data['name'] if instrument_data else instrument_code,
                    account_balance=form.cleaned_data['account_balance'],
                    account_currency=form.cleaned_data.get('account_currency', 'USD'),
                    risk_percentage=form.cleaned_data['risk_percentage'],
                    stop_loss_pips=form.cleaned_data['stop_loss_pips'],
                    calculated_lot_size=result
                )
            
            return render(request, 'journal/lot_size_calculator.html', {
                'form': form, 
                'result': result,
                'instrument_data': instrument_data,
                'instruments_json': json.dumps(INSTRUMENTS)
            })
    else:
        form = LotSizeCalculatorForm()
    
    # Get recent calculations for this user
    recent_calculations = LotSizeCalculation.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    return render(request, 'journal/lot_size_calculator.html', {
        'form': form,
        'instruments_json': json.dumps(INSTRUMENTS),
        'recent_calculations': recent_calculations
    })


@login_required
def trade_comparison(request):
    """Compare two trades"""
    trade1_id = request.GET.get('trade1')
    trade2_id = request.GET.get('trade2')
    
    trade1 = None
    trade2 = None
    
    if trade1_id:
        try:
            trade1 = AfterTradeEntry.objects.get(pk=trade1_id, user=request.user)
        except AfterTradeEntry.DoesNotExist:
            pass
    
    if trade2_id:
        try:
            trade2 = AfterTradeEntry.objects.get(pk=trade2_id, user=request.user)
        except AfterTradeEntry.DoesNotExist:
            pass
    
    # Get list of all trades for selection
    all_trades = AfterTradeEntry.objects.filter(user=request.user).order_by('-date')[:50]
    
    context = {
        'trade1': trade1,
        'trade2': trade2,
        'all_trades': all_trades,
    }
    return render(request, 'journal/trade_comparison.html', context)


@login_required
def save_filter_preset(request):
    """Save filter preset"""
    if request.method == 'POST':
        name = request.POST.get('name')
        filters = dict(request.POST.items())
        filters.pop('name', None)
        filters.pop('csrfmiddlewaretoken', None)
        
        preset = FilterPreset.objects.create(
            user=request.user,
            name=name,
            filters=filters
        )
        return JsonResponse({'success': True, 'preset_id': preset.id})
    return JsonResponse({'success': False})


@login_required
def load_filter_preset(request, preset_id):
    """Load filter preset"""
    preset = get_object_or_404(FilterPreset, pk=preset_id, user=request.user)
    query_string = urlencode(preset.filters, doseq=True)
    return redirect(f"/journal/after/?{query_string}")


# Error Insights
@login_required
def error_insights(request):
    """Error pattern insights page"""
    from .services import ErrorPatternAnalyzer
    
    time_filter = request.GET.get('time_filter', None)
    patterns = ErrorPatternAnalyzer.analyze_error_patterns(request.user, time_filter)
    
    context = {
        'patterns': patterns,
        'time_filter': time_filter,
    }
    return render(request, 'journal/error_insights.html', context)


@login_required
def regenerate_insights(request):
    """Regenerate error insights"""
    # This will trigger recalculation on next view
    messages.success(request, 'Error insights will be regenerated on next view.')
    return redirect('error_insights')


@login_required
def view_related_trades(request):
    """Filter trades based on error pattern"""
    filter_params = {}
    for key in ['market_condition', 'outcome', 'bias', 'entry_quality', 
                'poi_performance', 'session', 'market_behaviour', 
                'predicted_directional_bias']:
        value = request.GET.get(key)
        if value:
            filter_params[key] = value
    
    discipline_scores = request.GET.getlist('discipline_score')
    if discipline_scores:
        filter_params['discipline_score__in'] = discipline_scores
    
    query_string = urlencode(filter_params, doseq=True)
    return redirect(f"/journal/after/?{query_string}")


# Profile
@login_required
def profile(request):
    """User profile page"""
    after_count = AfterTradeEntry.objects.filter(user=request.user).count()
    pre_count = PreTradeEntry.objects.filter(user=request.user).count()
    backtest_count = BacktestEntry.objects.filter(user=request.user).count()
    total_entries = after_count + pre_count + backtest_count
    
    context = {
        'user': request.user,
        'after_count': after_count,
        'pre_count': pre_count,
        'backtest_count': backtest_count,
        'total_entries': total_entries,
    }
    return render(request, 'journal/profile.html', context)


# NEW FEATURES - Added Below

@login_required
def global_search(request):
    """Global search across all journal types"""
    query = request.GET.get('q', '').strip()
    results = {
        'after_trades': [],
        'pre_trades': [],
        'backtests': [],
        'query': query
    }
    
    if query:
        # Search after trades
        after_q = Q(
            Q(pair__icontains=query) |
            Q(observations__icontains=query) |
            Q(major_impact_news__icontains=query) |
            Q(ai_summary__icontains=query)
        )
        results['after_trades'] = AfterTradeEntry.objects.filter(
            user=request.user
        ).filter(after_q).order_by('-date', '-time_of_entry')[:20]
        
        # Search pre trades
        pre_q = Q(
            Q(pair__icontains=query) |
            Q(notes__icontains=query) |
            Q(reason_for_taking_or_not__icontains=query) |
            Q(htf_draws__icontains=query) |
            Q(lower_tf_confirmation__icontains=query)
        )
        results['pre_trades'] = PreTradeEntry.objects.filter(
            user=request.user
        ).filter(pre_q).order_by('-date')[:20]
        
        # Search backtests
        backtest_q = Q(
            Q(pair__icontains=query) |
            Q(notes__icontains=query) |
            Q(entry_trigger__icontains=query) |
            Q(behaviour_based_on_previous_moves__icontains=query) |
            Q(lower_tf_bos__icontains=query) |
            Q(high_impact_news__icontains=query)
        )
        results['backtests'] = BacktestEntry.objects.filter(
            user=request.user
        ).filter(backtest_q).order_by('-date')[:20]
    
    return render(request, 'journal/global_search.html', results)


@login_required
def trade_statistics(request):
    """Comprehensive trade statistics page"""
    after_trades = AfterTradeEntry.objects.filter(user=request.user)
    
    # Overall stats
    total_trades = after_trades.count()
    wins = after_trades.filter(outcome='win').count()
    losses = after_trades.filter(outcome='loss').count()
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    # Advanced metrics
    winning_trades = after_trades.filter(outcome='win')
    losing_trades = after_trades.filter(outcome='loss')
    
    # Average win/loss (using pips as proxy)
    avg_win_pips = winning_trades.aggregate(Avg('reward_pips'))['reward_pips__avg'] or 0
    avg_loss_pips = losing_trades.aggregate(Avg('risk_pips'))['risk_pips__avg'] or 0
    profit_factor = (avg_win_pips * wins) / (avg_loss_pips * losses) if losses > 0 and avg_loss_pips else 0
    
    # Best and worst trades (by RR ratio)
    best_trade = after_trades.filter(rr_ratio__isnull=False).order_by('-rr_ratio').first()
    worst_trade = after_trades.filter(rr_ratio__isnull=False).order_by('rr_ratio').first()
    
    # Max consecutive wins/losses
    trades_ordered = after_trades.order_by('date', 'time_of_entry')
    max_win_streak = 0
    max_loss_streak = 0
    current_win_streak = 0
    current_loss_streak = 0
    
    for trade in trades_ordered:
        if trade.outcome == 'win':
            current_win_streak += 1
            current_loss_streak = 0
            max_win_streak = max(max_win_streak, current_win_streak)
        else:
            current_loss_streak += 1
            current_win_streak = 0
            max_loss_streak = max(max_loss_streak, current_loss_streak)
    
    # Monthly stats
    monthly_stats = {}
    for trade in after_trades:
        month_key = f"{trade.date.year}-{trade.date.month:02d}"
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {'wins': 0, 'losses': 0, 'total': 0}
        monthly_stats[month_key]['total'] += 1
        if trade.outcome == 'win':
            monthly_stats[month_key]['wins'] += 1
        else:
            monthly_stats[month_key]['losses'] += 1
    
    # Calculate win rates for monthly stats
    for key in monthly_stats:
        stats = monthly_stats[key]
        stats['win_rate'] = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    # Per pair stats
    pair_stats = {}
    for trade in after_trades:
        if trade.pair not in pair_stats:
            pair_stats[trade.pair] = {'wins': 0, 'losses': 0, 'total': 0}
        pair_stats[trade.pair]['total'] += 1
        if trade.outcome == 'win':
            pair_stats[trade.pair]['wins'] += 1
        else:
            pair_stats[trade.pair]['losses'] += 1
    
    # Per session stats
    session_stats = {}
    for trade in after_trades:
        if trade.session not in session_stats:
            session_stats[trade.session] = {'wins': 0, 'losses': 0, 'total': 0}
        session_stats[trade.session]['total'] += 1
        if trade.outcome == 'win':
            session_stats[trade.session]['wins'] += 1
        else:
            session_stats[trade.session]['losses'] += 1
    
    # Calculate win rates for pair and session
    for key in pair_stats:
        stats = pair_stats[key]
        stats['win_rate'] = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    for key in session_stats:
        stats = session_stats[key]
        stats['win_rate'] = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    context = {
        'total_trades': total_trades,
        'wins': wins,
        'losses': losses,
        'win_rate': round(win_rate, 1),
        'avg_win_pips': round(float(avg_win_pips), 2) if avg_win_pips else 0,
        'avg_loss_pips': round(float(avg_loss_pips), 2) if avg_loss_pips else 0,
        'profit_factor': round(float(profit_factor), 2) if profit_factor else 0,
        'best_trade': best_trade,
        'worst_trade': worst_trade,
        'max_win_streak': max_win_streak,
        'max_loss_streak': max_loss_streak,
        'monthly_stats': monthly_stats,
        'pair_stats': pair_stats,
        'session_stats': session_stats,
    }
    
    return render(request, 'journal/trade_statistics.html', context)


@login_required
def duplicate_trade(request, pk):
    """Duplicate an after trade entry"""
    original = get_object_or_404(AfterTradeEntry, pk=pk, user=request.user)
    
    # Create a copy
    duplicate = AfterTradeEntry(
        user=request.user,
        pair=original.pair,
        date=original.date,
        session=original.session,
        bias=original.bias,
        htf_mitigation=original.htf_mitigation,
        liquidity_analysis=original.liquidity_analysis,
        market_condition=original.market_condition,
        lower_tf_confirmation=original.lower_tf_confirmation,
        risk_management_applied=original.risk_management_applied,
        high_impact_news=original.high_impact_news,
        major_impact_news=original.major_impact_news,
        predicted_directional_bias=original.predicted_directional_bias,
        poi_performance=original.poi_performance,
        risk_percentage=original.risk_percentage,
        market_behaviour=original.market_behaviour,
        entry_quality=original.entry_quality,
        poi_quality_score=original.poi_quality_score,
        time_of_entry=original.time_of_entry,
        outcome=original.outcome,
        discipline_score=original.discipline_score,
        observations=original.observations,
        risk_pips=original.risk_pips,
        reward_pips=original.reward_pips,
    )
    duplicate.save()
    
    # Copy many-to-many relationships
    duplicate.strategy_tags.set(original.strategy_tags.all())
    
    messages.success(request, f'Trade entry duplicated successfully!')
    return redirect('after_trade_edit', pk=duplicate.pk)


@login_required
def trade_templates(request):
    """Manage trade templates"""
    from .models import TradeTemplate
    
    if request.method == 'POST':
        template_id = request.POST.get('template_id')
        action = request.POST.get('action')
        
        if action == 'delete':
            template = get_object_or_404(TradeTemplate, pk=template_id, user=request.user)
            template.delete()
            messages.success(request, 'Template deleted successfully!')
            return redirect('trade_templates')
        
        elif action == 'create':
            name = request.POST.get('name')
            if name:
                template = TradeTemplate(
                    user=request.user,
                    name=name,
                    pair=request.POST.get('pair', ''),
                    session=request.POST.get('session', ''),
                    bias=request.POST.get('bias', ''),
                    market_condition=request.POST.get('market_condition', ''),
                    liquidity_analysis=request.POST.get('liquidity_analysis', ''),
                    risk_percentage=request.POST.get('risk_percentage') or 0,
                )
                template.save()
                messages.success(request, 'Template created successfully!')
                return redirect('trade_templates')
    
    templates = TradeTemplate.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'journal/trade_templates.html', {'templates': templates})


@login_required
def use_template(request, template_id):
    """Create a new trade entry from a template"""
    from .models import TradeTemplate
    from .forms import AfterTradeEntryForm
    
    template = get_object_or_404(TradeTemplate, pk=template_id, user=request.user)
    
    # Pre-populate form with template data
    initial_data = {
        'pair': template.pair,
        'session': template.session,
        'bias': template.bias,
        'market_condition': template.market_condition,
        'liquidity_analysis': template.liquidity_analysis,
        'risk_percentage': template.risk_percentage,
    }
    
    form = AfterTradeEntryForm(initial=initial_data)
    return render(request, 'journal/after_trade_form.html', {
        'form': form,
        'template': template,
    })


@login_required
def settings_page(request):
    """User settings and preferences"""
    if request.method == 'POST':
        # Update user preferences
        user = request.user
        if 'email' in request.POST:
            user.email = request.POST.get('email')
        if 'first_name' in request.POST:
            user.first_name = request.POST.get('first_name')
        if 'last_name' in request.POST:
            user.last_name = request.POST.get('last_name')
        user.save()
        messages.success(request, 'Settings updated successfully!')
        return redirect('settings')
    
    return render(request, 'journal/settings.html')


# Property Management Views for Dynamic Fields
@login_required
def manage_properties(request, journal_type):
    """Manage custom fields/properties for a journal type"""
    if journal_type not in ['after_trade', 'pre_trade', 'backtest']:
        messages.error(request, 'Invalid journal type')
        return redirect('dashboard')
    
    fields = JournalField.objects.filter(
        user=request.user,
        journal_type=journal_type
    ).order_by('order', 'display_name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            # Create new field
            name = request.POST.get('name', '').strip().lower().replace(' ', '_')
            display_name = request.POST.get('display_name', '').strip()
            field_type = request.POST.get('field_type', 'text')
            is_required = request.POST.get('is_required') == 'on'
            help_text = request.POST.get('help_text', '').strip()
            default_value = request.POST.get('default_value', '').strip()
            
            if name and display_name:
                # Get max order
                max_order = fields.aggregate(Max('order'))['order__max'] or 0
                
                field = JournalField.objects.create(
                    user=request.user,
                    journal_type=journal_type,
                    name=name,
                    display_name=display_name,
                    field_type=field_type,
                    is_required=is_required,
                    help_text=help_text,
                    default_value=default_value,
                    order=max_order + 1
                )
                
                # If select/multiselect, add options
                if field_type in ['select', 'multiselect']:
                    options_text = request.POST.get('options', '').strip()
                    if options_text:
                        options_list = [opt.strip() for opt in options_text.split('\n') if opt.strip()]
                        for idx, option in enumerate(options_list):
                            JournalFieldOption.objects.create(
                                field=field,
                                value=option.lower().replace(' ', '_'),
                                display_label=option,
                                order=idx
                            )
                
                messages.success(request, f'Field "{display_name}" created successfully!')
                return redirect('manage_properties', journal_type=journal_type)
        
        elif action == 'update':
            # Update field
            field_id = request.POST.get('field_id')
            try:
                field = JournalField.objects.get(pk=field_id, user=request.user)
                field.display_name = request.POST.get('display_name', '').strip()
                field.is_required = request.POST.get('is_required') == 'on'
                field.help_text = request.POST.get('help_text', '').strip()
                field.default_value = request.POST.get('default_value', '').strip()
                field.save()
                messages.success(request, 'Field updated successfully!')
            except JournalField.DoesNotExist:
                messages.error(request, 'Field not found')
        
        elif action == 'delete':
            # Delete field
            field_id = request.POST.get('field_id')
            try:
                field = JournalField.objects.get(pk=field_id, user=request.user)
                field_name = field.display_name
                field.delete()
                messages.success(request, f'Field "{field_name}" deleted successfully!')
            except JournalField.DoesNotExist:
                messages.error(request, 'Field not found')
        
        elif action == 'reorder':
            # Reorder fields
            field_orders = request.POST.getlist('field_order[]')
            for idx, field_id in enumerate(field_orders):
                try:
                    field = JournalField.objects.get(pk=field_id, user=request.user)
                    field.order = idx
                    field.save()
                except JournalField.DoesNotExist:
                    pass
            messages.success(request, 'Field order updated!')
            return JsonResponse({'success': True})
        
        return redirect('manage_properties', journal_type=journal_type)
    
    journal_type_display = dict(JournalField.JOURNAL_TYPE_CHOICES).get(journal_type, journal_type)
    context = {
        'fields': fields,
        'journal_type': journal_type,
        'journal_type_display': journal_type_display,
        'field_types': JournalField.FIELD_TYPE_CHOICES,
    }
    return render(request, 'journal/manage_properties.html', context)


@login_required
def manage_field_options(request, field_id):
    """Manage options for a select/multi-select field"""
    try:
        field = JournalField.objects.get(pk=field_id, user=request.user)
    except JournalField.DoesNotExist:
        messages.error(request, 'Field not found')
        return redirect('dashboard')
    
    if field.field_type not in ['select', 'multiselect']:
        messages.error(request, 'This field type does not support options')
        return redirect('manage_properties', journal_type=field.journal_type)
    
    options = field.options.all().order_by('order', 'display_label')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            value = request.POST.get('value', '').strip().lower().replace(' ', '_')
            display_label = request.POST.get('display_label', '').strip()
            color = request.POST.get('color', '#6c757d')
            
            if value and display_label:
                max_order = options.aggregate(Max('order'))['order__max'] or 0
                JournalFieldOption.objects.create(
                    field=field,
                    value=value,
                    display_label=display_label,
                    color=color,
                    order=max_order + 1
                )
                messages.success(request, 'Option added successfully!')
        
        elif action == 'delete':
            option_id = request.POST.get('option_id')
            try:
                option = JournalFieldOption.objects.get(pk=option_id, field=field)
                option.delete()
                messages.success(request, 'Option deleted successfully!')
            except JournalFieldOption.DoesNotExist:
                messages.error(request, 'Option not found')
        
        elif action == 'reorder':
            option_orders = request.POST.getlist('option_order[]')
            for idx, option_id in enumerate(option_orders):
                try:
                    option = JournalFieldOption.objects.get(pk=option_id, field=field)
                    option.order = idx
                    option.save()
                except JournalFieldOption.DoesNotExist:
                    pass
            return JsonResponse({'success': True})
        
        return redirect('manage_field_options', field_id=field_id)
    
    context = {
        'field': field,
        'options': options,
    }
    return render(request, 'journal/manage_field_options.html', context)
