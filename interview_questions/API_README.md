In order to design an API, we need answers of below questions-
1. What is the purpose of the API? (e.g., user management, product catalog, payment gateway, etc.)
2. Who are the consumers? (e.g., internal devs, public users, third-party clients)
3. Preferred architecture style? (e.g., REST, GraphQL, gRPC)
4. Do you need authentication/authorization? 
5. Any specific technologies/frameworks in mind? (e.g., Flask, FastAPI, Spring Boot)

## Choosing right API architecture style (REST, GraphQL, gRPC, etc.)

### REST (Representational State Transfer)
Best when:
- You want a simple, widely adopted standard. 
- The API will be consumed by many clients (mobile, web, 3rd-party, etc.). 
- You’re dealing with resource-based CRUD operations (Create, Read, Update, Delete).

Pros:
- Easy to cache, debug, and document (Swagger/OpenAPI).
- Language-agnostic; works well over HTTP. 
- Supported everywhere.

Cons:
- Over-fetching or under-fetching data is common. 
- Rigid endpoint structure (requires versioning for changes).

Example:
```bash
GET /users/123
POST /orders
PUT /products/456
```

### GraphQL
Best when:
- The client needs precise control over the data it fetches (avoid over-fetching). 
- The schema is relational or nested (e.g., user → posts → comments). 
- You want a single endpoint API that evolves over time.

Pros:
- Flexible queries: clients ask for exactly what they need. 
- Reduces number of network calls. 
- Strong type system and introspection.

Cons:
- Steeper learning curve. 
- Harder to cache. 
- Overkill for simple APIs or non-nested data. 
- More complex for rate limiting and monitoring.

Example:
```graphql
{
  user(id: "123") {
    name
    posts {
      title
      comments {
        text
      }
    }
  }
}

```


### gRPC (Google Remote Procedure Call)
Best when:
- You need high performance and low latency. 
- It’s a service-to-service (internal microservices) communication scenario.
- ou want strong typing and backward compatibility.

Pros:
- Extremely fast (uses HTTP/2). 
- Uses Protocol Buffers (compact binary format). 
- Bi-directional streaming supported.
- trong contracts and code generation support.

Cons:
- Not human-readable like REST/JSON. 
- Limited browser support — not ideal for public APIs. 
- Requires more tooling to set up.

Example:
```protobuf
rpc GetUser(GetUserRequest) returns (User);
```


## Naming conventions
Endpoint naming is critical in REST API design. The goal is to make them intuitive, consistent, and resource-oriented (not action-oriented).
1. Use Plural Nouns for Resources

    | Resource | Endpoint    |
    |----------|-------------|
    | User     | `/users`    |
    | Product  | `/products` |
    | Order    | `/orders`   |

    Even when fetching a single item:

        ✅ GET /users/123
        ❌ GET /user/123

2. No Verbs in Endpoint Names , The HTTP method already describes the action.
        
    | Purpose          | Method | Good Endpoint | Bad Endpoint       |
    |------------------|--------|---------------|--------------------|
    | Create a product | POST   | `/products`   | `/createProduct`   |
    | Get user info    | GET    | `/users/123`  | `/getUserInfo`     |
    | Delete order     | DELETE | `/orders/456` | `/deleteOrder/456` |

3. Use Nested Resources for Hierarchies: If a resource is logically under another, use nesting.
        
    | Relationship             | Endpoint             |
    |--------------------------|----------------------|
    | Orders of a user         | `/users/123/orders`  |
    | Comments on a blog post  | `/posts/45/comments` |
    | Items in a shopping cart | `/carts/32/items`    |

4. Use Query Parameters for Filters, Pagination, Sorting: Keep endpoints clean — use ? for details.
    ```text
    GET /products?category=electronics&sort=price&page=2&limit=10
    ```
   
    NOT
    ```text
    GET /products/electronics/price/page/2
    ```
5. Use Dash (-) to Separate Words (Not Underscores): URLs use hyphens, not camelCase or snake_case.
    
    | Good                | Bad                |
    |---------------------|--------------------|
    | `/product-reviews`  | `/product_reviews` |
    | `/user-preferences` | `/userPreferences` |

6. Use Consistent Naming for Actions on Resources (When Needed): If an action is not CRUD, use a sub-resource or /action suffix.
    
    | Action                 | Endpoint                         |
    |------------------------|----------------------------------|
    | User login             | `POST /auth/login`               |
    | Password reset request | `POST /users/123/reset-password` |
    | Add item to cart       | `POST /carts/123/items`          |
    | Checkout cart          | `POST /carts/123/checkout`       |
    

