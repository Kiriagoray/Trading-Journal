# Ray's Trading Journal - Pro Trading Journal Web Application

A comprehensive Django-based trading journal application with advanced analytics, AI-powered insights, and professional dashboard interface.

## Features

### Core Functionality
- **After Trade Journal**: Log completed trades with detailed metrics
- **Pre Trade Journal**: Plan and track upcoming trades
- **Backtesting Journal**: Document strategy testing results
- **AI-Powered Trade Summaries**: Automatic trade analysis and insights
- **Error Pattern Detection**: Identify recurring trading mistakes and weaknesses

### Advanced Features
- **Dashboard/Command Center**: KPIs, charts, and quick stats
- **Trade Comparison Tool**: Side-by-side comparison of any two trades
- **Lot Size Calculator**: Calculate position sizes for Deriv broker
- **Calendar View**: Visual calendar of all trading activity
- **Daily Summary**: Comprehensive daily trade review
- **CSV Export**: Export journal data for external analysis
- **Advanced Filtering**: Filter by pair, date, session, bias, outcome, and more
- **Strategy Tagging**: Tag trades for better organization (if needed)

### User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Mode**: Toggle between light and dark themes
- **Bootstrap 5 UI**: Modern, clean interface
- **Chart.js Analytics**: Interactive charts and visualizations
- **File Uploads**: Store trade screenshots and charts locally
- **Secure**: User authentication with data isolation

## Technology Stack

- **Backend**: Django 5.2
- **Frontend**: Bootstrap 5.3, Bootstrap Icons
- **Charts**: Chart.js
- **Database**: SQLite (default, easily switchable to PostgreSQL)
- **Language**: Python 3.11+

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd journal_project
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django pillow
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser** (admin account)
   ```bash
   python manage.py createsuperuser
   ```

6. **Create media directories** (for file uploads)
   ```bash
   # Windows:
   mkdir media\journal\after_trade
   mkdir media\journal\pre_trade
   mkdir media\journal\pre_trade_outcomes
   mkdir media\journal\backtesting
   
   # macOS/Linux:
   mkdir -p media/journal/{after_trade,pre_trade,pre_trade_outcomes,backtesting}
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and navigate to: `http://127.0.0.1:8000/`
   - Register a new account or use the superuser account

## Project Structure

```
journal_project/
├── journal/                 # Main app
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── forms.py            # Form definitions
│   ├── urls.py             # URL routing
│   ├── services.py         # AI services (summary, error detection)
│   ├── templates/          # HTML templates
│   └── migrations/         # Database migrations
├── journal_project/        # Django project settings
│   ├── settings.py         # Project configuration
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI config
├── media/                  # User uploaded files (not in git)
├── static/                 # Static files
├── db.sqlite3              # SQLite database (not in git)
├── manage.py               # Django management script
└── README.md               # This file
```

## Usage Guide

### Creating Your First Entry

1. **After Trade Entry**: Navigate to "After Trade" → "New Entry"
   - Fill in trade details (pair, date, session, bias, outcome, etc.)
   - Upload chart screenshot
   - Add observations and notes
   - AI summary will be generated automatically

2. **Pre Trade Entry**: Navigate to "Pre Trade" → "New Entry"
   - Plan your trade setup
   - Document conditions and analysis
   - Upload setup images

3. **Backtest Entry**: Navigate to "Backtesting" → "New Entry"
   - Document strategy testing
   - Record outcomes and learnings

### Dashboard Features

- **Command Center**: Overview of all trading activity
- **Quick Stats**: Current streak, win rate, POI scores
- **Charts**: Visual representation of performance metrics
- **Recent Entries**: Quick access to latest trades

### Exporting Data

- Click "Export" in the top navigation
- Select the journal type to export
- CSV file will download with all your data

## Configuration

### Media Files (Uploads)
Media files are stored in `media/journal/` directory. In production:
- Configure `MEDIA_ROOT` and `MEDIA_URL` in `settings.py`
- Use a proper web server (nginx, Apache) to serve media files
- Or use cloud storage (AWS S3, etc.)

### Database
Default is SQLite. For production, switch to PostgreSQL:
1. Install PostgreSQL and `psycopg2`
2. Update `DATABASES` in `settings.py`
3. Run migrations again

### Security
For production deployment:
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Use environment variables for sensitive settings
- Set up proper static file serving
- Enable HTTPS

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
```

### Applying Migrations
```bash
python manage.py migrate
```

## License

This project is for personal use. Modify and use as needed.

## Support

For issues or questions, please check the code comments or create an issue in the repository.

## Author

Ray's Trading Journal - Built for professional traders
