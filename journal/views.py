from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg, Sum, Case, When, IntegerField
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings
from datetime import datetime, timedelta
from urllib.parse import urlencode
import csv
from .models import AfterTradeEntry, PreTradeEntry, BacktestEntry, StrategyTag, FilterPreset, LotSizeCalculation


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
    """List after trade entries"""
    entries = AfterTradeEntry.objects.filter(user=request.user)
    
    # Basic filtering
    pair = request.GET.get('pair', '')
    session = request.GET.get('session', '')
    bias = request.GET.get('bias', '')
    outcome = request.GET.get('outcome', '')
    search = request.GET.get('search', '')
    
    if pair:
        entries = entries.filter(pair__icontains=pair)
    if session:
        entries = entries.filter(session=session)
    if bias:
        entries = entries.filter(bias=bias)
    if outcome:
        entries = entries.filter(outcome=outcome)
    if search:
        entries = entries.filter(Q(observations__icontains=search) | Q(pair__icontains=search) | Q(major_impact_news__icontains=search))
    
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filters': {'pair': pair, 'session': session, 'bias': bias, 'outcome': outcome, 'search': search}
    }
    return render(request, 'journal/after_trade_list.html', context)


@login_required
def after_trade_create(request):
    """Create after trade entry"""
    from .forms import AfterTradeEntryForm
    
    if request.method == 'POST':
        form = AfterTradeEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            form.save_m2m()  # Save many-to-many relationships
            # Auto-generate AI summary
            try:
                from .services import TradeSummaryGenerator
                TradeSummaryGenerator.generate_and_save_summary(entry)
                messages.success(request, 'After Trade entry created successfully! AI summary generated.')
            except Exception as e:
                messages.success(request, 'After Trade entry created successfully!')
            return redirect('after_trade_detail', pk=entry.pk)
    else:
        form = AfterTradeEntryForm()
    return render(request, 'journal/after_trade_form.html', {'form': form})


@login_required
def after_trade_detail(request, pk):
    """View after trade entry detail"""
    entry = get_object_or_404(AfterTradeEntry, pk=pk, user=request.user)
    return render(request, 'journal/after_trade_detail.html', {'entry': entry})


@login_required
def after_trade_edit(request, pk):
    """Edit after trade entry"""
    from .forms import AfterTradeEntryForm
    entry = get_object_or_404(AfterTradeEntry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AfterTradeEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            entry = form.save()
            form.save_m2m()
            messages.success(request, 'Entry updated successfully!')
            return redirect('after_trade_detail', pk=entry.pk)
    else:
        form = AfterTradeEntryForm(instance=entry)
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
    """List pre trade entries"""
    entries = PreTradeEntry.objects.filter(user=request.user)
    
    pair = request.GET.get('pair', '')
    bias = request.GET.get('bias', '')
    trade_taken = request.GET.get('trade_taken', '')
    date_from = request.GET.get('date_from', '')
    search = request.GET.get('search', '')
    
    if pair:
        entries = entries.filter(pair__icontains=pair)
    if bias:
        entries = entries.filter(bias=bias)
    if trade_taken:
        entries = entries.filter(trade_taken=(trade_taken == 'true'))
    if date_from:
        entries = entries.filter(date__gte=date_from)
    if search:
        entries = entries.filter(Q(notes__icontains=search) | Q(pair__icontains=search) | Q(reason_for_taking_or_not__icontains=search))
    
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filters': {'pair': pair, 'bias': bias, 'trade_taken': trade_taken, 'date_from': date_from, 'search': search}
    }
    return render(request, 'journal/pre_trade_list.html', context)


@login_required
def pre_trade_create(request):
    """Create pre trade entry"""
    from .forms import PreTradeEntryForm
    
    if request.method == 'POST':
        form = PreTradeEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, 'Pre Trade entry created successfully!')
            return redirect('pre_trade_detail', pk=entry.pk)
    else:
        form = PreTradeEntryForm()
    return render(request, 'journal/pre_trade_form.html', {'form': form})


@login_required
def pre_trade_detail(request, pk):
    """View pre trade entry detail"""
    entry = get_object_or_404(PreTradeEntry, pk=pk, user=request.user)
    return render(request, 'journal/pre_trade_detail.html', {'entry': entry})


@login_required
def pre_trade_edit(request, pk):
    """Edit pre trade entry"""
    from .forms import PreTradeEntryForm
    entry = get_object_or_404(PreTradeEntry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PreTradeEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            entry = form.save()
            messages.success(request, 'Entry updated successfully!')
            return redirect('pre_trade_detail', pk=entry.pk)
    else:
        form = PreTradeEntryForm(instance=entry)
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
    """List backtest entries"""
    entries = BacktestEntry.objects.filter(user=request.user)
    
    pair = request.GET.get('pair', '')
    outcome = request.GET.get('outcome', '')
    date_from = request.GET.get('date_from', '')
    search = request.GET.get('search', '')
    
    if pair:
        entries = entries.filter(pair__icontains=pair)
    if outcome:
        entries = entries.filter(outcome=outcome)
    if date_from:
        entries = entries.filter(date__gte=date_from)
    if search:
        entries = entries.filter(Q(notes__icontains=search) | Q(pair__icontains=search) | Q(strategy_name__icontains=search))
    
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filters': {'pair': pair, 'outcome': outcome, 'date_from': date_from, 'search': search}
    }
    return render(request, 'journal/backtest_list.html', context)


@login_required
def backtest_create(request):
    """Create backtest entry"""
    from .forms import BacktestEntryForm
    
    if request.method == 'POST':
        form = BacktestEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, 'Backtest entry created successfully!')
            return redirect('backtest_detail', pk=entry.pk)
    else:
        form = BacktestEntryForm()
    return render(request, 'journal/backtest_form.html', {'form': form})


@login_required
def backtest_detail(request, pk):
    """View backtest entry detail"""
    entry = get_object_or_404(BacktestEntry, pk=pk, user=request.user)
    return render(request, 'journal/backtest_detail.html', {'entry': entry})


@login_required
def backtest_edit(request, pk):
    """Edit backtest entry"""
    from .forms import BacktestEntryForm
    entry = get_object_or_404(BacktestEntry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BacktestEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            entry = form.save()
            messages.success(request, 'Entry updated successfully!')
            return redirect('backtest_detail', pk=entry.pk)
    else:
        form = BacktestEntryForm(instance=entry)
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
    
    if request.method == 'POST':
        form = LotSizeCalculatorForm(request.POST)
        if form.is_valid():
            result = form.calculate_lot_size()
            return render(request, 'journal/lot_size_calculator.html', {'form': form, 'result': result})
    else:
        form = LotSizeCalculatorForm()
    
    return render(request, 'journal/lot_size_calculator.html', {'form': form})


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