## POST/GET Methods
Ask yourself these questions:

1. Will this call change anything on the server? 
   - Yes → Use POST 
   - No → Use GET 
2. Is the client expecting to receive new or updated data? 
   - GET if it’s just retrieval 
   - POST if the data being returned is a result of a creation/action 
3. Is the data being sent sensitive or long? 
   - If yes, use POST (GET URL params are limited & visible)

## Pagination
Pagination is crucial for APIs that return large datasets. It helps manage load and improves performance.
### Common Pagination Strategies
1. **Offset-Based Pagination**: 
   - Use `offset` and `limit` query parameters.
   - Example: `/items?offset=20&limit=10`
   - Pros: Simple to implement.
   - Cons: Can be inefficient for large datasets (as offset grows).
2. **Cursor-Based Pagination**: 
   - Use a unique identifier (cursor) to fetch the next set of results.
   - Example: `/items?cursor=abc123&limit=10`
   - Pros: More efficient for large datasets, avoids issues with data changes.
   - Cons: More complex to implement, requires maintaining state.
3. **Page-Based Pagination**: 
   - Use page numbers.
   - Example: `/items?page=3&limit=10`
   - Pros: Easy to understand.
   - Cons: Can lead to inconsistencies if data changes between requests.
4. **Keyset Pagination**: 
   - Use the last item’s key to fetch the next set.
   - Example: `/items?last_id=123&limit=10`
   - Pros: Efficient, avoids issues with data changes.
   - Cons: Requires knowledge of the last item’s key.
5. **Hybrid Pagination**: 
   - Combine multiple strategies for flexibility.
   - Example: `/items?cursor=abc123&page=2&limit=10`
   - Pros: Offers the best of both worlds.
   - Cons: More complex to implement and understand.
6. **Infinite Scrolling**: 
   - Load more data as the user scrolls down.
   - Example: `/items?offset=20&limit=10` with a JavaScript listener.
   - Pros: Good for user experience.
   - Cons: Can lead to performance issues if not managed properly.

Some example in Post APIs - 
Request: 

```text
POST /products/search
Content-Type: application/json
```

```json
{
  "filters": {
    "category": "electronics",
    "price_range": [100, 1000],
    "in_stock": true
  },
  "page": 2,
  "limit": 20,
  "sort": {
    "field": "price",
    "order": "asc"
  }
}
```

Response: 
```json
{
  "page": 2,
  "limit": 20,
  "total": 245,
  "total_pages": 13,
  "data": [
    { "id": 201, "name": "Bluetooth Speaker", "price": 199 }

  ]
}

```


Best Practices:

| Aspect           | Recommendation                                                                 |
|------------------|--------------------------------------------------------------------------------|
| Pagination keys  | Use `page` & `limit`, or `offset` & `limit`                                    |
| Sort keys        | Use `"sort": { "field": "name", "order": "asc" }`                              |
| Metadata         | Always include `total`, `total_pages`, `page`, `limit` in the response         |
| Cursor-based     | For better performance in large datasets, support `"cursor": "abc123"` instead |
| Default fallback | Have sensible defaults (e.g., page=1, limit=10) if not provided                |


GET vs POST for Pagination:

| Feature                | `GET`                         | `POST`                            |
| ---------------------- | ----------------------------- | --------------------------------- |
| Simple listing         | ✅ `/products?page=2&limit=10` | ❌ Too verbose for simple use case |
| Complex search         | ❌ Query string too long       | ✅ Body allows structured filters  |
| Secure filters         | ❌ Query exposed in URL        | ✅ Body is not logged in URLs      |
| Caching supported      | ✅ Easily cacheable            | ❌ Harder to cache                 |
| Standard REST browsing | ✅                             | ❌ Less intuitive without docs     |


Cursor-Based Pagination (Advanced): If your dataset is large and frequently updated (e.g., social feeds), you may want to use a cursor instead of page numbers:

```json
{
  "filters": { "status": "active" },
  "cursor": "user_123|timestamp_20250706145501",
  "limit": 50
}

```

And return the next cursor in response:

```json
{
  "data": ["asdf"],
  "next_cursor": "user_123|timestamp_20250706150000"
}

```

## Response returned
The answer depends on the type of API request (e.g., fetch, create, update, error), but here's a breakdown of best practices for structuring any API response, consistently and clearly.

