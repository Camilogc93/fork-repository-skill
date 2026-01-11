# Project Conventions and Standards

> **Note**: This is a template file. Customize it with your project's actual conventions.
> Delete this note after filling out.

## General Principles

- **Keep it simple**: Favor clarity over cleverness
- **Be consistent**: Follow established patterns
- **DRY (Don't Repeat Yourself)**: Extract reusable logic
- **YAGNI (You Aren't Gonna Need It)**: Don't build for hypothetical future
- **Test your code**: Write tests for new features and bug fixes
- **Document when necessary**: Code should be self-explanatory, document the "why"

---

## Code Style

### Frontend (TypeScript/React)

#### Naming Conventions
```typescript
// Components: PascalCase
const UserProfile = () => { ... }
const NavigationBar = () => { ... }

// Functions and variables: camelCase
const getUserData = () => { ... }
const userEmail = "user@example.com";

// Constants: UPPER_SNAKE_CASE
const MAX_RETRIES = 3;
const API_BASE_URL = "https://api.example.com";

// Types and Interfaces: PascalCase
interface User {
  id: number;
  name: string;
}

type UserRole = "admin" | "user" | "guest";

// Private variables/functions: prefix with underscore (optional)
const _internalHelper = () => { ... }
```

#### File Naming
```
Components: PascalCase
  - UserProfile.tsx
  - NavigationBar.tsx

Utilities: camelCase
  - formatDate.ts
  - apiClient.ts

Tests: Same as source + .test or .spec
  - UserProfile.test.tsx
  - formatDate.test.ts

Styles: Same as component + .module.css
  - UserProfile.module.css
```

#### Component Structure
```typescript
// Imports - group by category
import { FC, useState, useEffect } from 'react';  // React imports
import { useNavigate } from 'react-router-dom';    // Third-party hooks
import { Button } from '@/components/common';      // Internal components
import { useAuth } from '@/hooks/useAuth';         // Internal hooks
import { User } from '@/types';                    // Types
import styles from './UserProfile.module.css';     // Styles

// Types/Interfaces
interface UserProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
}

// Component
export const UserProfile: FC<UserProfileProps> = ({ userId, onUpdate }) => {
  // Hooks first
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [isEditing, setIsEditing] = useState(false);

  // Effects
  useEffect(() => {
    // Effect logic
  }, [userId]);

  // Event handlers
  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = async () => {
    // Save logic
  };

  // Early returns
  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  // Main render
  return (
    <div className={styles.container}>
      {/* Component JSX */}
    </div>
  );
};
```

#### TypeScript Best Practices
```typescript
// ✅ Good: Explicit types for function parameters and return
function getUser(id: string): Promise<User | null> {
  return api.get(`/users/${id}`);
}

// ✅ Good: Type inference for simple cases
const userName = "John Doe";  // Type inferred as string
const userAge = 30;            // Type inferred as number

// ❌ Avoid: Using 'any'
function processData(data: any) { ... }  // Avoid 'any'

// ✅ Good: Use proper types or 'unknown'
function processData(data: unknown) { ... }

// ✅ Good: Use utility types
type PartialUser = Partial<User>;
type ReadonlyUser = Readonly<User>;
type UserWithoutPassword = Omit<User, 'password'>;
```

---

### Backend (Python)

#### Naming Conventions
```python
# Classes: PascalCase
class UserService:
    pass

class DatabaseConnection:
    pass

# Functions and variables: snake_case
def get_user_by_id(user_id: int):
    pass

user_email = "user@example.com"

# Constants: UPPER_SNAKE_CASE
MAX_PAGE_SIZE = 100
API_VERSION = "v1"

# Private methods/variables: prefix with underscore
def _internal_helper():
    pass

_cache = {}
```

#### File Naming
```
All files: snake_case
  - user_service.py
  - database.py
  - test_user_service.py
```

#### Function Structure
```python
from typing import Optional
from app.models import User
from app.schemas import UserCreate

async def create_user(
    user_data: UserCreate,
    db: Session
) -> User:
    """
    Create a new user.

    Args:
        user_data: User creation data
        db: Database session

    Returns:
        Created user object

    Raises:
        ValueError: If email already exists
    """
    # Validation
    if await _email_exists(user_data.email, db):
        raise ValueError("Email already registered")

    # Business logic
    hashed_password = hash_password(user_data.password)

    # Database operation
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user
```

#### Type Hints
```python
# ✅ Good: Use type hints for function signatures
def get_user(user_id: int) -> Optional[User]:
    ...

async def create_user(data: UserCreate) -> User:
    ...

# ✅ Good: Type hints for variables when not obvious
users: list[User] = []
user_dict: dict[str, any] = {}

# ✅ Good: Use Optional for nullable values
def find_user(email: str) -> Optional[User]:
    ...
```

---

## Git Workflow

### Branch Naming
```
main              - Production-ready code
develop           - Integration branch (if using git-flow)

Feature branches:
feature/user-authentication
feature/dashboard-redesign

Bug fixes:
fix/login-error
fix/memory-leak-in-cache

Hotfixes:
hotfix/critical-security-patch

Chores/refactoring:
chore/update-dependencies
refactor/simplify-auth-logic

Documentation:
docs/api-documentation
docs/setup-guide
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, missing semicolons, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build config)
- `ci`: CI/CD changes

**Examples:**
```bash
feat(auth): add password reset functionality

Implement password reset flow with email verification.
Users can now request a password reset link that expires
after 1 hour.

Closes #123

---

fix(api): handle null user in getUserProfile

Check if user exists before accessing properties to prevent
TypeError when user is null.

---

docs(readme): update installation instructions

Add Docker setup instructions and clarify Node version
requirement.

---

refactor(components): simplify Button component API

Remove unused props and consolidate size variants.
BREAKING CHANGE: 'large' and 'small' props replaced with
'size' prop accepting 'sm', 'md', 'lg'.
```

### Pull Request Guidelines

#### PR Title
Use same format as commit messages:
```
feat(auth): add OAuth2 authentication
fix(api): resolve race condition in user creation
```

#### PR Description Template
```markdown
## Description
Brief description of what this PR does and why.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows project conventions
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No console warnings or errors
- [ ] Tests passing

## Related Issues
Closes #123
Related to #456
```

---

## Testing Standards

### Test Organization

#### Frontend Tests
```
tests/
├── unit/                   # Unit tests for functions/hooks
│   ├── utils/
│   └── hooks/
├── integration/            # Integration tests for components
│   ├── components/
│   └── pages/
└── e2e/                   # End-to-end tests
    ├── auth.spec.ts
    └── dashboard.spec.ts
```

#### Backend Tests
```
tests/
├── unit/                   # Unit tests for services/utils
│   ├── services/
│   └── utils/
├── integration/            # Integration tests for API
│   ├── test_auth_api.py
│   └── test_users_api.py
└── conftest.py            # Pytest fixtures
```

### Test Naming
```typescript
// ✅ Good: Descriptive test names
describe('UserProfile', () => {
  it('renders user name and email', () => { ... });
  it('calls onEdit when edit button is clicked', () => { ... });
  it('shows loading state while fetching user data', () => { ... });
});

// ❌ Avoid: Vague test names
it('works', () => { ... });
it('test 1', () => { ... });
```

### Test Structure (AAA Pattern)
```typescript
it('creates a new user successfully', async () => {
  // Arrange
  const userData = {
    email: 'test@example.com',
    password: 'password123',
    name: 'Test User'
  };

  // Act
  const response = await api.post('/users', userData);

  // Assert
  expect(response.status).toBe(201);
  expect(response.data.email).toBe(userData.email);
  expect(response.data.password).toBeUndefined();
});
```

### Coverage Requirements
- **Minimum coverage**: 80%
- **Critical paths**: 100% (auth, payments, etc.)
- **Utility functions**: 100%
- **UI components**: 80%+ (focus on logic, not just rendering)

---

## Code Review Guidelines

### For Authors
- [ ] Self-review your changes before requesting review
- [ ] Write clear PR description
- [ ] Keep PRs focused and reasonably sized (<500 lines)
- [ ] Add tests for new functionality
- [ ] Update documentation if needed
- [ ] Respond to feedback constructively

### For Reviewers
- [ ] Review code logic and design
- [ ] Check for security issues
- [ ] Verify tests are adequate
- [ ] Check for code style consistency
- [ ] Look for performance issues
- [ ] Suggest improvements, don't demand perfection
- [ ] Approve when ready, request changes if needed

### Review Feedback Style
```
✅ Good: Constructive and specific
"Consider using `Promise.all()` here to run these API calls in parallel
for better performance. Current approach makes them sequential."

❌ Avoid: Vague or demanding
"This is slow."
"You must use Promise.all here."
```

---

## Error Handling

### Frontend
```typescript
// ✅ Good: Specific error handling
try {
  const user = await api.getUser(userId);
  setUser(user);
} catch (error) {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 404) {
      setError('User not found');
    } else if (error.response?.status === 401) {
      navigate('/login');
    } else {
      setError('Failed to load user. Please try again.');
    }
  } else {
    setError('An unexpected error occurred');
  }
}

