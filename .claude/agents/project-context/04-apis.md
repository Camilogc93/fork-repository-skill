# API Documentation

> **Note**: This is a template file. Customize it with your project's actual API design and endpoints.
> Delete this note after filling out.

## API Overview

**Base URL**: `http://localhost:8000/api/v1` (development)
**Production URL**: `https://api.example.com/api/v1`

**API Style**: RESTful
**Data Format**: JSON
**Authentication**: JWT Bearer Token

---

## API Conventions

### Versioning
- **Method**: URL path versioning
- **Format**: `/api/v1/`, `/api/v2/`
- **Current Version**: v1

### HTTP Methods
- `GET` - Retrieve resource(s)
- `POST` - Create new resource
- `PUT` - Update entire resource
- `PATCH` - Partially update resource
- `DELETE` - Delete resource

### Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE with no response body |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Server maintenance |

### Response Format

#### Success Response
```json
{
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

#### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

#### Paginated Response
```json
{
  "data": [
    { "id": 1, "name": "Item 1" },
    { "id": 2, "name": "Item 2" }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

---

## Authentication

### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-01-11T10:00:00Z"
  }
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "is_admin": false,
    "created_at": "2026-01-11T10:00:00Z"
  }
}
```

### Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

**Response** (204 No Content)

---

## Users

### List Users
```http
GET /api/v1/users?page=1&limit=20&search=john
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `page` (integer, optional, default: 1) - Page number
- `limit` (integer, optional, default: 20, max: 100) - Items per page
- `search` (string, optional) - Search by name or email
- `sort` (string, optional, default: created_at) - Sort field
- `order` (string, optional, default: desc) - Sort order (asc/desc)

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "email": "user1@example.com",
      "name": "User One",
      "is_active": true,
      "created_at": "2026-01-11T10:00:00Z"
    },
    {
      "id": 2,
      "email": "user2@example.com",
      "name": "User Two",
      "is_active": true,
      "created_at": "2026-01-10T15:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 42,
    "pages": 3
  }
}
```

### Get User by ID
```http
GET /api/v1/users/{id}
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": true,
    "is_admin": false,
    "created_at": "2026-01-11T10:00:00Z",
    "updated_at": "2026-01-11T10:00:00Z"
  }
}
```

**Error Response** (404 Not Found):
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found"
  }
}
```

### Create User (Admin Only)
```http
POST /api/v1/users
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "name": "New User",
  "is_admin": false
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": 3,
    "email": "newuser@example.com",
    "name": "New User",
    "is_active": true,
    "is_admin": false,
    "created_at": "2026-01-11T12:00:00Z"
  }
}
```

### Update User
```http
PUT /api/v1/users/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "email": "updated@example.com"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "id": 1,
    "email": "updated@example.com",
    "name": "Updated Name",
    "is_active": true,
    "updated_at": "2026-01-11T13:00:00Z"
  }
}
```

### Delete User (Admin Only)
```http
DELETE /api/v1/users/{id}
Authorization: Bearer <access_token>
```

**Response** (204 No Content)

---

## [Add Other Resource Endpoints]

### Example: Posts

#### List Posts
```http
GET /api/v1/posts?page=1&limit=20
```

#### Get Post
```http
GET /api/v1/posts/{id}
```

#### Create Post
```http
POST /api/v1/posts
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Post Title",
  "content": "Post content here...",
  "published": true
}
```

#### Update Post
```http
PUT /api/v1/posts/{id}
Authorization: Bearer <access_token>
```

#### Delete Post
```http
DELETE /api/v1/posts/{id}
Authorization: Bearer <access_token>
```

---

## Authentication & Authorization

### Authentication Methods

#### Bearer Token (Primary)
```http
Authorization: Bearer <access_token>
```

#### API Key (Optional)
```http
X-API-Key: <api_key>
```

### Token Lifecycle
- **Access Token**: Valid for 15 minutes
- **Refresh Token**: Valid for 7 days
- **Token Renewal**: Use refresh endpoint before access token expires

### Protected Routes
All endpoints except the following require authentication:
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/health` (health check)

### Role-Based Access
- **Admin**: Full access to all endpoints
- **User**: Access to own resources and public data
- **Guest**: Read-only access to public data (if applicable)

---

## Rate Limiting

### Limits
- **Authenticated Users**: 1000 requests per hour
- **Unauthenticated**: 100 requests per hour
- **Specific Endpoints**: May have stricter limits

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641900000
```

### Rate Limit Exceeded Response (429)
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retry_after": 3600
  }
}
```

---

## Pagination

### Query Parameters
- `page` (integer, default: 1) - Page number (1-indexed)
- `limit` (integer, default: 20, max: 100) - Items per page

### Response Format
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false,
    "next_page": 2,
    "prev_page": null
  }
}
```

---

## Filtering & Sorting

### Filtering
```http
GET /api/v1/users?is_active=true&role=admin
GET /api/v1/posts?published=true&author_id=5
```