Standard Structure for API Responses:
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": 123,
    "name": "Himanshu",
    "email": "himanshu@example.com"
  },
  "meta": {
    "timestamp": "2025-07-06T12:00:00Z"
  }
}
```

Common Fields to Include:

| Field     | Type                | Required          | Description                                             |
|-----------|---------------------|-------------------|---------------------------------------------------------|
| `success` | `bool`              | ✅                 | Indicates if request was successful (`true` or `false`) |
| `message` | `string`            | ✅                 | Human-readable summary of the outcome                   |
| `data`    | `object` or `array` | ✅ (if applicable) | The actual response data (e.g., user, list of products) |
| `errors`  | `array`             | Optional          | Detailed validation or application errors               |
| `meta`    | `object`            | Optional          | Pagination, timestamp, request ID, etc.                 |
| `status`  | `int`               | Optional          | Custom app-level status code (not HTTP status code)     |


Tips for Clean API Responses:
- Keep responses consistent across endpoints. 
- Don’t mix concerns: message is for humans; data is for machines. 
- Avoid returning raw database errors. 
- Use HTTP status codes correctly, but repeat important info inside the body. 
- Include request_id in meta for tracing issues across logs.

Anti-Patterns to Avoid:

| Bad Practice                | Why it's bad                           |
|-----------------------------|----------------------------------------|
| Returning raw DB objects    | Leaks internal structure, not API-safe |
| Missing `success` field     | Clients have to infer from HTTP status |
| No `message` on errors      | Hard to debug or inform users          |
| Inconsistent response shape | Makes client-side parsing fragile      |


Examples:

GET (Success Response)
```json
{
  "success": true,
  "message": "User fetched successfully",
  "data": {
    "id": 42,
    "name": "Himanshu"
  }
}
```
POST (Creation Success)
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": 101,
    "email": "himanshu@example.com"
  }
}
```

Validation Error
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": 101,
    "email": "himanshu@example.com"
  }
}
```

Unauthorized / Forbidden
```json
{
  "success": false,
  "message": "Unauthorized access"
}
```

Paginated Response
```json
{
  "success": true,
  "message": "Products fetched successfully",
  "data": [
    { "id": 1, "name": "iPhone 15" },
    { "id": 2, "name": "Galaxy S23" }
  ],
  "meta": {
    "page": 2,
    "limit": 10,
    "total": 50,
    "total_pages": 5
  }
}
```


## Validations
Validations are crucial for maintaining the integrity, security, and usability of your API. They ensure that the data coming in is correct, safe, and meaningful before your backend processes it.

1. Authentication & Authorization Validation: Ensures the caller is who they say they are and is allowed to perform the action.
    
    | Type        | Example                                   |
    |-------------|-------------------------------------------|
    | Token check | Missing or expired JWT token              |
    | Role check  | Admin-only route being accessed by user   |
    | Ownership   | User trying to update another user's data |

    Always return a 401 (unauthorized) or 403 (forbidden) as appropriate.

2. Schema & Type Validation: Validate data format, types, and structure before your app logic uses it.
    
    | Type            | Example                                    |
    |-----------------|--------------------------------------------|
    | Type checking   | `"age": "twenty"` → invalid, expect number |
    | Required fields | `"email"` missing in signup payload        |
    | Enum validation | `"status": "active"` vs `"frozen"`         |
    | Format checks   | `"email"` is not in valid email format     |
    
   Tools:
      - Python: Pydantic, Marshmallow 
      - Node.js: Joi, Zod 
      - Java: Hibernate Validator

3. Business Logic Validation: These checks enforce your app rules, often beyond static schema validation.
    
    | Rule                           | Example                                              |
    |--------------------------------|------------------------------------------------------|
    | Unique constraints             | Email already exists                                 |
    | Cross-field validation         | `start_date < end_date`                              |
    | Permission rules               | User must belong to the project                      |
    | Item availability              | Product out of stock                                 |
    | Conditional field requirements | If `type = company`, then `company_name` is required |

4. Security Validation: Prevents malicious input or unexpected behavior.
    
    | Threat           | Example                              |
    |------------------|--------------------------------------|
    | SQL Injection    | `"' OR 1=1 --"` in a search box      |
    | XSS Injection    | `<script>alert('x')</script>`        |
    | Mass assignment  | Changing fields like `role: "admin"` |
    | Rate limiting    | Too many requests in short time      |
    | Header tampering | Missing or malformed headers         |

5. Sanitization / Normalization: Clean or adjust data before use (but not reject it).
    
    | Action             | Example                                     |
    |--------------------|---------------------------------------------|
    | Trimming spaces    | `" Himanshu "` → `"Himanshu"`               |
    | Lowercasing emails | `"USER@EXAMPLE.COM"` → `"user@example.com"` |
    | Remove HTML tags   | From comments or feedback                   |
    | Default values     | If `sort` not provided, use `"asc"`         |

6. Pagination / Filtering Validation: Ensure your API doesn't break or over-fetch.

    | Check                    | Example                         |
    |--------------------------|---------------------------------|
    | `limit` is within bounds | No more than 100 items per page |
    | `page` must be >= 1      | No negative or 0 pages          |
    | Sort field is allowed    | Avoid arbitrary sorting fields  |


Example: POST /users Validation Flow
```json
{
  "name": "Himanshu",
  "email": "himanshu@example.com",
  "password": "123"
}
```

Validation Steps:
1. Auth Check (optional): Is the caller allowed to create users? 
2. Schema Check: All fields present? Is email valid? Is password string? 
3. Business Logic: Is email already registered? 
4. Security: Is password strong enough? 
5. Sanitization: Trim name, normalize email. 
6. Response: Return structured error or success.

Tip: Validation Error Structure
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    { "field": "email", "error": "Invalid email format" },
    { "field": "password", "error": "Must be at least 8 characters" }
  ]
}

```