// ❌ Avoid: Generic catch-all
try {
  const user = await api.getUser(userId);
} catch (error) {
  console.error(error);  // Don't just log and ignore
}
```

### Backend
```python
# ✅ Good: Specific exceptions with proper HTTP status
from fastapi import HTTPException, status

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user

# ✅ Good: Custom exceptions for business logic
class InsufficientFundsError(Exception):
    pass

try:
    process_payment(amount)
except InsufficientFundsError:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Insufficient funds"
    )
```

---

## Security Best Practices

### Input Validation
- **Always validate user input** on both frontend and backend
- **Use schema validation** (Pydantic, Zod, Joi)
- **Sanitize HTML** if displaying user-generated content
- **Validate file uploads** (type, size, content)

### Authentication & Authorization
```typescript
// ✅ Frontend: Check auth on protected routes
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" />;

  return children;
};
```

```python
# ✅ Backend: Require authentication
from app.dependencies import get_current_user

@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

# ✅ Backend: Require specific role
from app.dependencies import require_admin

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin)
):
    ...
```

### Secrets Management
```python
# ✅ Good: Use environment variables
import os
SECRET_KEY = os.getenv("SECRET_KEY")

# ❌ Never: Hardcode secrets
SECRET_KEY = "my-secret-key-123"  # NEVER DO THIS
```

---

## Performance Guidelines

### Database Queries
```python
# ✅ Good: Eager loading to prevent N+1 queries
users = await db.query(User).options(
    selectinload(User.posts)
).all()

