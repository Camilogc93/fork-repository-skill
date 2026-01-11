# Project Context Guide

This guide explains how to set up and maintain project context files that provide agents with essential project information.

## Table of Contents

- [Overview](#overview)
- [Context Files](#context-files)
- [Setting Up Context](#setting-up-context)
- [Context Templates](#context-templates)
- [Maintaining Context](#maintaining-context)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

**Project context** provides agents with the knowledge they need to work effectively on your project. Without proper context, agents won't understand your tech stack, architecture, conventions, or APIs.

### Why Context Matters

1. **Consistency**: All agents work with same standards and patterns
2. **Efficiency**: Agents don't need to search for basic information
3. **Quality**: Agents produce code that fits your project style
4. **Onboarding**: New agents (or resumed agents) quickly understand the project

### Context Structure

Context is organized into 5 files in `.claude/agents/project-context/`:

```
.claude/agents/project-context/
├── 00-tech-stack.md      # Technologies and tools
├── 01-architecture.md    # System design and structure
├── 02-conventions.md     # Coding standards and practices
├── 03-setup.md          # Development environment setup
└── 04-apis.md           # API documentation
```

## Context Files

### 00-tech-stack.md

**Purpose**: Inventory of all technologies, frameworks, and tools used in the project.

**Used By**: All agents need to know what technologies are available.

**Contents**:
- Programming languages and versions
- Frontend frameworks and libraries
- Backend frameworks and tools
- Databases and caching
- Infrastructure and deployment
- Development tools
- Testing frameworks

### 01-architecture.md

**Purpose**: High-level system design, directory structure, and component organization.

**Used By**:
- Architect (for design decisions)
- All agents (to understand where code goes)

**Contents**:
- System architecture overview
- Directory structure and organization
- Key components and their responsibilities
- Data flow and integration points
- External services and APIs

### 02-conventions.md

**Purpose**: Coding standards, naming conventions, git workflow, and best practices.

**Used By**: All agents to maintain code consistency.

**Contents**:
- Code style and formatting
- Naming conventions
- Git workflow and branch naming
- Commit message format
- Pull request process
- Testing requirements
- Documentation standards

### 03-setup.md

**Purpose**: How to set up and run the development environment.

**Used By**:
- DevOps (for environment configuration)
- All agents (to understand dependencies)

**Contents**:
- Prerequisites and dependencies
- Installation steps
- Environment variables
- Database setup
- Running the application
- Running tests
- Common development commands

### 04-apis.md

**Purpose**: API documentation, endpoints, and contracts.

**Used By**:
- Backend (implementing APIs)
- Frontend (consuming APIs)
- QA (testing APIs)

**Contents**:
- Base URLs and authentication
- API endpoints and methods
- Request/response formats
- Error handling
- Rate limiting
- WebSocket endpoints (if applicable)
- GraphQL schema (if applicable)

## Setting Up Context

### Initial Setup

1. **Run Setup Script**:
   ```bash
   ./scripts/setup-orchestration.sh
   ```

2. **Edit Context Files**:
   ```bash
   cd .claude/agents/project-context

   # Edit each file with your project information
   nano 00-tech-stack.md
   nano 01-architecture.md
   nano 02-conventions.md
   nano 03-setup.md
   nano 04-apis.md
   ```

3. **Commit Context**:
   ```bash
   git add .claude/agents/project-context/
   git commit -m "docs: add project context for agent orchestration"
   ```

### Quick Start Template

If you're starting from scratch, use this abbreviated setup:

```bash
# Create minimal context
cat > .claude/agents/project-context/00-tech-stack.md << 'EOF'
# Tech Stack

## Frontend
- React 18 with TypeScript
- Tailwind CSS
- React Router

## Backend
- Node.js 18 with Express
- TypeScript
- PostgreSQL 14

## Testing
- Jest
- React Testing Library
- Supertest
EOF

cat > .claude/agents/project-context/01-architecture.md << 'EOF'
# Architecture

## Directory Structure
```
src/
├── client/          # React frontend
│   ├── components/
│   ├── pages/
│   └── utils/
├── server/          # Express backend
│   ├── routes/
│   ├── controllers/
│   └── models/
└── shared/          # Shared types
```
EOF

# Continue for other files...
```

## Context Templates

### Tech Stack Template

```markdown
# Tech Stack

## Frontend

### Framework
- **Framework**: [React/Vue/Angular/Svelte] version X
- **Language**: TypeScript X.X
- **Build Tool**: [Vite/Webpack/Parcel]

### UI Libraries
- **Component Library**: [Material-UI/Ant Design/Chakra UI/Custom]
- **Styling**: [Tailwind CSS/Styled Components/CSS Modules/SCSS]
- **Icons**: [React Icons/Font Awesome/Custom]

### State Management
- **Global State**: [Redux/Zustand/Context API/Jotai]
- **Server State**: [React Query/SWR/RTK Query]
- **Form State**: [React Hook Form/Formik]

### Routing
- **Router**: [React Router/Next.js routing/Vue Router]

## Backend

### Framework
- **Framework**: [Express/FastAPI/Django/NestJS/Rails] version X
- **Language**: [Node.js/Python/Ruby/Go/Rust] version X
- **Runtime**: [Node.js/Bun/Deno]

### Database
- **Primary DB**: [PostgreSQL/MySQL/MongoDB] version X
- **ORM/ODM**: [Prisma/TypeORM/Mongoose/SQLAlchemy]
- **Migrations**: [Prisma Migrate/TypeORM/Alembic]

### Caching
- **Cache**: [Redis/Memcached] version X
- **Use Cases**: Session storage, API caching

### Authentication
- **Strategy**: [JWT/Session/OAuth2/Passport]
- **Library**: [jsonwebtoken/passport/next-auth]

## DevOps

### Containerization
- **Runtime**: Docker version X
- **Orchestration**: [docker-compose/Kubernetes]

### CI/CD
- **Platform**: [GitHub Actions/GitLab CI/Jenkins/CircleCI]
- **Workflows**: Build, test, deploy

### Cloud Platform
- **Provider**: [AWS/GCP/Azure/Vercel/Netlify]
- **Services**: [List key services used]

### Monitoring
- **Application**: [Sentry/Datadog/New Relic]
- **Infrastructure**: [Prometheus/Grafana/CloudWatch]
- **Logs**: [ELK Stack/Loki/CloudWatch Logs]

## Testing

### Unit Testing
- **Framework**: [Jest/Vitest/pytest/RSpec]
- **Coverage Tool**: [Istanbul/coverage.py]

### Integration Testing
- **Framework**: [Supertest/pytest/RSpec]

### E2E Testing
- **Framework**: [Playwright/Cypress/Selenium]

## Development Tools

### Package Manager
- **Manager**: [npm/yarn/pnpm/pip/cargo]

### Code Quality
- **Linter**: [ESLint/pylint/rubocop]
- **Formatter**: [Prettier/Black/RuboCop]
- **Type Checker**: [TypeScript/mypy]

### Git Hooks
- **Tool**: [Husky/pre-commit]
- **Hooks**: pre-commit, pre-push

## Additional Tools
- [List any other relevant tools]
```

### Architecture Template

```markdown
# Architecture

## System Overview

[High-level description of your system]

### Architecture Pattern
- **Pattern**: [Monolith/Microservices/Serverless/Jamstack]
- **Communication**: [REST/GraphQL/gRPC/WebSocket]

## Directory Structure

```
project-root/
├── src/
│   ├── client/              # Frontend application
│   │   ├── components/      # React components
│   │   │   ├── common/      # Shared components
│   │   │   └── features/    # Feature-specific components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── utils/          # Utility functions
│   │   ├── types/          # TypeScript types
│   │   └── api/            # API client
│   ├── server/             # Backend application
│   │   ├── routes/         # API routes
│   │   ├── controllers/    # Route handlers
│   │   ├── services/       # Business logic
│   │   ├── models/         # Database models
│   │   ├── middleware/     # Express middleware
│   │   └── utils/          # Server utilities
│   └── shared/             # Shared between client/server
│       └── types/          # Shared TypeScript types
├── tests/                  # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                   # Documentation
├── scripts/                # Build and deployment scripts
└── infrastructure/         # IaC files (Terraform, etc.)
```

## Component Organization

### Frontend Components

**Structure**:
```
components/
├── common/                 # Shared across features
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   └── Button.module.css
│   └── Input/
└── features/               # Feature-specific
    ├── auth/
    │   ├── LoginForm/
    │   └── SignupForm/
    └── dashboard/
```

**Principles**:
- One component per directory
- Colocate tests and styles
- Export from index files

### Backend Services

**Structure**:
```
services/
├── auth.service.ts         # Authentication logic
├── user.service.ts         # User management
├── post.service.ts         # Post management
└── email.service.ts        # Email sending
```

**Principles**:
- One service per domain entity
- Services contain business logic
- Controllers are thin, services are fat

## Data Flow

### Frontend → Backend

1. User interacts with UI component
2. Component calls API client function
3. API client sends HTTP request
4. Backend route receives request
5. Controller validates and calls service
6. Service executes business logic
7. Response sent back through chain

### Backend → Database

1. Service calls model/repository
2. ORM generates SQL query
3. Database executes query
4. Results mapped to domain objects
5. Returned to service

## External Integrations

### Third-Party Services
- **Service 1**: [Purpose] - [Integration method]
- **Service 2**: [Purpose] - [Integration method]

### APIs Consumed
- **API 1**: [Purpose] - [Authentication method]
- **API 2**: [Purpose] - [Authentication method]

## Security Architecture

### Authentication Flow
[Describe your auth flow]

### Authorization
- **Strategy**: [RBAC/ABAC/Claims-based]
- **Implementation**: [How it's enforced]

### Data Protection
- **At Rest**: [Encryption method]
- **In Transit**: HTTPS/TLS
- **Secrets**: [How secrets are managed]

## Performance Considerations

### Caching Strategy
- **Frontend**: Service workers, local storage
- **Backend**: Redis caching layer
- **Database**: Query result caching

### Optimization
- Code splitting
- Lazy loading
- Database indexing
- CDN for static assets

## Scalability

### Horizontal Scaling
[How the system scales horizontally]

### Vertical Scaling
[Limits and considerations]

### Bottlenecks
[Known bottlenecks and mitigation strategies]
```

### Conventions Template

```markdown
# Coding Conventions

## Code Style

### General Principles
- Write clear, self-documenting code
- Follow SOLID principles
- Keep functions small and focused
- Prefer composition over inheritance

### Formatting
- **Indentation**: 2 spaces (JavaScript/TypeScript), 4 spaces (Python)
- **Line Length**: Max 100 characters
- **Quotes**: Single quotes for JavaScript, double for Python
- **Semicolons**: Required in JavaScript/TypeScript
- **Trailing Commas**: Required in multi-line arrays/objects

### Tool Configuration
- **ESLint**: Use `.eslintrc.json` config
- **Prettier**: Use `.prettierrc` config
- **EditorConfig**: Use `.editorconfig`

## Naming Conventions

### Variables and Functions
- **JavaScript/TypeScript**: `camelCase`
  ```typescript
  const userName = "John";
  function getUserById(id: string) { }
  ```
- **Python**: `snake_case`
  ```python
  user_name = "John"
  def get_user_by_id(id: str):
  ```

### Classes and Types
- **PascalCase** for all languages
  ```typescript
  class UserService { }
  interface UserProfile { }
  type UserId = string;
  ```

### Constants
- **UPPER_SNAKE_CASE**
  ```typescript
  const MAX_RETRY_ATTEMPTS = 3;
  const API_BASE_URL = "https://api.example.com";
  ```

### Files and Directories
- **Components**: `PascalCase.tsx` (e.g., `UserProfile.tsx`)
- **Utilities**: `camelCase.ts` (e.g., `formatDate.ts`)
- **Tests**: `*.test.ts` or `*.spec.ts`
- **Directories**: `kebab-case` (e.g., `user-profile/`)

## TypeScript Guidelines

### Type Annotations
- Always annotate function parameters and return types
- Use interfaces for object shapes
- Use type aliases for unions/intersections
- Avoid `any`, use `unknown` when type is truly unknown

```typescript
// Good
function getUserById(id: string): Promise<User> {
  return api.get(`/users/${id}`);
}

interface User {
  id: string;
  name: string;
  email: string;
}

// Bad
function getUserById(id) {
  return api.get(`/users/${id}`);
}
```

### Generics
Use generics for reusable components and functions:
```typescript
function identity<T>(value: T): T {
  return value;
}
```

## React Guidelines

### Component Structure
```typescript
// 1. Imports
import React, { useState, useEffect } from 'react';
import { User } from '@/types';

// 2. Types/Interfaces
interface UserProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
}

// 3. Component
export function UserProfile({ userId, onUpdate }: UserProfileProps) {
  // 3a. Hooks
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser();
  }, [userId]);

  // 3b. Functions
  const fetchUser = async () => {
    // Implementation
  };

  // 3c. Render
  if (loading) return <LoadingSpinner />;
  if (!user) return <ErrorMessage />;

  return (
    <div>
      {/* JSX */}
    </div>
  );
}
```

### Hooks
- Use custom hooks for reusable logic
- Prefix custom hooks with `use` (e.g., `useAuth`, `useFetch`)
- Keep hooks focused on single responsibility

### Props
- Use destructuring in function parameters
- Provide default values when appropriate
- Document complex props with JSDoc comments

## Git Workflow

### Branch Naming
- **Feature**: `feature/short-description` (e.g., `feature/user-auth`)
- **Bugfix**: `fix/short-description` (e.g., `fix/login-error`)
- **Hotfix**: `hotfix/short-description`
- **Chore**: `chore/short-description` (e.g., `chore/update-deps`)

### Commit Messages
Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(auth): add OAuth2 login support

Implement OAuth2 authentication flow with Google and GitHub providers.
Includes login button, callback handling, and session management.

Closes #123
```

```
fix(api): handle null response in user endpoint

Add null check before accessing user properties to prevent crashes
when user is not found.
```

### Pull Requests

1. **Title**: Same format as commit messages
2. **Description**: Include:
   - What changed and why
   - How to test
   - Screenshots (for UI changes)
   - Related issues/PRs
3. **Reviews**: Require at least 1 approval
4. **CI**: All checks must pass
5. **Conflicts**: Resolve before merging

## Testing Requirements

### Coverage
- **Minimum**: 80% code coverage
- **Critical Paths**: 100% coverage for auth, payments, data integrity

### Unit Tests
- Test each function/component in isolation
- Mock external dependencies
- Use descriptive test names

```typescript
describe('formatDate', () => {
  it('should format date as YYYY-MM-DD', () => {
    const date = new Date('2026-01-11');
    expect(formatDate(date)).toBe('2026-01-11');
  });

  it('should handle invalid dates', () => {
    expect(formatDate(new Date('invalid'))).toBe('Invalid Date');
  });
});
```

### Integration Tests
- Test feature workflows end-to-end
- Use real database (or test database)
- Clean up test data after each test

### E2E Tests
- Test critical user journeys
- Run against staging environment
- Include happy path and error scenarios

## Documentation Standards

### Code Comments
- Use JSDoc for public APIs
- Explain *why*, not *what*
- Keep comments up-to-date

```typescript
/**
 * Calculates the total price including tax and shipping.
 *
 * @param items - Array of cart items
 * @param shippingMethod - Selected shipping method
 * @returns Total price in cents
 */
function calculateTotal(items: CartItem[], shippingMethod: ShippingMethod): number {
  // Implementation
}
```

### README Files
- Every major directory should have a README
- Explain purpose and usage
- Include examples

### API Documentation
- Use OpenAPI/Swagger for REST APIs
- Document all endpoints, parameters, responses
- Include example requests/responses

## Error Handling

### Frontend
```typescript
try {
  const user = await fetchUser(id);
  setUser(user);
} catch (error) {
  if (error instanceof ApiError) {
    showToast(error.message, 'error');
  } else {
    showToast('An unexpected error occurred', 'error');
    logger.error('Failed to fetch user:', error);
  }
}
```

### Backend
```typescript
app.use((err, req, res, next) => {
  logger.error(err.stack);

  if (err instanceof ValidationError) {
    return res.status(400).json({ error: err.message });
  }

  if (err instanceof UnauthorizedError) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  res.status(500).json({ error: 'Internal server error' });
});
```

## Security Guidelines

### Input Validation
- Validate all user input
- Sanitize before storing in database
- Use validation libraries (Zod, Joi, etc.)

### Authentication
- Use secure password hashing (bcrypt, argon2)
- Implement rate limiting on auth endpoints
- Use HTTPS only in production

### Data Access
- Follow principle of least privilege
- Validate user permissions before data access
- Log security-relevant events

## Performance Guidelines

### Frontend
- Lazy load routes and components
- Optimize images (WebP, lazy loading)
- Minimize bundle size
- Use React.memo for expensive components

### Backend
- Use database indexes appropriately
- Implement caching for frequently accessed data
- Optimize N+1 queries
- Use connection pooling

### Database
- Index foreign keys
- Avoid SELECT *
- Use appropriate data types
- Regular vacuum/analyze (PostgreSQL)
```

## Maintaining Context

### When to Update

Update context when:
1. **Tech stack changes** (new library, framework upgrade)
2. **Architecture evolves** (new services, refactoring)
3. **Conventions change** (new code standards adopted)
4. **New APIs added** (new endpoints, services)
5. **Setup process changes** (new dependencies, environment variables)

### Update Process

1. **Identify Change**:
   ```bash
   # Example: Added new frontend library
   npm install react-query
   ```

2. **Update Context**:
   ```bash
   nano .claude/agents/project-context/00-tech-stack.md
   # Add: - **Server State**: React Query
   ```

3. **Commit Update**:
   ```bash
   git add .claude/agents/project-context/00-tech-stack.md
   git commit -m "docs: update tech stack with React Query"
   ```

4. **Notify Active Agents** (if orchestration running):
   ```python
   # Agents will see updated context on next task
   ```

### Version Control

Keep context in git:
```bash
# Context is part of repository
git add .claude/agents/project-context/
git commit -m "docs: update project context"
git push
```

Benefits:
- Track context changes over time
- Share context with team
- Restore previous context if needed

## Best Practices

### 1. Start Simple

Begin with minimal context:
```markdown
# Tech Stack (Minimal)
- React + TypeScript
- Express + PostgreSQL
- Jest for testing
```

Expand as needed.

### 2. Keep It Current

Outdated context is worse than no context:
- Review quarterly
- Update immediately after major changes
- Remove deprecated information

### 3. Be Specific

```markdown
# Bad
- Database: SQL

# Good
- Database: PostgreSQL 14.5
- Connection pooling: pg-pool (max 20 connections)
- Migrations: Prisma Migrate
```

### 4. Include Examples

```markdown
# API Authentication

All API requests require JWT token in header:

```
Authorization: Bearer <token>
```

Example:
```typescript
const response = await fetch('/api/users', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```
```

### 5. Link to External Docs

```markdown
# Frontend Framework
- React 18 - [Official Docs](https://react.dev)
- TypeScript 5 - [Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
```

### 6. Organize by Role Needs

Think about which roles need which information:
- **All roles**: Tech stack, architecture overview
- **Frontend/Backend**: Detailed architecture, conventions
- **DevOps**: Setup instructions, deployment process
- **QA**: Testing requirements, coverage standards

## Examples

### Example: Web Application

See complete example in:
- [examples/webapp-context/](../examples/webapp-context/)

### Example: Mobile App

See complete example in:
- [examples/mobile-context/](../examples/mobile-context/)

### Example: Microservices

See complete example in:
- [examples/microservices-context/](../examples/microservices-context/)

## Troubleshooting

### Agents Making Wrong Technology Choices

**Problem**: Agent suggests using library X, but project uses library Y.

**Solution**: Update `00-tech-stack.md` to explicitly list all libraries:
```markdown
## State Management
- **Global State**: Zustand (NOT Redux)
- **Server State**: React Query (NOT SWR)
```

### Agents Not Following Code Style

**Problem**: Agent code doesn't match project style.

**Solution**: Update `02-conventions.md` with explicit examples:
```markdown
## Function Style
✅ Use arrow functions for components:
```typescript
export const UserProfile = ({ id }: Props) => {
  // ...
};
```

❌ Don't use function declarations:
```typescript
export function UserProfile({ id }: Props) {
  // ...
}
```
```

### Agents Don't Know Where to Put Files

**Problem**: Agent creates files in wrong directories.

**Solution**: Update `01-architecture.md` with clear directory structure and rules:
```markdown
## File Placement Rules
- New React components → `src/client/components/features/<feature-name>/`
- API routes → `src/server/routes/<resource>.routes.ts`
- Tests → `tests/<type>/<matching-path>/<file>.test.ts`
```

## Further Reading

- [README-ORCHESTRATION.md](README-ORCHESTRATION.md) - Main orchestration guide
- [AGENT-ROLES.md](AGENT-ROLES.md) - Understanding agent roles
- [WORKFLOW-GUIDE.md](WORKFLOW-GUIDE.md) - Advanced workflow patterns
- [API-REFERENCE.md](API-REFERENCE.md) - Complete API documentation
