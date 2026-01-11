# Project Tech Stack

> **Note**: This is a template file. Customize it with your project's actual technology stack.
> Delete this note after filling out.

## Frontend

### Framework & Library
- **Framework**: [e.g., React 18.2, Vue 3, Svelte, Angular 16]
- **Language**: [e.g., TypeScript 5.0, JavaScript ES2022]
- **Build Tool**: [e.g., Vite 4.0, Webpack 5, Parcel]

### State Management
- **Library**: [e.g., Redux Toolkit, Zustand, Recoil, Context API]
- **Approach**: [Brief description of state management strategy]

### Styling
- **Method**: [e.g., Tailwind CSS, CSS Modules, Styled Components, SASS]
- **Component Library**: [e.g., Material-UI, Ant Design, Chakra UI, Custom]

### Testing
- **Unit Tests**: [e.g., Vitest, Jest]
- **Component Tests**: [e.g., React Testing Library, Vue Test Utils]
- **E2E Tests**: [e.g., Playwright, Cypress, Selenium]

### Other Frontend Tools
- **Router**: [e.g., React Router, Vue Router]
- **Forms**: [e.g., React Hook Form, Formik]
- **HTTP Client**: [e.g., Axios, Fetch API]
- **Date/Time**: [e.g., date-fns, Day.js, Luxon]

---

## Backend

### Language & Framework
- **Language**: [e.g., Python 3.11, Node.js 20, Go 1.21, Ruby 3.2]
- **Framework**: [e.g., FastAPI, Express, Django, Rails, Gin]
- **Runtime**: [e.g., Node.js 20 LTS, Python 3.11]

### Database
- **Primary Database**: [e.g., PostgreSQL 15, MySQL 8.0, MongoDB 6.0]
- **ORM/ODM**: [e.g., SQLAlchemy 2.0, Prisma, Mongoose, ActiveRecord]
- **Migrations**: [e.g., Alembic, Knex, Django Migrations]

### Caching
- **Cache System**: [e.g., Redis 7, Memcached]
- **Usage**: [e.g., Session storage, API response caching, rate limiting]

### Background Jobs
- **Queue System**: [e.g., Celery + Redis, Bull, Sidekiq]
- **Use Cases**: [e.g., Email sending, file processing, data exports]

### Testing
- **Unit Tests**: [e.g., Pytest, Jest, RSpec, Go testing]
- **API Tests**: [e.g., Pytest + TestClient, Supertest]
- **Fixtures/Mocking**: [e.g., Factory Boy, Faker, Mock]

### Other Backend Tools
- **Validation**: [e.g., Pydantic, Joi, Zod]
- **Authentication**: [e.g., JWT, Passport.js, OAuth2]
- **API Documentation**: [e.g., OpenAPI/Swagger, API Blueprint]

---

## DevOps & Infrastructure

### Containerization
- **Container Runtime**: [e.g., Docker 24, Podman]
- **Orchestration**: [e.g., Docker Compose, Kubernetes, ECS]

### Cloud Provider
- **Provider**: [e.g., AWS, Google Cloud, Azure, DigitalOcean]
- **Key Services**:
  - Compute: [e.g., EC2, ECS, Cloud Run, App Service]
  - Database: [e.g., RDS, Cloud SQL, Azure Database]
  - Storage**: [e.g., S3, Cloud Storage, Blob Storage]
  - CDN: [e.g., CloudFront, Cloud CDN]

### CI/CD
- **Platform**: [e.g., GitHub Actions, GitLab CI, CircleCI, Jenkins]
- **Deployment Strategy**: [e.g., Rolling, Blue-Green, Canary]

### Infrastructure as Code
- **Tool**: [e.g., Terraform, CloudFormation, Pulumi]
- **Configuration Management**: [e.g., Ansible, Chef, None]

### Monitoring & Logging
- **Monitoring**: [e.g., Datadog, Prometheus + Grafana, CloudWatch]
- **Logging**: [e.g., ELK Stack, Loki, CloudWatch Logs]
- **Error Tracking**: [e.g., Sentry, Rollbar, Bugsnag]

### Web Server
- **Reverse Proxy**: [e.g., Nginx, Traefik, HAProxy]
- **Load Balancer**: [e.g., AWS ALB, Nginx, Cloud Load Balancing]

---

## Development Tools

### Version Control
- **System**: [e.g., Git]
- **Platform**: [e.g., GitHub, GitLab, Bitbucket]

### Package Managers
- **Frontend**: [e.g., npm, yarn, pnpm]
- **Backend**: [e.g., pip + poetry, npm, bundler, go modules]

### Code Quality
- **Linters**:
  - Frontend: [e.g., ESLint, TypeScript]
  - Backend: [e.g., Flake8, Black, Pylint, ESLint]
- **Formatters**:
  - Frontend: [e.g., Prettier]
  - Backend: [e.g., Black, Prettier, gofmt]

### Development Environment
- **Node Version**: [e.g., 20.x LTS]
- **Python Version**: [e.g., 3.11]
- **Required System Tools**: [e.g., Docker, PostgreSQL client, Redis CLI]

---

## Third-Party Services

### Authentication
- [e.g., Auth0, Firebase Auth, Supabase, Custom JWT]

### Email
- [e.g., SendGrid, AWS SES, Mailgun, Postmark]

### File Storage
- [e.g., AWS S3, Cloudinary, UploadCare]

### Payment Processing
- [e.g., Stripe, PayPal, Square]

### Analytics
- [e.g., Google Analytics, Mixpanel, Amplitude, PostHog]

### Other Services
- [List any other third-party integrations]

---

## Development Setup Requirements

### Prerequisites
```bash
# Required versions
Node.js: 20.x LTS
Python: 3.11
Docker: 24.x
PostgreSQL: 15.x (or Docker)
Redis: 7.x (or Docker)
```

### Quick Start
```bash
# Clone repository
git clone <repo-url>
cd <project-name>

# Frontend setup
cd frontend
npm install
npm run dev

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Docker setup (alternative)
docker-compose up
```

---

## Notes

- **Update this file** when adopting new technologies
- **Keep versions current** - specify actual version numbers being used
- **Document reasons** for major technology choices in `design-decisions/`
- **List deprecated technologies** if migrating away from something

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| [Date] | Initial tech stack documentation | [Name] |

