# Setup Instructions

To get the Officiating Tracker site running locally:

## Prerequisites
- Python 3.12+
- Node.js and npm

## Installation Steps

1. **Install Python dependencies:**
   ```bash
   pip install dj-database-url>=3.0.1 django>=5.2.4 django-debug-toolbar>=6.0.0 python-decouple>=3.8 python-dotenv>=1.1.1
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   Copy `.env-template` to `.env` and fill in the required values:
   ```bash
   cp .env-template .env
   ```
   
   Minimum required configuration for development:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=sqlite:///db.sqlite3
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Build CSS files:**
   ```bash
   npm run build
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

The site will be available at http://127.0.0.1:8000/
The admin interface will be available at http://127.0.0.1:8000/admin/

## Development

- For CSS development with auto-rebuild: `npm run dev`
- To run Django checks: `python manage.py check`