# ❌ Avoid: N+1 queries
users = await db.query(User).all()
for user in users:
    posts = await user.posts  # Separate query for each user!
```

### API Response Size
- **Paginate large lists**: Default page size: 20-50 items
- **Field selection**: Allow clients to specify which fields they need
- **Compression**: Enable gzip compression for API responses

### Frontend Performance
- **Code splitting**: Split bundles by route
- **Lazy loading**: Load components/images on demand
- **Memoization**: Use `useMemo` and `useCallback` appropriately
- **List virtualization**: For long lists (>100 items)

---

## Documentation Standards

### Code Comments
```typescript
// ✅ Good: Explain "why", not "what"
// Use exponential backoff to avoid overwhelming the API during retries
const delay = Math.pow(2, attempt) * 1000;

// ❌ Avoid: Stating the obvious
// Set delay to 2 to the power of attempt times 1000
const delay = Math.pow(2, attempt) * 1000;
```

### Function Documentation
```python
# ✅ Good: Clear docstring with examples
def calculate_discount(
    price: Decimal,
    discount_percent: int
) -> Decimal:
    """
    Calculate discounted price.

    Args:
        price: Original price
        discount_percent: Discount percentage (0-100)

    Returns:
        Discounted price

    Raises:
        ValueError: If discount_percent is not between 0 and 100

    Example:
        >>> calculate_discount(Decimal('100.00'), 20)
        Decimal('80.00')
    """
    ...
```

---

## Linting and Formatting

### Frontend
```json
// .eslintrc.json
{
  "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  "rules": {
    "no-console": "warn",
    "@typescript-eslint/no-unused-vars": "error"
  }
}

// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

### Backend
```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.flake8]
max-line-length = 100
extend-ignore = E203, W503
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
```

---

## Notes

- **Update this document** when adopting new conventions
- **Consistency is key** - it's better to be consistently suboptimal than inconsistently perfect
- **Automate what you can** - use linters, formatters, and pre-commit hooks
- **Be pragmatic** - rules are guidelines, not laws. Use judgment.

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| [Date] | Initial conventions documentation | [Name] |