## API Documentation
API documentation is one of the most important parts of any backend service. A well-documented API:
- Helps frontend teams or 3rd-party developers understand how to use it. 
- Reduces back-and-forth communication. 
- Makes onboarding easier. 
- Acts as a contract between services.

Let’s break down the essentials.
1. Overview Section 
    - What does this API do? 
    - Who is the target user? 
    - Base URL: `https://api.example.com/v1`
    - Authentication method (e.g., API key, OAuth, JWT)

2. Endpoint Reference
   
    | Section             | Example                           |
    |---------------------|-----------------------------------|
    | **Method & Path**   | `POST /users`                     |
    | **Description**     | "Creates a new user."             |
    | **Request Headers** | `Authorization: Bearer <token>`   |
    | **Request Body**    | JSON structure with example       |
    | **Query Params**    | For filters, pagination, etc.     |
    | **Response**        | Success and error examples        |
    | **Status Codes**    | `200 OK`, `400 Bad Request`, etc. |

3. Request & Response Examples
    Request:
   ```json
    {
      "name": "Himanshu",
      "email": "himanshu@example.com",
      "password": "Secret123!"
    }
    ```
   Response (201 Created):
    ```
   {
      "success": true,
      "message": "User created successfully",
      "data": {
        "id": 101,
        "email": "himanshu@example.com"
      }
    }
   ```
   
    Response (400 Bad Request):
    ```
   {
      "success": false,
      "message": "Validation failed",
      "errors": [
        { "field": "email", "error": "Email already exists" }
      ]
    }

   ```
4. Authentication Docs
   - Token format: Bearer <JWT>
   - How to get a token (e.g., POST /auth/login)
   - What roles or scopes are required (if RBAC is used)
5. Error Handling Reference: List common errors:
    
    | Code | Meaning               | Description                        |
    |------|-----------------------|------------------------------------|
    | 400  | Bad Request           | Validation or format errors        |
    | 401  | Unauthorized          | Invalid/missing token              |
    | 403  | Forbidden             | No permission                      |
    | 404  | Not Found             | Resource doesn’t exist             |
    | 500  | Internal Server Error | Something went wrong on the server |

6. Rate Limits & Throttling: Document limits:
    - Max requests per minute/hour 
    - What happens when limit is exceeded


## Versioning
API versioning is critical for backward compatibility, allowing you to introduce changes without breaking existing clients.

Why Version an API? 
- Avoid breaking clients using old versions. 
- Allow gradual migration to new features or designs. 
- Support long-term maintenance for external or mobile apps that can't update quickly.


When Should You Introduce a New Version? 
- Changing the shape of the response (adding/removing fields). 
- Renaming or removing endpoints. 
- Changing behavior or business rules. 
- Updating authentication flows or error formats. 
- Adding mandatory fields in a request.

Common API Versioning Strategies

| Strategy                | Example                                 | Pros                      | Cons                                  |
|-------------------------|-----------------------------------------|---------------------------|---------------------------------------|
| **URI Versioning**      | `GET /api/v1/users`                     | Easy to implement and see | Ties version to route structure       |
| **Header Versioning**   | `Accept: application/vnd.myapi.v2+json` | Clean URLs                | Harder to debug, not browser-friendly |
| **Query Parameter**     | `/users?version=2`                      | Easy to test              | Violates REST conventions             |
| **Content Negotiation** | `Accept: application/json; version=2`   | Flexible, RESTful         | Complex to implement                  |



