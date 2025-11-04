"""
Management command to initialize choice categories and options from existing constants
Run: python manage.py setup_choice_categories
"""
from django.core.management.base import BaseCommand
from journal.models import ChoiceCategory, ChoiceOption


class Command(BaseCommand):
    help = 'Initialize choice categories and options for the configuration system'

    def handle(self, *args, **options):
        # Define all categories and their default options
        categories_data = {
            'session': {
                'display_name': 'Trading Session',
                'description': 'Trading session choices (Asian, London, New York)',
                'options': [
                    ('Asian', 'Asian', 0),
                    ('London', 'London', 1),
                    ('NewYork', 'New York', 2),
                ]
            },
            'bias': {
                'display_name': 'Market Bias',
                'description': 'Bullish or Bearish market bias',
                'options': [
                    ('bullish', 'Bullish', 0),
                    ('bearish', 'Bearish', 1),
                ]
            },
            'market_condition': {
                'display_name': 'Market Condition',
                'description': 'Current market condition state',
                'options': [
                    ('Trending Up', 'Trending Up', 0),
                    ('Trending Down', 'Trending Down', 1),
                    ('Consolidating', 'Consolidating', 2),
                ]
            },
            'liquidity_analysis': {
                'display_name': 'Liquidity Analysis',
                'description': 'Liquidity sweep analysis',
                'options': [
                    ('buyside swept', 'Buyside Swept', 0),
                    ('sellside swept', 'Sellside Swept', 1),
                    ('neither', 'Neither', 2),
                    ('both', 'Both', 3),
                    ('london lows swept', 'London Lows Swept', 4),
                ]
            },
            'outcome': {
                'display_name': 'Trade Outcome',
                'description': 'Trade result',
                'options': [
                    ('win', 'Win', 0),
                    ('loss', 'Loss', 1),
                ]
            },
            'discipline_score': {
                'display_name': 'Discipline Score',
                'description': 'Trading discipline rating',
                'options': [
                    ('excellent', 'Excellent', 0),
                    ('good', 'Good', 1),
                    ('average', 'Average', 2),
                    ('poor', 'Poor', 3),
                    ('very poor', 'Very Poor', 4),
                ]
            },
            'entry_quality': {
                'display_name': 'Entry Quality',
                'description': 'Quality of trade entry',
                'options': [
                    ('perfect', 'Perfect', 0),
                    ('chased', 'Chased', 1),
                    ('early', 'Early', 2),
                    ('late', 'Late', 3),
                    ('stop loss issue', 'Stop Loss Issue', 4),
                ]
            },
            'market_behaviour': {
                'display_name': 'Market Behaviour',
                'description': 'Market behavior during trade',
                'options': [
                    ('as expected', 'As Expected', 0),
                    ('choppy', 'Choppy', 1),
                    ('surprise', 'Surprise', 2),
                    ('opposite', 'Opposite', 3),
                    ('hit stop then reversed', 'Hit Stop Then Reversed', 4),
                ]
            },
            'day_of_week': {
                'display_name': 'Day of Week',
                'description': 'Trading day',
                'options': [
                    ('Monday', 'Monday', 0),
                    ('Tuesday', 'Tuesday', 1),
                    ('Wednesday', 'Wednesday', 2),
                    ('Thursday', 'Thursday', 3),
                    ('Friday', 'Friday', 4),
                ]
            },
            'backtest_outcome': {
                'display_name': 'Backtest Outcome',
                'description': 'Backtest result',
                'options': [
                    ('no_setup', 'No Setup', 0),
                    ('win', 'Win', 1),
                    ('loss', 'Loss', 2),
                ]
            },
            'pair': {
                'display_name': 'Currency Pair',
                'description': 'Trading currency pairs',
                'journal_type': 'all',
                'field_name': 'pair',
                'options': [
                    ('AUD/JPY', 'AUD/JPY', 0),
                    ('AUD/USD', 'AUD/USD', 1),
                    ('EUR/AUD', 'EUR/AUD', 2),
                    ('EUR/CAD', 'EUR/CAD', 3),
                    ('EUR/GBP', 'EUR/GBP', 4),
                    ('EUR/JPY', 'EUR/JPY', 5),
                    ('EUR/USD', 'EUR/USD', 6),
                    ('GBP/CHF', 'GBP/CHF', 7),
                    ('GBP/JPY', 'GBP/JPY', 8),
                    ('GBP/USD', 'GBP/USD', 9),
                    ('NZD/USD', 'NZD/USD', 10),
                    ('USD/CAD', 'USD/CAD', 11),
                    ('USD/CHF', 'USD/CHF', 12),
                    ('USD/JPY', 'USD/JPY', 13),
                    ('USD/HKD', 'USD/HKD', 14),
                    ('USD/SGD', 'USD/SGD', 15),
                    ('USD/TRY', 'USD/TRY', 16),
                    ('USD/ZAR', 'USD/ZAR', 17),
                    ('XAU/USD', 'XAU/USD (Gold)', 18),
                ]
            },
        }
        
        created_count = 0
        updated_count = 0
        
        for category_name, category_info in categories_data.items():
            defaults = {
                'display_name': category_info['display_name'],
                'description': category_info['description'],
                'is_active': True,
                'order': len([c for c in categories_data.keys() if list(categories_data.keys()).index(c) < list(categories_data.keys()).index(category_name)]),
                'journal_type': category_info.get('journal_type', 'all'),
                'field_name': category_info.get('field_name', ''),
            }
            
            category, created = ChoiceCategory.objects.get_or_create(
                name=category_name,
                defaults=defaults
            )
            
            if not created:
                category.display_name = category_info['display_name']
                category.description = category_info['description']
                if 'journal_type' in category_info:
                    category.journal_type = category_info['journal_type']
                if 'field_name' in category_info:
                    category.field_name = category_info['field_name']
                category.save()
                updated_count += 1
            else:
                created_count += 1
            
            # Create options
            for value, label, order in category_info['options']:
                ChoiceOption.objects.get_or_create(
                    category=category,
                    value=value,
                    defaults={
                        'display_label': label,
                        'is_active': True,
                        'order': order
                    }
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized {created_count} new categories, updated {updated_count} existing categories'
            )
        )

