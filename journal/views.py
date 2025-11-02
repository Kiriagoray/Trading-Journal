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
from .services import ErrorPatternAnalyzer


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
    
    if pair:
        entries = entries.filter(pair__icontains=pair)
    if session:
        entries = entries.filter(session=session)
    if bias:
        entries = entries.filter(bias=bias)
    if outcome:
        entries = entries.filter(outcome=outcome)
    
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filters': {'pair': pair, 'session': session, 'bias': bias, 'outcome': outcome}
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
    return render(request, 'journal/after_trade_form.html', {'form': form, 'action': 'Create'})


@login_required
def after_trade_detail(request, pk):
    """Detail view for after trade entry"""
    entry = get_object_or_404(AfterTradeEntry, pk=pk, user=request.user)
    related = AfterTradeEntry.objects.filter(user=request.user, pair=entry.pair).exclude(pk=pk)[:5]
    
    context = {'entry': entry, 'related': related}
    return render(request, 'journal/after_trade_detail.html', context)


@login_required
def after_trade_edit(request, pk):
    """Edit after trade entry"""
    from .forms import AfterTradeEntryForm
    entry = get_object_or_404(AfterTradeEntry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AfterTradeEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            entry = form.save()
            # Auto-regenerate summary
            try:
                from .services import TradeSummaryGenerator
                TradeSummaryGenerator.generate_and_save_summary(entry, regenerate=True)
                messages.success(request, 'Entry updated successfully! AI summary regenerated.')
            except Exception as e:
                messages.success(request, 'Entry updated successfully!')
            return redirect('after_trade_detail', pk=pk)
    else:
        form = AfterTradeEntryForm(instance=entry)
    return render(request, 'journal/after_trade_form.html', {'form': form, 'entry': entry, 'action': 'Edit'})


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
def after_trade_export_csv(request):
    """Export after trade entries to CSV"""
    entries = AfterTradeEntry.objects.filter(user=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="after_trade_entries.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Pair', 'Date', 'Outcome', 'POI Score', 'Discipline Score'])
    
    for entry in entries:
        writer.writerow([entry.pair, entry.date, entry.outcome, entry.poi_quality_score, entry.discipline_score])
    
    return response


@login_required
def regenerate_summary(request, pk):
    """Regenerate AI summary"""
    entry = get_object_or_404(AfterTradeEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        try:
            from .services import TradeSummaryGenerator
            TradeSummaryGenerator.generate_and_save_summary(entry, regenerate=True)
            messages.success(request, 'AI summary regenerated!')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return redirect('after_trade_detail', pk=pk)


# Pre Trade Views
@login_required
def pre_trade_list(request):
    """List pre trade entries"""
    entries = PreTradeEntry.objects.filter(user=request.user)
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'journal/pre_trade_list.html', {'page_obj': page_obj})


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
            messages.success(request, 'Pre Trade entry created!')
            return redirect('pre_trade_detail', pk=entry.pk)
    else:
        form = PreTradeEntryForm()
    return render(request, 'journal/pre_trade_form.html', {'form': form, 'action': 'Create'})


@login_required
def pre_trade_detail(request, pk):
    """Detail view for pre trade entry"""
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
            form.save()
            messages.success(request, 'Entry updated!')
            return redirect('pre_trade_detail', pk=pk)
    else:
        form = PreTradeEntryForm(instance=entry)
    return render(request, 'journal/pre_trade_form.html', {'form': form, 'entry': entry, 'action': 'Edit'})


@login_required
def pre_trade_delete(request, pk):
    """Delete pre trade entry"""
    entry = get_object_or_404(PreTradeEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Entry deleted!')
        return redirect('pre_trade_list')
    return render(request, 'journal/pre_trade_delete.html', {'entry': entry})


@login_required
def pre_trade_export_csv(request):
    """Export pre trade entries to CSV"""
    entries = PreTradeEntry.objects.filter(user=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pre_trade_entries.csv"'
    writer = csv.writer(response)
    writer.writerow(['Pair', 'Date', 'Bias', 'Trade Taken'])
    for entry in entries:
        writer.writerow([entry.pair, entry.date, entry.bias, entry.trade_taken])
    return response


# Backtest Views
@login_required
def backtest_list(request):
    """List backtest entries"""
    entries = BacktestEntry.objects.filter(user=request.user)
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'journal/backtest_list.html', {'page_obj': page_obj})


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
            messages.success(request, 'Backtest entry created!')
            return redirect('backtest_detail', pk=entry.pk)
    else:
        form = BacktestEntryForm()
    return render(request, 'journal/backtest_form.html', {'form': form, 'action': 'Create'})


@login_required
def backtest_detail(request, pk):
    """Detail view for backtest entry"""
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
            form.save()
            messages.success(request, 'Entry updated!')
            return redirect('backtest_detail', pk=pk)
    else:
        form = BacktestEntryForm(instance=entry)
    return render(request, 'journal/backtest_form.html', {'form': form, 'entry': entry, 'action': 'Edit'})


@login_required
def backtest_delete(request, pk):
    """Delete backtest entry"""
    entry = get_object_or_404(BacktestEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Entry deleted!')
        return redirect('backtest_list')
    return render(request, 'journal/backtest_delete.html', {'entry': entry})


@login_required
def backtest_export_csv(request):
    """Export backtest entries to CSV"""
    entries = BacktestEntry.objects.filter(user=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="backtest_entries.csv"'
    writer = csv.writer(response)
    writer.writerow(['Pair', 'Date', 'Outcome'])
    for entry in entries:
        writer.writerow([entry.pair, entry.date, entry.outcome])
    return response


# Calendar & Daily Summary
@login_required
def journal_calendar(request):
    """Calendar view"""
    after_trades = AfterTradeEntry.objects.filter(user=request.user)
    context = {'after_trades': after_trades}
    return render(request, 'journal/calendar.html', context)


@login_required
def daily_summary(request, year, month, day):
    """Daily summary view"""
    date = datetime(year, month, day).date()
    after_trades = AfterTradeEntry.objects.filter(user=request.user, date=date)
    pre_trades = PreTradeEntry.objects.filter(user=request.user, date=date)
    backtests = BacktestEntry.objects.filter(user=request.user, date=date)
    
    context = {
        'date': date,
        'after_trades': after_trades,
        'pre_trades': pre_trades,
        'backtests': backtests,
        'total_trades': after_trades.count(),
        'wins': after_trades.filter(outcome='win').count(),
        'losses': after_trades.filter(outcome='loss').count(),
    }
    return render(request, 'journal/daily_summary.html', context)


# Enhanced Features
@login_required
def lot_size_calculator(request):
    """Lot size calculator"""
    from .forms import LotSizeCalculatorForm
    
    calculated_lot = None
    if request.method == 'POST':
        form = LotSizeCalculatorForm(request.POST)
        if form.is_valid():
            calculated_lot = form.calculate_lot_size()
            if calculated_lot:
                # Save to history
                LotSizeCalculation.objects.create(
                    user=request.user,
                    account_balance=form.cleaned_data['account_balance'],
                    risk_percentage=form.cleaned_data['risk_percentage'],
                    stop_loss_pips=form.cleaned_data['stop_loss_pips'],
                    instrument=form.cleaned_data['instrument'],
                    calculated_lot_size=calculated_lot
                )
    else:
        form = LotSizeCalculatorForm()
    
    # Get history
    history = LotSizeCalculation.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'form': form,
        'calculated_lot': calculated_lot,
        'history': history
    }
    return render(request, 'journal/lot_size_calculator.html', context)


@login_required
def trade_comparison(request):
    """Trade comparison tool"""
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
    
    # Get all user's trades for selection
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
        if name:
            FilterPreset.objects.create(user=request.user, name=name, filters={})
            messages.success(request, 'Filter preset saved!')
    return redirect('after_trade_list')


@login_required
def load_filter_preset(request, preset_id):
    """Load filter preset"""
    preset = get_object_or_404(FilterPreset, pk=preset_id, user=request.user)
    # Redirect with filter parameters
    return redirect('after_trade_list')


@login_required
def profile(request):
    """User profile page"""
    return render(request, 'journal/profile.html', {'user': request.user})


# Error Insights Views (already defined, keeping them)
@login_required
def error_insights(request):
    """Error Pattern Detection & Suggestions view"""
    time_filter = request.GET.get('filter', None)
    
    try:
        insights_data = ErrorPatternAnalyzer.analyze_error_patterns(
            request.user, 
            time_filter=time_filter
        )
    except Exception as e:
        messages.error(request, f'Error generating insights: {str(e)}')
        insights_data = {
            'patterns': [],
            'chart_data': {'labels': [], 'counts': []},
            'total_analyzed': 0,
            'generated_at': None
        }
    
    context = {
        'insights': insights_data['patterns'],
        'chart_data': insights_data['chart_data'],
        'total_analyzed': insights_data['total_analyzed'],
        'generated_at': insights_data['generated_at'],
        'time_filter': time_filter
    }
    
    return render(request, 'journal/error_insights.html', context)


@login_required
def regenerate_insights(request):
    """Regenerate error insights"""
    time_filter = request.GET.get('filter', None)
    
    try:
        insights_data = ErrorPatternAnalyzer.analyze_error_patterns(
            request.user,
            time_filter=time_filter
        )
        messages.success(request, 'Error insights regenerated successfully!')
    except Exception as e:
        messages.error(request, f'Error regenerating insights: {str(e)}')
    
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