### Searching
```http
GET /api/v1/users?search=john
GET /api/v1/posts?q=javascript
```

### Sorting
```http
GET /api/v1/users?sort=created_at&order=desc
GET /api/v1/posts?sort=title&order=asc
```

### Combined Example
```http
GET /api/v1/posts?published=true&sort=created_at&order=desc&page=1&limit=10
```

---

## Error Handling

### Validation Errors (422)
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "value": "not-an-email"
      },
      {
        "field": "password",
        "message": "Password must be at least 8 characters",
        "value": null
      }
    ]
  }
}
```

### Authorization Errors (403)
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to perform this action"
  }
}
```

### Not Found Errors (404)
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "resource": "User",
    "id": 999
  }
}
```

### Server Errors (500)
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred",
    "request_id": "abc123"
  }
}
```

---

## File Uploads

### Upload File
```http
POST /api/v1/uploads
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <binary data>
```

**Response** (201 Created):
```json
{
  "data": {
    "id": "abc123",
    "filename": "document.pdf",
    "size": 1024000,
    "mime_type": "application/pdf",
    "url": "https://cdn.example.com/uploads/abc123.pdf",
    "uploaded_at": "2026-01-11T14:00:00Z"
  }
}
```

### File Size Limits
- **Maximum file size**: 10 MB
- **Allowed types**: images (jpg, png, webp), documents (pdf)

---

## Webhooks (if applicable)

### Webhook Events
- `user.created` - New user registered
- `user.updated` - User profile updated
- `post.created` - New post created
- `post.published` - Post published

### Webhook Payload Format
```json
{
  "event": "user.created",
  "timestamp": "2026-01-11T10:00:00Z",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Webhook Signature
Webhooks are signed with HMAC-SHA256. Verify signature:
```python
import hmac
import hashlib

signature = request.headers.get('X-Webhook-Signature')
expected = hmac.new(
    WEBHOOK_SECRET.encode(),
    request.body,
    hashlib.sha256
).hexdigest()

if not hmac.compare_digest(signature, expected):
    raise InvalidSignature()
```

---

## API Clients

### JavaScript/TypeScript
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Example usage
const getUsers = async () => {
  const response = await apiClient.get('/users');
  return response.data;
};
```

### Python
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

class APIClient:
    def __init__(self, access_token=None):
        self.base_url = BASE_URL
        self.access_token = access_token

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def get_users(self, page=1, limit=20):
        response = requests.get(
            f"{self.base_url}/users",
            headers=self._headers(),
            params={"page": page, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

# Example usage
client = APIClient(access_token="your-token")
users = client.get_users()
```

### cURL Examples
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Get users (with auth)
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <access_token>"

# Create user
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"email":"new@example.com","password":"pass123","name":"New User"}'
```

---

## API Versioning Strategy

### Current: v1
- Stable, production-ready
- No breaking changes

### Deprecation Policy
- Breaking changes require new version
- Old versions supported for 6 months
- Deprecation warnings in response headers:
  ```http
  X-API-Deprecation: true
  X-API-Deprecation-Date: 2026-07-01
  X-API-Sunset: 2026-12-31
  ```

---

## Interactive API Documentation

### Swagger/OpenAPI UI
- **URL**: http://localhost:8000/docs
- Interactive API explorer
- Try out endpoints directly
- View request/response schemas

### ReDoc
- **URL**: http://localhost:8000/redoc
- Clean, readable API documentation
- Search functionality
- Export to PDF

### Postman Collection
- Download: [Link to Postman collection]
- Import into Postman for easy testing

---

## Best Practices for API Consumers

### 1. Use HTTPS in Production
Always use HTTPS endpoints in production to ensure data security.

### 2. Handle Rate Limits
Respect rate limits and implement exponential backoff for retries.

### 3. Refresh Tokens Proactively
Refresh access tokens before they expire to avoid 401 errors.

### 4. Implement Proper Error Handling
Don't assume requests will succeed. Handle all possible HTTP status codes.

### 5. Use Pagination
Don't fetch all data at once. Use pagination for large datasets.

### 6. Cache Responses
Cache GET responses where appropriate to reduce API calls.

### 7. Include Request IDs
Include unique request IDs for easier debugging:
```http
X-Request-ID: abc-123-def-456
```

### 8. Monitor API Usage
Track your API usage to stay within rate limits and identify issues.

---

## Changelog

### v1.1.0 (Upcoming)
- [ ] Add bulk operations endpoints
- [ ] Implement GraphQL endpoint
- [ ] Add WebSocket support for real-time updates

### v1.0.0 (Current)
- Initial stable release
- User authentication and management
- CRUD operations for main resources
- Rate limiting and pagination

---

## Support & Resources

- **API Status**: https://status.example.com
- **Developer Portal**: https://developers.example.com
- **Support Email**: api-support@example.com
- **Community Forum**: https://community.example.com
- **GitHub Issues**: [Link to issues]

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| [Date] | Initial API documentation | [Name] |
