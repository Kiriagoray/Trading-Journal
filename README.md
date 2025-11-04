# JournalX

A comprehensive trading journal application designed for professional traders who demand detailed analytics, intelligent insights, and a streamlined workflow for tracking trading performance.

## Overview

JournalX provides a complete solution for documenting, analyzing, and improving trading performance. Whether you're tracking live trades, planning entries, or backtesting strategies, the platform offers the tools needed to maintain detailed records and derive actionable insights from your trading data.

## Key Features

### Trading Journals
- **After Trade Journal** - Document completed trades with comprehensive metrics including entry/exit points, profit/loss, session analysis, and market conditions
- **Pre Trade Journal** - Plan and prepare trades with detailed setup documentation, market analysis, and risk assessment
- **Backtesting Journal** - Record strategy testing results, performance metrics, and validation outcomes

### Analytics & Insights
- **Performance Dashboard** - Real-time KPIs including win rate, profit factor, average win/loss, and trading streaks
- **Trade Statistics** - Comprehensive analytics with performance breakdowns by currency pair, trading session, and time period
- **Error Pattern Detection** - AI-powered analysis to identify recurring mistakes and trading weaknesses
- **Trade Comparison** - Side-by-side comparison tool to analyze differences between any two trades

### Productivity Tools
- **Trade Templates** - Save and reuse common trade setups for rapid entry
- **Trade Duplication** - Clone previous trades with a single click
- **Global Search** - Search across all journal types with intelligent filtering
- **Lot Size Calculator** - Calculate position sizes tailored for Deriv broker specifications
- **Calendar View** - Visual timeline of all trading activity
- **CSV Export** - Export data for external analysis and reporting

### User Experience
- **Responsive Design** - Fully functional across desktop, tablet, and mobile devices
- **Dark/Light Mode** - Seamless theme switching for comfortable viewing in any environment
- **Modern Interface** - Clean, intuitive design built with Bootstrap 5
- **Interactive Charts** - Dynamic visualizations powered by Chart.js
- **File Management** - Secure storage for trade screenshots and chart images

## Technology

Built with modern web technologies to ensure reliability, performance, and maintainability.

- **Backend**: Django 5.2
- **Frontend**: Bootstrap 5.3, Bootstrap Icons
- **Visualization**: Chart.js
- **Database**: PostgreSQL (production), SQLite (development)
- **Runtime**: Python 3.11+

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip package manager
- PostgreSQL (for production deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd journal_project
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file with your configuration:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser account:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the application:
   Open `http://127.0.0.1:8000` in your browser and log in with your superuser credentials.

## Usage

### Creating Trade Entries

**After Trade Entry**
1. Navigate to "After Trade" → "New Entry"
2. Complete trade details including pair, date, session, bias, and outcome
3. Upload relevant screenshots or charts
4. Add observations and lessons learned
5. Review AI-generated trade summary

**Pre Trade Entry**
1. Navigate to "Pre Trade" → "New Entry"
2. Document your trade plan and setup conditions
3. Record market analysis and entry criteria
4. Upload setup images for reference

**Backtest Entry**
1. Navigate to "Backtesting" → "New Entry"
2. Document strategy parameters and test conditions
3. Record outcomes and performance metrics
4. Note any insights or adjustments needed

### Dashboard

The command center provides an overview of your trading performance:
- Key performance indicators (KPIs) at a glance
- Visual charts showing performance trends
- Quick access to recent entries
- Performance breakdowns by pair and session

### Data Management

- **Export**: Use the export functionality to download CSV files of your journal data
- **Templates**: Create reusable templates for common trade setups
- **Search**: Use global search to quickly find specific trades or entries
- **Filtering**: Apply advanced filters to analyze subsets of your data

## Configuration

### Database

The application supports both SQLite (development) and PostgreSQL (production). Configure your database connection via environment variables or Django settings.

### Static Files

Static files are served using WhiteNoise in production. No additional web server configuration is required for static file serving.

### Media Files

User-uploaded files are stored in the `media/` directory. For production deployments, configure appropriate storage backends or use cloud storage services.

### Email Configuration

Configure email settings for password reset and notifications:
- `EMAIL_BACKEND`: SMTP backend for production
- `EMAIL_HOST`: SMTP server address
- `EMAIL_PORT`: SMTP port (typically 587 for TLS)
- `EMAIL_HOST_USER`: SMTP username
- `EMAIL_HOST_PASSWORD`: SMTP password

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

## Deployment

The application is configured for deployment on modern PaaS platforms. Key requirements:

- Set `DEBUG=False` in production
- Configure `ALLOWED_HOSTS` appropriately
- Use environment variables for sensitive settings
- Ensure static files are collected (`python manage.py collectstatic`)
- Configure proper database connection
- Enable HTTPS in production

## Security

Production deployments should:
- Use strong, unique `SECRET_KEY` values
- Enable HTTPS/SSL
- Configure proper CORS settings if needed
- Use secure session and CSRF cookie settings
- Implement proper authentication and authorization
- Regularly update dependencies

## License

This project is for personal use. Modify and distribute as needed.

---

**Author**: Raymond