Most Common (and Recommended): URI Versioning
```commandline
GET /api/v1/users
GET /api/v2/users
```

We can use a proxy layer or routing framework to redirect to the correct version internally.


Best Practices for Versioning:

| Rule                           | Recommendation                              |
|--------------------------------|---------------------------------------------|
| Start with `/v1` from day one  | Avoid “unversioned” default API             |
| Be explicit in your versioning | Don’t hide it (e.g., only in documentation) |
| Don’t change existing versions | Add new versions for breaking changes only  |
| Deprecate with a timeline      | Communicate and give time to migrate        |
| Keep versions **independent**  | Don’t let v2 depend on v1 internals         |


What Not to Version ,Avoid versioning for:
- Pagination or filters (use query params instead)
- Non-breaking changes (e.g., adding optional fields)
- Bug fixes (should just be part of current version)


TL;DR: What You Should Do 
- Use URI versioning: /api/v1/... 
- Don’t change a version once released — create a new one. 
- Keep versions documented clearly (and preferably with Swagger). 
- If using Accept headers for versioning, make it strict and well-tested.


## Security
Security is one of the most important aspects of API design and development. A well-secured API protects sensitive data, prevents unauthorized access, and guards against attacks like injection, spoofing, and abuse.

### Authentication – “Who are you?”
Ensures only valid users or systems can access your API.

Common Methods: (Always use HTTPS — never expose tokens over plain HTTP.)

| Method             | Use Case                          |
|--------------------|-----------------------------------|
| **API Key**        | Internal systems, simple use      |
| **JWT**            | User-based access (web/mobile)    |
| **OAuth2**         | Delegated access (Google, GitHub) |
| **Session tokens** | Legacy or browser-based apps      |

### Authorization – “What are you allowed to do?”
Restrict actions based on roles or ownership.

| Rule                 | Example                                     |
|----------------------|---------------------------------------------|
| Role-based           | Only admins can delete users                |
| Resource ownership   | Users can only update their own profile     |
| Scope-based (OAuth2) | Token with `read:products` but not `write:` |


- Input Validation & Sanitization To prevent: SQL Injection , XSS , Command Injection , Mass Assignment
- Rate Limiting / Throttling
- Logging & Monitoring
- Use Secure Headers
- CORS (Cross-Origin Resource Sharing)
- Token Expiry & Rotation
- Avoid Data Leaks (Return minimal data by default., Don’t expose internal IDs, DB schema, or error traces.)

## Error Handling
Error handling is a key part of designing reliable, user-friendly APIs.

If Done right, it helps:
- Frontend developers understand what went wrong. 
- Users see helpful error messages.
- Systems handle edge cases gracefully.

A good API should return:
- The correct HTTP status code. 
- A consistent response structure (return req_id as well for tracing) 
- A clear error message. 
- Optional: field-level validation errors, trace IDs, and debug info in dev mode.

Common HTTP Status Codes:

| Code | Meaning               | When to Use                                       |
|------|-----------------------|---------------------------------------------------|
| 200  | OK                    | Success (GET, POST if not creating)               |
| 201  | Created               | New resource created (POST)                       |
| 204  | No Content            | Successful but no response body (DELETE)          |
| 400  | Bad Request           | Validation errors, missing/invalid input          |
| 401  | Unauthorized          | Missing or invalid auth token                     |
| 403  | Forbidden             | Authenticated, but not allowed                    |
| 404  | Not Found             | Resource doesn’t exist                            |
| 409  | Conflict              | Duplicate data (e.g., user already exists)        |
| 422  | Unprocessable Entity  | Semantic errors in request (e.g., invalid format) |
| 500  | Internal Server Error | Bug on server side                                |
| 503  | Service Unavailable   | DB down, rate limit exceeded, etc.                |


Map Error Types to Status Codes:

| Error Type             | Status Code | Use Case                            |
|------------------------|-------------|-------------------------------------|
| Input validation error | 400 or 422  | Invalid fields, missing data        |
| Auth failure           | 401         | Missing or expired token            |
| Access denied          | 403         | Trying to modify data you don’t own |
| Resource not found     | 404         | Invalid ID                          |
| Conflict               | 409         | Duplicate entries                   |
| Unhandled exceptions   | 500         | Unexpected server-side bug          |
| Service unavailable    | 503         | Downstream service or DB failure    |



