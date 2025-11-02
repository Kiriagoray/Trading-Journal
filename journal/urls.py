from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Root redirect to dashboard
    path('', views.dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='journal/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # After Trade URLs
    path('journal/after/', views.after_trade_list, name='after_trade_list'),
    path('journal/after/create/', views.after_trade_create, name='after_trade_create'),
    path('journal/after/<int:pk>/', views.after_trade_detail, name='after_trade_detail'),
    path('journal/after/<int:pk>/edit/', views.after_trade_edit, name='after_trade_edit'),
    path('journal/after/<int:pk>/delete/', views.after_trade_delete, name='after_trade_delete'),
    path('journal/after/<int:pk>/regenerate-summary/', views.regenerate_summary, name='regenerate_summary'),
    path('journal/after/export_csv/', views.after_trade_export_csv, name='after_trade_export_csv'),
    
    # Pre Trade URLs
    path('journal/pre/', views.pre_trade_list, name='pre_trade_list'),
    path('journal/pre/create/', views.pre_trade_create, name='pre_trade_create'),
    path('journal/pre/<int:pk>/', views.pre_trade_detail, name='pre_trade_detail'),
    path('journal/pre/<int:pk>/edit/', views.pre_trade_edit, name='pre_trade_edit'),
    path('journal/pre/<int:pk>/delete/', views.pre_trade_delete, name='pre_trade_delete'),
    path('journal/pre/export_csv/', views.pre_trade_export_csv, name='pre_trade_export_csv'),
    
    # Backtest URLs
    path('journal/backtest/', views.backtest_list, name='backtest_list'),
    path('journal/backtest/create/', views.backtest_create, name='backtest_create'),
    path('journal/backtest/<int:pk>/', views.backtest_detail, name='backtest_detail'),
    path('journal/backtest/<int:pk>/edit/', views.backtest_edit, name='backtest_edit'),
    path('journal/backtest/<int:pk>/delete/', views.backtest_delete, name='backtest_delete'),
    path('journal/backtest/export_csv/', views.backtest_export_csv, name='backtest_export_csv'),
    
    # Calendar and Daily Summary
    path('journal/calendar/', views.journal_calendar, name='journal_calendar'),
    path('journal/daily/<int:year>-<int:month>-<int:day>/', views.daily_summary, name='daily_summary'),
    
    # Enhanced Features
    path('lot-size-calculator/', views.lot_size_calculator, name='lot_size_calculator'),
    path('trade-comparison/', views.trade_comparison, name='trade_comparison'),
    path('filter-preset/save/', views.save_filter_preset, name='save_filter_preset'),
    path('filter-preset/<int:preset_id>/load/', views.load_filter_preset, name='load_filter_preset'),
    
    # Error Insights
    path('error-insights/', views.error_insights, name='error_insights'),
    path('error-insights/regenerate/', views.regenerate_insights, name='regenerate_insights'),
    path('error-insights/view-trades/', views.view_related_trades, name='view_related_trades'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
]

