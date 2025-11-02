"""
AI-powered trade summary generator service and Error Pattern Detection
"""
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q, Count, Avg, Sum, Case, When, IntegerField
from collections import Counter
from datetime import datetime, timedelta


class TradeSummaryGenerator:
    """
    Generates intelligent, concise summaries of trades using key metrics and insights.
    Can be extended to use actual AI APIs (OpenAI, Anthropic, etc.) in the future.
    """
    
    @staticmethod
    def generate_summary(entry):
        """Generate an AI-powered summary for a trade entry."""
        if not entry:
            return ""
        
        summary_parts = []
        outcome_emoji = "✅" if entry.outcome == 'win' else "❌"
        summary_parts.append(
            f"{outcome_emoji} **{entry.outcome.upper()}** | {entry.pair} | {entry.date.strftime('%B %d, %Y')} | {entry.session} Session"
        )
        
        # Add key metrics, setup analysis, execution, etc.
        if hasattr(entry, 'poi_quality_score') and entry.poi_quality_score:
            poi_stars = "⭐" * entry.poi_quality_score
            summary_parts.append(f"\n**POI Quality:** {poi_stars} ({entry.poi_quality_score}/5)")
        
        if hasattr(entry, 'rr_ratio') and entry.rr_ratio:
            summary_parts.append(f"\n**Risk:Reward:** {entry.rr_ratio:.2f}:1")
        
        return "\n".join(summary_parts)
    
    @staticmethod
    def generate_and_save_summary(entry, regenerate=False):
        """Generate summary and save it to the entry."""
        if not regenerate and hasattr(entry, 'ai_summary') and entry.ai_summary:
            return entry.ai_summary
        
        summary = TradeSummaryGenerator.generate_summary(entry)
        if hasattr(entry, 'ai_summary'):
            entry.ai_summary = summary
            entry.summary_generated_at = timezone.now()
            entry.save(update_fields=['ai_summary', 'summary_generated_at'])
        
        return summary