Best Practices for Error Handling:

| Rule                                | Example or Tip                                  |
|-------------------------------------|-------------------------------------------------|
| Return consistent error structure   | Use same keys (`success`, `message`, `errors`)  |
| Avoid leaking sensitive info        | Don't expose DB errors, stack traces in prod    |
| Use meaningful status codes         | Don’t just return `200 OK` with `"error": true` |
| Log errors with request IDs         | Helps debug issues in production                |
| Localize error messages (if needed) | e.g., for mobile apps in multiple languages     |
| Fail fast with descriptive errors   | Validate and return early                       |


Anti-Patterns to Avoid:

| Anti-Pattern                        | Why It’s Bad                               |
|-------------------------------------|--------------------------------------------|
| Always return `200 OK`              | Breaks semantic REST; misleads clients     |
| Returning HTML error pages          | Clients expect JSON, not HTML              |
| Different error shapes per endpoint | Hard to write reliable frontend code       |
| Handling all errors as 500          | Hides useful feedback from client and logs |


## Errors thrown

You should "throw" (or return) errors that are:
- Helpful to the client 
- Relevant to the context 
- Mapped to the right HTTP status code 
- Not leaking internal details


### Types of Errors You Should Throw in an API: 

1. Client-Side Errors (4xx): Errors caused by bad input, unauthorized access, or incorrect usage.

    | Type                     | When to Throw It                                 | Status Code |
    |--------------------------|--------------------------------------------------|-------------|
    | **ValidationError**      | Missing fields, wrong types, bad formats         | 400 or 422  |
    | **AuthenticationError**  | No token or invalid token                        | 401         |
    | **AuthorizationError**   | Valid token, but user not allowed                | 403         |
    | **NotFoundError**        | Resource doesn’t exist (e.g., user ID not found) | 404         |
    | **ConflictError**        | Duplicate data (e.g., email already taken)       | 409         |
    | **TooManyRequestsError** | Rate limiting, spam, abuse                       | 429         |
    | **UnsupportedMediaType** | Wrong `Content-Type` header                      | 415         |

2. Server-Side Errors (5xx): Errors caused by unexpected behavior in your system.

    | Type                        | When to Throw It                                    | Status Code |
    |-----------------------------|-----------------------------------------------------|-------------|
    | **InternalServerError**     | Uncaught exception, DB failure, null pointer, etc.  | 500         |
    | **ServiceUnavailableError** | Downstream service or DB is temporarily unavailable | 503         |
    | **GatewayTimeout**          | Timeout calling an external API                     | 504         |

3. Security Errors

    | Error                 | Use Case                      | Status Code |
    |-----------------------|-------------------------------|-------------|
    | **InvalidTokenError** | Malformed or expired JWT      | 401         |
    | **CSRFError**         | CSRF token missing or invalid | 403         |
    | **AccessDeniedError** | User accessing another’s data | 403         |


### Structured Error Naming in Code
In most frameworks, you can create custom exception classes for clarity:

```python
class ValidationError(Exception):
    pass

class NotFoundError(Exception):
    pass

class AuthorizationError(Exception):
    pass

```
Then in middleware:

```python
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return {"success": False, "message": str(e)}, 400
```


### What Should the Error Response Contain?
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    { "field": "email", "error": "Invalid email format" }
  ],
  "code": "VALIDATION_ERROR"
}

```


### Errors You Should Not Throw Directly to Clients

| Internal Error                          | Instead…                                 |
|-----------------------------------------|------------------------------------------|
| Stack trace or traceback                | Return a generic 500 with request ID     |
| Database constraint violation           | Map to 409 Conflict or 422 Unprocessable |
| Library-specific errors (e.g. psycopg2) | Catch and wrap in domain-level error     |
| "NullPointerException" type logs        | Don’t return this in production          |


### Summary: When to Throw What

| Scenario                     | Error to Throw            | HTTP Code |
|------------------------------|---------------------------|-----------|
| Missing email in signup      | `ValidationError`         | 400       |
| Email already in use         | `ConflictError`           | 409       |
| No token provided            | `AuthenticationError`     | 401       |
| Token provided but not admin | `AuthorizationError`      | 403       |
| Product ID not found         | `NotFoundError`           | 404       |
| Unexpected exception         | `InternalServerError`     | 500       |
| DB unavailable               | `ServiceUnavailableError` | 503       |


