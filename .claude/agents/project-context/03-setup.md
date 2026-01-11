# Development Environment Setup

> **Note**: This is a template file. Customize it with your project's actual setup instructions.
> Delete this note after filling out.

## Prerequisites

### Required Software

| Software | Minimum Version | Recommended | Installation |
|----------|----------------|-------------|--------------|
| Node.js | 18.x | 20.x LTS | https://nodejs.org |
| Python | 3.10 | 3.11 | https://python.org |
| Git | 2.30 | Latest | https://git-scm.com |
| Docker | 20.x | 24.x | https://docker.com |
| PostgreSQL | 14 | 15 | https://postgresql.org |

### Optional Tools
- **Redis**: For caching (can use Docker)
- **pgAdmin**: PostgreSQL GUI client
- **Postman/Insomnia**: API testing
- **VS Code**: Recommended editor with extensions

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd <project-name>

# Copy environment variables
cp .env.example .env
# Edit .env with your values

# Start all services
docker-compose up -d

# Frontend will be at: http://localhost:3000
# Backend API will be at: http://localhost:8000
# API docs will be at: http://localhost:8000/docs
```

### Option 2: Local Development

#### 1. Clone Repository
```bash
git clone <repository-url>
cd <project-name>
```

#### 2. Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# OR with poetry:
poetry install

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
python manage.py migrate
# OR with Alembic:
alembic upgrade head

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
# OR with uvicorn:
uvicorn app.main:app --reload

# Backend API should be running at: http://localhost:8000
```

#### 3. Setup Frontend

```bash
# Navigate to frontend directory (open new terminal)
cd frontend

# Install dependencies
npm install
# OR with yarn:
yarn install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
# OR with yarn:
yarn dev

# Frontend should be running at: http://localhost:3000
```

---

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis (if using)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Environment
ENVIRONMENT=development
DEBUG=True

# Third-party services
SENDGRID_API_KEY=your-sendgrid-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=your-bucket-name

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env.local)

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_FEATURE_X=true

# Third-party services
VITE_GOOGLE_ANALYTICS_ID=
VITE_SENTRY_DSN=
```

**Important**: Never commit `.env` files to version control!

---

## Database Setup

### Using Docker

```bash
# Start PostgreSQL container
docker run --name postgres-dev \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=myapp_dev \
  -p 5432:5432 \
  -d postgres:15-alpine

# Verify it's running
docker ps
```

### Local PostgreSQL Installation

```bash
# Create database
createdb myapp_dev

# Or using psql:
psql -U postgres
CREATE DATABASE myapp_dev;
\q

# Run migrations
cd backend
python manage.py migrate
```

### Database Seeding (Optional)

```bash
# Seed with sample data
python manage.py seed
# OR
python scripts/seed_database.py
```

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_users.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run E2E tests
npm run test:e2e

# Run E2E tests in UI mode
npx playwright test --ui
```

---

## Development Workflow

### Starting Development

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python manage.py runserver

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Watch tests (optional)
cd frontend
npm run test:watch
```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Write tests
   - Update documentation if needed

3. **Run tests locally**
   ```bash
   # Backend
   pytest

   # Frontend
   npm test
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to GitHub/GitLab
   - Create PR from your branch
   - Fill out PR template
   - Request review

---

## Common Tasks

### Adding a New Dependency

#### Frontend
```bash
cd frontend

# Install and save to package.json
npm install package-name

# For dev dependencies
npm install --save-dev package-name

# Update lock file
npm install
```

#### Backend
```bash
cd backend

# With pip
pip install package-name
pip freeze > requirements.txt

# With poetry
poetry add package-name

# For dev dependencies
poetry add --group dev package-name
```

### Creating Database Migration

#### Django
```bash
# After modifying models
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

#### Alembic
```bash
# After modifying models
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head
```

### Resetting Database

```bash
# Django
python manage.py flush
python manage.py migrate

# Alembic
alembic downgrade base
alembic upgrade head

# Or drop and recreate
dropdb myapp_dev
createdb myapp_dev
alembic upgrade head
```

### Updating Dependencies

#### Frontend
```bash
# Check for outdated packages
npm outdated

# Update all dependencies
npm update

# Update specific package
npm update package-name
```

#### Backend
```bash
# With pip
pip list --outdated
pip install --upgrade package-name

