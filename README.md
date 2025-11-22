# Officiating Tracker

A Django web application designed to track income, travel expenses, and mileage for seasonal sports officiating. Features automatic distance calculation using Google Maps API and manages game assignments, sites, and leagues.

## Features

- **Game Management**: Track game dates, sites, leagues, positions, and payment status
- **Automatic Mileage Calculation**: Uses Google Maps Distance Matrix API to calculate driving distance from home location to game sites
- **Site & League Management**: Organize games by venue and league/organization
- **User Profiles**: Store home location for automatic mileage calculations
- **Payment Tracking**: Monitor fee and mileage payment status
- **Responsive UI**: Built with Tailwind CSS for a modern, mobile-friendly interface

## Tech Stack

- **Backend**: Django 5.2.4
- **Database**: SQLite (configurable via DATABASE_URL)
- **Frontend**: Tailwind CSS 3.x
- **API Integration**: Google Maps Distance Matrix API
- **Environment Management**: uv (Python package manager)
- **Testing**: pytest with Django integration

## Prerequisites

- Python 3.12 or higher
- Node.js and npm (for Tailwind CSS)
- Google Maps API key
- uv package manager

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ncarsner/officiating-tracker.git
cd officiating-tracker
```

### 2. Set Up Python Environment

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file in the project root (use `.env-template` as reference):

```bash
cp .env-template .env
```

Edit `.env` with your settings:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
API_KEY=your-google-maps-api-key
```

**Note**: Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/) with Distance Matrix API enabled.

### 4. Install Node Dependencies

```bash
npm install
```

### 5. Build CSS

```bash
# One-time build
npm run build

# Or run in watch mode during development
npm run dev
```

### 6. Run Database Migrations

```bash
uv run python manage.py migrate
```

### 7. Create a Superuser (Optional)

```bash
uv run python manage.py createsuperuser
```

## Running the Application

### Start the Development Server

```bash
uv run python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

### Run with Tailwind Watch Mode

For active development with auto-rebuilding CSS:

```bash
# Terminal 1: Tailwind watch mode
npm run dev

# Terminal 2: Django server
uv run python manage.py runserver
```

## Project Structure

```
officiating-tracker/
├── project/               # Django project settings
│   ├── settings.py        # Main configuration
│   ├── urls.py            # Root URL configuration
│   └── static/            # Static files (CSS, JS)
│       └── css/
│           ├── input.css  # Tailwind source
│           └── output.css # Compiled CSS
├── tracker/               # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── forms.py           # Form definitions
│   ├── urls.py            # App URL routing
│   ├── utils.py           # Utility functions (mileage, et al)
│   ├── tests.py           # Test suite
│   └── templates/         # HTML templates
│       └── game/          # Game-related templates
├── manage.py              # Django management script
├── pyproject.toml         # Python dependencies
├── package.json           # Node.js dependencies
├── tailwind.config.js     # Tailwind configuration
└── .env                   # Environment variables (not in git)
```

## Key Models

- **Game**: Tracks individual game assignments with date, site, league, fees, mileage
- **Site**: Venue information with name and address
- **League**: Organization/league details with assignor and fee information
- **Profile**: User profile with home location for mileage calculations

## Testing

Run the test suite:

**Note**: The test suite is currently incomplete and under active development.

```bash
# Run all tests
uv run python manage.py test

# Run specific test class
uv run python manage.py test tracker.tests.GameModelTest

# Run with pytest
uv run pytest

# Run with coverage
uv run pytest --cov=tracker
```

## Development Tools

- **Django Debug Toolbar**: Enabled in DEBUG mode at `/__debug__/`
- **Pre-commit Hooks**: Configured with isort and Ruff for code quality
- **VS Code Settings**: Included for Python environment configuration

## API Integration

The application uses Google Maps Distance Matrix API to automatically calculate driving distance between the user's home location and game sites.

**Default origin** (for testing): `123 Main St, Nashville, TN 37203`

When user authentication is fully implemented, each user's profile location will be used as the origin.

## Mileage Calculation Behavior

- **Creating new games**: Mileage is automatically calculated and hidden from user
- **Editing existing games**: Mileage field is editable
  - If unchanged, mileage is recalculated based on current site
  - If manually changed, user's value is preserved
  - Helpful for overriding calculated values when needed

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/<feature-name>`)
3. Commit your changes
4. Push to the branch (`git push origin feature/<feature-name>`)
5. Open a Pull Request

## License

TBD

## Author

Nicholas Carsner

## Links

- **Repository**: [https://github.com/ncarsner/officiating-tracker](https://github.com/ncarsner/officiating-tracker)
- **Issues**: [https://github.com/ncarsner/officiating-tracker/issues](https://github.com/ncarsner/officiating-tracker/issues)
