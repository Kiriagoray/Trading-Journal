"""
API endpoints for dynamic features (dropdowns, sync, etc.)
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import ChoiceOption, ChoiceCategory


@require_http_methods(["GET"])
@login_required
def api_dropdown_choices(request):
    """
    API endpoint to fetch all dropdown choices dynamically
    
    Returns JSON with all available choice categories and their options
    """
    try:
        categories = ChoiceCategory.objects.filter(is_active=True).order_by('order', 'display_name')
        choices_data = {}
        
        for category in categories:
            options = ChoiceOption.objects.filter(
                category=category,
                is_active=True
            ).order_by('order', 'display_label')
            
            choices_data[category.name] = {
                'display_name': category.display_name,
                'description': category.description,
                'options': [
                    {
                        'value': opt.value,
                        'label': opt.display_label,
                        'description': opt.description,
                        'color': opt.color,
                        'order': opt.order
                    }
                    for opt in options
                ]
            }
        
        # Include fallback choices for categories not yet configured
        fallback_categories = {
            'session': {'display_name': 'Trading Session', 'options': [('Asian', 'Asian'), ('London', 'London'), ('NewYork', 'New York')]},
            'bias': {'display_name': 'Bias', 'options': [('bullish', 'Bullish'), ('bearish', 'Bearish')]},
            'market_condition': {'display_name': 'Market Condition', 'options': [
                ('Trending Up', 'Trending Up'),
                ('Trending Down', 'Trending Down'),
                ('Consolidating', 'Consolidating')
            ]},
        }
        
        # Merge with fallbacks if category doesn't exist
        for cat_name, fallback in fallback_categories.items():
            if cat_name not in choices_data:
                choices_data[cat_name] = {
                    'display_name': fallback['display_name'],
                    'description': '',
                    'options': [{'value': v, 'label': l, 'description': '', 'color': '#6c757d', 'order': i} 
                               for i, (v, l) in enumerate(fallback['options'])]
                }
        
        return JsonResponse({
            'success': True,
            'choices': choices_data,
            'timestamp': str(timezone.now())
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def api_dropdown_category(request, category_name):
    """
    Fetch choices for a specific category
    """
    try:
        choices = ChoiceOption.get_choices_for_category(category_name)
        
        if choices:
            return JsonResponse({
                'success': True,
                'category': category_name,
                'choices': [{'value': v, 'label': l} for v, l in choices]
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Category "{category_name}" not found or has no active options'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