# With poetry
poetry show --outdated
poetry update package-name
```

---

## IDE Setup

### VS Code (Recommended)

#### Recommended Extensions
```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "prisma.prisma",
    "ms-azuretools.vscode-docker"
  ]
}
```

#### Settings (.vscode/settings.json)
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  },
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true,
  "typescript.updateImportsOnFileMove.enabled": "always"
}
```

---

## Troubleshooting

### Backend Issues

#### Database Connection Error
```
Problem: Can't connect to PostgreSQL
Solution:
1. Check if PostgreSQL is running: pg_isready
2. Verify DATABASE_URL in .env
3. Check PostgreSQL logs
4. Ensure database exists: psql -l
```

#### Import Errors
```
Problem: ModuleNotFoundError
Solution:
1. Ensure virtual environment is activated
2. Reinstall dependencies: pip install -r requirements.txt
3. Check PYTHONPATH
```

#### Migration Issues
```
Problem: Migration conflicts
Solution:
1. Check migration history: python manage.py showmigrations
2. Resolve conflicts manually
3. Or reset: python manage.py migrate <app> zero
```

### Frontend Issues

#### Module Not Found
```
Problem: Cannot find module 'package-name'
Solution:
1. Delete node_modules and package-lock.json
2. Run npm install
3. Restart dev server
```

#### Port Already in Use
```
Problem: Port 3000 is already in use
Solution:
1. Find process: lsof -i :3000 (Mac/Linux) or netstat -ano | findstr :3000 (Windows)
2. Kill process: kill -9 <PID>
3. Or use different port: PORT=3001 npm run dev
```

#### Build Errors
```
Problem: TypeScript compilation errors
Solution:
1. Delete .next or dist directory
2. Run npm run build
3. Check tsconfig.json
4. Ensure all types are installed: npm install --save-dev @types/node
```

### Docker Issues

#### Container Won't Start
```
Problem: Docker container exits immediately
Solution:
1. Check logs: docker logs <container-name>
2. Check docker-compose.yml configuration
3. Verify environment variables
4. Check port conflicts: docker ps -a
```

#### Database Container Issues
```
Problem: Database data persisted incorrectly
Solution:
1. Remove volume: docker-compose down -v
2. Recreate: docker-compose up -d
```

---

## Performance Tips

### Backend Performance
- Use database connection pooling
- Enable query caching with Redis
- Use select_related/prefetch_related to avoid N+1 queries
- Enable compression middleware
- Use async views where appropriate

### Frontend Performance
- Enable code splitting
- Use lazy loading for routes
- Optimize images (WebP format, appropriate sizes)
- Use React.memo for expensive components
- Enable production build optimizations

---

## Useful Commands Cheat Sheet

```bash
# Backend
python manage.py runserver          # Start dev server
python manage.py migrate            # Run migrations
python manage.py makemigrations     # Create migrations
python manage.py createsuperuser    # Create admin user
python manage.py shell              # Open Django shell
pytest                              # Run tests

# Frontend
npm run dev                         # Start dev server
npm run build                       # Build for production
npm run preview                     # Preview production build
npm test                            # Run tests
npm run lint                        # Run linter
npm run format                      # Format code

# Docker
docker-compose up -d                # Start all services
docker-compose down                 # Stop all services
docker-compose logs -f              # View logs
docker-compose restart <service>    # Restart service
docker-compose exec backend bash    # Open shell in container

# Git
git status                          # Check status
git add .                           # Stage all changes
git commit -m "message"             # Commit changes
git push                            # Push to remote
git pull                            # Pull from remote
git checkout -b branch-name         # Create new branch
```

---

## Getting Help

- **Documentation**: Check `/docs` folder
- **API Docs**: http://localhost:8000/docs (when backend running)
- **Team Chat**: [Slack/Discord channel]
- **Issues**: [GitHub/GitLab Issues URL]
- **Wiki**: [Wiki URL if applicable]

---

## Next Steps

Once your environment is set up:

1. Read the **Architecture Documentation** (`01-architecture.md`)
2. Review **Coding Conventions** (`02-conventions.md`)
3. Check **API Documentation** (`04-apis.md`)
4. Look at **Example Features** in the codebase
5. Pick up a "good first issue" and start coding!

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| [Date] | Initial setup documentation | [Name] |
