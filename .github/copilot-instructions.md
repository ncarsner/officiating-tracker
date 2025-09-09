# Officiating Tracker

Always follow these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

Officiating Tracker is a Django 5.2.4 web application that tracks income and travel expenses for seasonal officiating work. It uses Python 3.12, uv for package management, TailwindCSS for styling, and SQLite for development.

## Quick Setup & Validation
**CRITICAL: Use these exact commands in this order. All commands have been validated to work.**

1. **Install uv package manager** (if not available):
   ```bash
   pip install uv
   ```
   - Takes ~10 seconds. Always check with `uv --version` first.

2. **Install Python dependencies**:
   ```bash
   uv sync
   ```
   - Takes ~1-2 seconds. NEVER CANCEL - always wait for completion.

3. **Install Node.js dependencies for TailwindCSS**:
   ```bash
   npm install
   ```
   - Takes ~10-15 seconds. NEVER CANCEL - always wait for completion.

4. **Create environment file**:
   ```bash
   cp .env-template .env
   ```
   - Edit `.env` and set: `SECRET_KEY=dev-secret-key`, `DEBUG=True`, `ALLOWED_HOSTS=localhost,127.0.0.1`, `DATABASE_URL=sqlite:///db.sqlite3`

5. **Setup database**:
   ```bash
   uv run python manage.py migrate
   ```
   - Takes ~1-2 seconds. Creates SQLite database with all tables.

6. **Build TailwindCSS**:
   ```bash
   npm run build
   ```
   - Takes ~1 second. Ignore browserslist warnings - they are non-critical.

7. **Create superuser for admin access**:
   ```bash
   echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | uv run python manage.py shell
   ```

## Running the Application

**Development server**:
```bash
uv run python manage.py runserver 8000
```
- Starts immediately (~1 second)
- Access at: http://localhost:8000/
- Admin at: http://localhost:8000/admin/ (login: admin/admin123)
- NEVER CANCEL - always use Ctrl+C to stop properly

**TailwindCSS watch mode** (for development):
```bash
npm run dev
```
- Watches for CSS changes and rebuilds automatically
- Run in separate terminal alongside Django server

## Code Quality & Validation

**ALWAYS run these before committing changes:**

1. **Lint code**:
   ```bash
   uv run ruff check
   ```
   - Takes <0.1 seconds. Must show "All checks passed!"

2. **Format code**:
   ```bash
   uv run ruff format
   ```
   - Takes <0.1 seconds. Auto-formats Python code.

3. **Fix linting issues**:
   ```bash
   uv run ruff check --fix
   ```
   - Automatically fixes most linting issues.

4. **Run tests** (currently no tests exist):
   ```bash
   uv run python manage.py test
   ```
   - Takes <1 second. Shows "NO TESTS RAN" currently.

## Manual Validation Scenarios

**ALWAYS test these scenarios after making changes:**

1. **Homepage functionality**:
   - Navigate to http://localhost:8000/
   - Verify game tracking form displays with date picker, site/league dropdowns
   - Test "Add Game" button (should submit form)

2. **Admin interface**:
   - Login to http://localhost:8000/admin/ with admin/admin123
   - Verify all models appear: Games, Leagues, Sites, Users, Groups
   - Test adding a new League or Site entry
   - Verify data saves correctly

3. **Static assets**:
   - Verify TailwindCSS loads (check developer tools for /static/css/output.css)
   - Verify styling appears correctly on both homepage and admin

## Repository Structure

```
.
├── .env-template              # Environment variables template
├── .pre-commit-config.yaml    # Pre-commit hooks with ruff
├── .python-version           # Python 3.12 requirement
├── manage.py                 # Django management commands
├── package.json              # Node.js dependencies (TailwindCSS)
├── pyproject.toml            # Python dependencies (uv format)
├── tailwind.config.js        # TailwindCSS configuration
├── project/                  # Django project settings
│   ├── settings.py           # Main Django settings
│   ├── urls.py              # URL routing
│   ├── static/css/          # TailwindCSS input/output files
│   └── wsgi.py              # WSGI configuration
└── tracker/                  # Main Django app
    ├── models.py            # Game, League, Site, Profile models
    ├── views.py             # Application views
    ├── urls.py              # App URL routing
    ├── forms.py             # Django forms
    ├── admin.py             # Admin interface configuration
    ├── templates/           # HTML templates
    └── migrations/          # Database migrations
```

## Known Issues & Warnings

- **Django Debug Toolbar Warning**: `urls.W005` about duplicate 'djdt' namespace - this is non-critical and safe to ignore
- **Browserslist Warning**: TailwindCSS shows browserslist outdated warning - this is cosmetic and doesn't affect functionality
- **No Tests**: The repository currently has no test suite - consider adding tests when making significant changes

## Development Workflow

1. **Start development**:
   - Terminal 1: `uv run python manage.py runserver 8000`
   - Terminal 2: `npm run dev` (if changing CSS)

2. **Make changes**:
   - Edit Python files in `tracker/` or `project/`
   - Edit templates in `tracker/templates/`
   - Edit CSS in `project/static/css/input.css`

3. **Before committing**:
   - `uv run ruff format`
   - `uv run ruff check`
   - Test homepage and admin functionality
   - If models changed: `uv run python manage.py makemigrations && uv run python manage.py migrate`

## Database

- **Development**: SQLite database (`db.sqlite3`) - created automatically
- **Models**: Game, League, Site, Profile (linked to User)
- **Admin Access**: All models registered and accessible via admin interface
- **Reset Database**: Delete `db.sqlite3`, run migrations, recreate superuser

## Static Files

- **CSS Framework**: TailwindCSS
- **Input**: `project/static/css/input.css`
- **Output**: `project/static/css/output.css` (built by npm)
- **Production Build**: `npm run build` (minified)
- **Development**: `npm run dev` (watch mode)

## Common Commands Reference

```bash
# Setup (one-time)
uv sync && npm install && cp .env-template .env
uv run python manage.py migrate
npm run build

# Daily development
uv run python manage.py runserver 8000  # Start server
npm run dev                              # Watch CSS changes

# Code quality
uv run ruff format                       # Format code
uv run ruff check                        # Check linting
uv run ruff check --fix                  # Fix issues

# Database operations
uv run python manage.py makemigrations   # Create migrations
uv run python manage.py migrate          # Apply migrations
uv run python manage.py shell            # Django shell

# Admin
uv run python manage.py createsuperuser  # Create admin user
```

**⚠️ NEVER CANCEL long-running commands. All build/install commands complete in under 15 seconds.**