class ErrorPatternAnalyzer:
    """
    Analyzes trading journal entries to detect recurring error patterns,
    weaknesses, and behavioral issues. Provides actionable suggestions.
    """
    
    @staticmethod
    def analyze_error_patterns(user, time_filter=None):
        """
        Analyze all journal entries for a user and detect error patterns.
        
        Args:
            user: User instance
            time_filter: Optional filter (e.g., 'last_30' for last 30 trades)
            
        Returns:
            dict: Dictionary containing detected patterns with suggestions
        """
        from .models import AfterTradeEntry, PreTradeEntry, BacktestEntry
        
        # Get all entries
        after_trades = AfterTradeEntry.objects.filter(user=user)
        pre_trades = PreTradeEntry.objects.filter(user=user)
        backtests = BacktestEntry.objects.filter(user=user)
        
        # Apply time filter if specified
        if time_filter == 'last_30':
            after_trades = after_trades.order_by('-date')[:30]
            pre_trades = pre_trades.order_by('-date')[:30]
            backtests = backtests.order_by('-date')[:30]
        
        patterns = []
        
        # 1. Market Condition vs Outcome Analysis
        market_pattern = ErrorPatternAnalyzer._analyze_market_condition_errors(after_trades)
        if market_pattern:
            patterns.append(market_pattern)
        
        # 2. Discipline Score Analysis
        discipline_pattern = ErrorPatternAnalyzer._analyze_discipline_issues(after_trades)
        if discipline_pattern:
            patterns.append(discipline_pattern)
        
        # 3. Bias Accuracy Analysis
        bias_pattern = ErrorPatternAnalyzer._analyze_bias_accuracy(after_trades)
        if bias_pattern:
            patterns.append(bias_pattern)
        
        # 4. Entry Quality/Timing Issues
        entry_pattern = ErrorPatternAnalyzer._analyze_entry_timing_issues(after_trades)
        if entry_pattern:
            patterns.append(entry_pattern)
        
        # 5. POI Performance Analysis
        poi_pattern = ErrorPatternAnalyzer._analyze_poi_issues(after_trades)
        if poi_pattern:
            patterns.append(poi_pattern)
        
        # 6. Session-based Performance
        session_pattern = ErrorPatternAnalyzer._analyze_session_performance(after_trades)
        if session_pattern:
            patterns.append(session_pattern)
        
        # 7. Market Behavior Issues
        behavior_pattern = ErrorPatternAnalyzer._analyze_market_behavior_issues(after_trades)
        if behavior_pattern:
            patterns.append(behavior_pattern)
        
        # Sort by severity/impact
        patterns.sort(key=lambda x: x.get('severity_score', 0), reverse=True)
        
        # Get top 5 patterns
        top_patterns = patterns[:5]
        
        # Calculate summary statistics for chart
        chart_data = ErrorPatternAnalyzer._calculate_chart_data(patterns)
        
        return {
            'patterns': top_patterns,
            'chart_data': chart_data,
            'total_analyzed': len(after_trades) + len(pre_trades) + len(backtests),
            'generated_at': timezone.now()
        }
    
    @staticmethod
    def _analyze_market_condition_errors(entries):
        """Analyze which market conditions lead to most losses."""
        if not entries.exists():
            return None
        
        condition_outcomes = {}
        for entry in entries:
            condition = entry.market_condition
            if condition not in condition_outcomes:
                condition_outcomes[condition] = {'wins': 0, 'losses': 0}
            
            if entry.outcome == 'win':
                condition_outcomes[condition]['wins'] += 1
            else:
                condition_outcomes[condition]['losses'] += 1
        
        # Find condition with worst win rate
        worst_condition = None
        worst_win_rate = 100
        
        for condition, outcomes in condition_outcomes.items():
            total = outcomes['wins'] + outcomes['losses']
            if total >= 3:  # Only analyze if at least 3 trades
                win_rate = (outcomes['wins'] / total) * 100
                if win_rate < worst_win_rate:
                    worst_win_rate = win_rate
                    worst_condition = condition
        
        if worst_condition and worst_win_rate < 50:
            total_trades = condition_outcomes[worst_condition]['wins'] + condition_outcomes[worst_condition]['losses']
            loss_pct = (condition_outcomes[worst_condition]['losses'] / total_trades) * 100
            
            return {
                'type': 'market_condition',
                'title': f'Struggling in {worst_condition} Markets',
                'severity_score': int(100 - worst_win_rate),
                'description': f'Your win rate in {worst_condition} market conditions is {worst_win_rate:.1f}%, significantly below average.',
                'statistics': f'{loss_pct:.0f}% of losses occur during {worst_condition} markets ({condition_outcomes[worst_condition]["losses"]} out of {total_trades} trades)',
                'suggestion': ErrorPatternAnalyzer._get_market_condition_suggestion(worst_condition),
                'filter_params': {'market_condition': worst_condition, 'outcome': 'loss'}
            }
        return None
    
    @staticmethod
    def _analyze_discipline_issues(entries):
        """Analyze discipline score patterns."""
        if not entries.exists():
            return None
        
        discipline_scores = {}
        for entry in entries:
            score = entry.discipline_score
            if score not in discipline_scores:
                discipline_scores[score] = {'wins': 0, 'losses': 0}
            
            if entry.outcome == 'win':
                discipline_scores[score]['wins'] += 1
            else:
                discipline_scores[score]['losses'] += 1
        
        # Find poor discipline patterns
        poor_scores = ['poor', 'very poor', 'average']
        poor_trades = {k: v for k, v in discipline_scores.items() if k in poor_scores}
        
        if poor_trades:
            total_poor = sum(v['wins'] + v['losses'] for v in poor_trades.values())
            total_trades = sum(v['wins'] + v['losses'] for v in discipline_scores.values())
            
            if total_poor >= 3 and total_trades > 0:
                poor_pct = (total_poor / total_trades) * 100
                avg_win_rate = sum(v['wins'] / (v['wins'] + v['losses']) * 100 if (v['wins'] + v['losses']) > 0 else 0 
                              for v in poor_trades.values()) / len(poor_trades) if poor_trades else 0
                
                if poor_pct > 30:  # If more than 30% of trades have poor discipline
                    return {
                        'type': 'discipline',
                        'title': 'Discipline Score Issues Detected',
                        'severity_score': int(poor_pct),
                        'description': f'{poor_pct:.0f}% of your trades have average or poor discipline scores.',
                        'statistics': f'Average win rate with poor discipline: {avg_win_rate:.1f}% ({total_poor} trades analyzed)',
                        'suggestion': 'Review your trading rules and stick to your plan. Consider using checklists before each trade. Avoid emotional trading and wait for clear setups.',
                        'filter_params': {'discipline_score__in': poor_scores}
                    }
        return None
    
    @staticmethod
    def _analyze_bias_accuracy(entries):
        """Analyze bias prediction accuracy."""
        if not entries.exists():
            return None
        
        bias_accuracy = {}
        for entry in entries:
            bias = entry.bias
            predicted_correct = entry.predicted_directional_bias == 'correct'
            
            if bias not in bias_accuracy:
                bias_accuracy[bias] = {'correct': 0, 'incorrect': 0, 'partial': 0}
            
            if entry.predicted_directional_bias == 'correct':
                bias_accuracy[bias]['correct'] += 1
            elif entry.predicted_directional_bias == 'incorrect':
                bias_accuracy[bias]['incorrect'] += 1
            else:
                bias_accuracy[bias]['partial'] += 1
        
        # Find weakest bias
        weakest_bias = None
        worst_accuracy = 100
        
        for bias, stats in bias_accuracy.items():
            total = stats['correct'] + stats['incorrect'] + stats['partial']
            if total >= 3:
                accuracy = (stats['correct'] / total) * 100
                if accuracy < worst_accuracy:
                    worst_accuracy = accuracy
                    weakest_bias = bias
        
        if weakest_bias and worst_accuracy < 60:
            stats = bias_accuracy[weakest_bias]
            total = stats['correct'] + stats['incorrect'] + stats['partial']
            
            return {
                'type': 'bias',
                'title': f'{weakest_bias.title()} Bias Accuracy Low',
                'severity_score': int(100 - worst_accuracy),
                'description': f'Your {weakest_bias} bias predictions are only {worst_accuracy:.1f}% accurate.',
                'statistics': f'{stats["incorrect"]} incorrect predictions out of {total} {weakest_bias} trades ({worst_accuracy:.0f}% accuracy)',
                'suggestion': f'Review your {weakest_bias} bias analysis methodology. Consider waiting for stronger confirmation signals before entering {weakest_bias} positions. Study successful {weakest_bias} trades to identify patterns.',
                'filter_params': {'bias': weakest_bias, 'predicted_directional_bias': 'incorrect'}
            }
        return None
    
    @staticmethod
    def _analyze_entry_timing_issues(entries):
        """Analyze entry quality issues."""
        if not entries.exists():
            return None
        
        entry_quality_stats = {}
        for entry in entries:
            quality = entry.entry_quality
            if quality not in entry_quality_stats:
                entry_quality_stats[quality] = {'wins': 0, 'losses': 0}
            
            if entry.outcome == 'win':
                entry_quality_stats[quality]['wins'] += 1
            else:
                entry_quality_stats[quality]['losses'] += 1
        
        # Focus on problematic entry types
        problematic = ['chased', 'early', 'late', 'stop loss issue']
        problem_trades = {k: v for k, v in entry_quality_stats.items() if k in problematic}
        
        if problem_trades:
            # Find most common problem
            most_common = max(problem_trades.items(), 
                            key=lambda x: x[1]['wins'] + x[1]['losses'])
            quality_type, stats = most_common
            total = stats['wins'] + stats['losses']
            
            if total >= 3:
                loss_rate = (stats['losses'] / total) * 100
                
                if loss_rate > 60:
                    quality_titles = {
                        'chased': 'Chased Entries',
                        'early': 'Early Entries',
                        'late': 'Late Entries',
                        'stop loss issue': 'Stop Loss Placement'
                    }
                    
                    return {
                        'type': 'entry_timing',
                        'title': f'{quality_titles.get(quality_type, quality_type.title())} Reduce Accuracy',
                        'severity_score': int(loss_rate),
                        'description': f'Your {quality_type} entries have a {loss_rate:.0f}% loss rate, significantly higher than ideal.',
                        'statistics': f'{stats["losses"]} losses out of {total} {quality_type} entries ({loss_rate:.0f}% loss rate)',
                        'suggestion': ErrorPatternAnalyzer._get_entry_timing_suggestion(quality_type),
                        'filter_params': {'entry_quality': quality_type, 'outcome': 'loss'}
                    }
        return None
    
    @staticmethod
    def _analyze_poi_issues(entries):
        """Analyze POI performance issues."""
        if not entries.exists():
            return None
        
        poi_performance = {}
        for entry in entries:
            poi = entry.poi_performance
            if poi not in poi_performance:
                poi_performance[poi] = {'wins': 0, 'losses': 0}
            
            if entry.outcome == 'win':
                poi_performance[poi]['wins'] += 1
            else:
                poi_performance[poi]['losses'] += 1
        
        # Find problematic POI types
        problematic_poi = ['rejected', 'overshot', 'no htf poi']
        problem_pois = {k: v for k, v in poi_performance.items() if k in problematic_poi}
        
        if problem_pois:
            worst_poi = max(problem_pois.items(), 
                          key=lambda x: x[1]['losses'] / (x[1]['wins'] + x[1]['losses']) if (x[1]['wins'] + x[1]['losses']) > 0 else 0)
            
            poi_type, stats = worst_poi
            total = stats['wins'] + stats['losses']
            
            if total >= 3:
                loss_rate = (stats['losses'] / total) * 100
                
                if loss_rate > 50:
                    return {
                        'type': 'poi',
                        'title': f'POI {poi_type.replace("_", " ").title()} Leads to Losses',
                        'severity_score': int(loss_rate),
                        'description': f'Trades where POI {poi_type} have a {loss_rate:.0f}% loss rate.',
                        'statistics': f'{stats["losses"]} losses when POI {poi_type} ({loss_rate:.0f}% loss rate)',
                        'suggestion': f'Avoid trading when POI {poi_type}. Wait for POI to be respected perfectly or look for better setups. Review your POI identification process.',
                        'filter_params': {'poi_performance': poi_type, 'outcome': 'loss'}
                    }
        return None
    
    @staticmethod
    def _analyze_session_performance(entries):
        """Analyze session-based performance."""
        if not entries.exists():
            return None
        
        session_stats = {}
        for entry in entries:
            session = entry.session
            if session not in session_stats:
                session_stats[session] = {'wins': 0, 'losses': 0}
            
            if entry.outcome == 'win':
                session_stats[session]['wins'] += 1
            else:
                session_stats[session]['losses'] += 1
        
        # Find worst performing session
        worst_session = None
        worst_win_rate = 100
        
        for session, stats in session_stats.items():
            total = stats['wins'] + stats['losses']
            if total >= 3:
                win_rate = (stats['wins'] / total) * 100
                if win_rate < worst_win_rate:
                    worst_win_rate = win_rate
                    worst_session = session
        
        if worst_session and worst_win_rate < 45:
            stats = session_stats[worst_session]
            total = stats['wins'] + stats['losses']
            
            return {
                'type': 'session',
                'title': f'Weak Performance in {worst_session} Session',
                'severity_score': int(100 - worst_win_rate),
                'description': f'Your win rate during {worst_session} session is {worst_win_rate:.1f}%, significantly below average.',
                'statistics': f'{stats["losses"]} losses out of {total} trades during {worst_session} session ({worst_win_rate:.0f}% win rate)',
                'suggestion': f'Consider avoiding {worst_session} session trades or focus on improving your setup identification during this time. Analyze what makes other sessions more successful.',
                'filter_params': {'session': worst_session, 'outcome': 'loss'}
            }
        return None
    
    @staticmethod
    def _analyze_market_behavior_issues(entries):
        """Analyze market behavior issues."""
        if not entries.exists():
            return None
        
        behavior_stats = {}
        for entry in entries:
            behavior = entry.market_behaviour
            if behavior not in behavior_stats:
                behavior_stats[behavior] = {'wins': 0, 'losses': 0}
            
            if entry.outcome == 'win':
                behavior_stats[behavior]['wins'] += 1
            else:
                behavior_stats[behavior]['losses'] += 1
        
        # Focus on problematic behaviors
        problematic = ['opposite', 'surprise', 'hit stop then reversed', 'choppy']
        problem_behaviors = {k: v for k, v in behavior_stats.items() if k in problematic}
        
        if problem_behaviors:
            worst = max(problem_behaviors.items(), 
                      key=lambda x: x[1]['losses'] / (x[1]['wins'] + x[1]['losses']) if (x[1]['wins'] + x[1]['losses']) > 0 else 0)
            
            behavior, stats = worst
            total = stats['wins'] + stats['losses']
            
            if total >= 3:
                loss_rate = (stats['losses'] / total) * 100
                
                if loss_rate > 60:
                    return {
                        'type': 'behavior',
                        'title': f'Market {behavior.replace("_", " ").title()} Causes Losses',
                        'severity_score': int(loss_rate),
                        'description': f'When market behaves {behavior}, your loss rate is {loss_rate:.0f}%.',
                        'statistics': f'{stats["losses"]} losses when market {behavior} ({loss_rate:.0f}% loss rate)',
                        'suggestion': ErrorPatternAnalyzer._get_behavior_suggestion(behavior),
                        'filter_params': {'market_behaviour': behavior, 'outcome': 'loss'}
                    }
        return None
    
    @staticmethod
    def _calculate_chart_data(patterns):
        """Calculate data for visualization charts."""
        pattern_types = {}
        for pattern in patterns:
            ptype = pattern.get('type', 'other')
            if ptype not in pattern_types:
                pattern_types[ptype] = 0
            pattern_types[ptype] += 1
        
        return {
            'labels': list(pattern_types.keys()),
            'counts': list(pattern_types.values())
        }
    
    @staticmethod
    def _get_market_condition_suggestion(condition):
        """Get suggestion based on market condition."""
        suggestions = {
            'Consolidating': 'Avoid trading during consolidation unless you have clear range boundaries. Wait for breakout confirmation or trade the range edges.',
            'Trending Up': 'Focus on pullback entries rather than chasing. Wait for retests of support levels.',
            'Trending Down': 'Look for retracements to resistance levels. Avoid buying dips in strong downtrends.'
        }
        return suggestions.get(condition, 'Review your strategy for this market condition.')
    
    @staticmethod
    def _get_entry_timing_suggestion(quality):
        """Get suggestion based on entry quality."""
        suggestions = {
            'chased': 'Avoid chasing price moves. Wait for proper retests and confirmations before entering.',
            'early': 'Be more patient. Wait for full confirmation signals before entering trades.',
            'late': 'Your entries are too late. Consider entering on initial setup confirmation rather than waiting.',
            'stop loss issue': 'Review your stop loss placement. Ensure stops are placed beyond significant support/resistance levels.'
        }
        return suggestions.get(quality, 'Review your entry timing and methodology.')
    
    @staticmethod
    def _get_behavior_suggestion(behavior):
        """Get suggestion based on market behavior."""
        suggestions = {
            'opposite': 'Market moved against your bias. Strengthen your bias confirmation process and wait for clearer signals.',
            'surprise': 'Unexpected market moves indicate you may be missing key information. Review news, economic events, and market context before trading.',
            'hit stop then reversed': 'Your stop losses may be too tight or placed incorrectly. Review stop placement strategy.',
            'choppy': 'Avoid trading in choppy markets. Wait for clearer trends and better liquidity conditions.'
        }
        return suggestions.get(behavior, 'Review your trading strategy for this market behavior.')

