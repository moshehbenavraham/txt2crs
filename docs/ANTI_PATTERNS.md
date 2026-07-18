# Anti-Patterns Guide

> What NOT to do when working with this codebase. AI agents trained on internet code often reproduce these common anti-patterns.

## Security Anti-Patterns

### NEVER: Include sensitive data in API responses

```python
# BAD - Exposes password hash
@router.get("/users/{user_id}")
def get_user(user_id: UUID) -> User:
    return db.get(User, user_id)  # Returns ALL fields including hashed_password

# GOOD - Use response model to filter fields
@router.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: UUID) -> User:
    return db.get(User, user_id)  # FastAPI filters to UserPublic fields only
```

### NEVER: Trust user input for database queries

```python
# BAD - SQL injection risk
query = f"SELECT * FROM users WHERE email = '{email}'"

# GOOD - Use parameterized queries (SQLModel does this automatically)
statement = select(User).where(User.email == email)
```

### NEVER: Hardcode secrets

```python
# BAD
SECRET_KEY = "my-super-secret-key-123"

# GOOD - Use environment variables
from app.core.config import settings
SECRET_KEY = settings.SECRET_KEY
```

### NEVER: Store plain text passwords

```python
# BAD - Never store passwords in plain text
user.password = password_input

# GOOD - Always hash passwords
from app.core.security import get_password_hash
user.hashed_password = get_password_hash(password_input)
```

### NEVER: Return stack traces in production errors

```python
# BAD - Exposes internal structure
except Exception as e:
    return {"error": str(e), "traceback": traceback.format_exc()}

# GOOD - Use structured error format
from app.core.exceptions import AppException
from app.core.constants import ErrorCode
raise AppException(code=ErrorCode.INTERNAL_ERROR, detail="An unexpected error occurred")
```

---

## Architecture Anti-Patterns

### AVOID: God Classes

```python
# BAD - One class doing everything
class UserService:
    def authenticate(self): ...
    def update_profile(self): ...
    def process_payment(self): ...
    def send_notification(self): ...
    def generate_report(self): ...

# GOOD - Separate concerns
class AuthService: ...
class ProfileService: ...
class PaymentService: ...
class NotificationService: ...
```

### AVOID: Magic Numbers

```python
# BAD - What does 100 mean?
if len(items) > 100:
    raise ValueError("Too many items")

# GOOD - Use named constants
from app.core.constants import Pagination
if len(items) > Pagination.MAX_LIMIT:
    raise ValueError(f"Cannot exceed {Pagination.MAX_LIMIT} items")
```

### AVOID: Circular Imports

```python
# BAD - Circular dependency
# file: users.py
from items import get_user_items

# file: items.py
from users import get_item_owner

# GOOD - Restructure or use TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from users import User
```

### AVOID: Mixing Business Logic with Routes

```python
# BAD - Business logic in route handler
@router.post("/users/")
def create_user(user_in: UserCreate, session: SessionDep):
    # All logic embedded in route
    if session.exec(select(User).where(User.email == user_in.email)).first():
        raise HTTPException(status_code=409, detail="Email taken")
    hashed = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed)
    session.add(user)
    session.commit()
    return user

# GOOD - Delegate to CRUD layer
@router.post("/users/", response_model=UserPublic)
def create_user(user_in: UserCreate, session: SessionDep) -> User:
    return crud.create_user(session=session, user_create=user_in)
```

---

## Frontend Anti-Patterns

### NEVER: Edit generated API client files

```typescript
// BAD - Never modify files in src/client/
// frontend/src/client/services/UsersService.ts
export class UsersService {
  // DO NOT ADD CODE HERE - this file is auto-generated!
}

// GOOD - Run the generator when backend changes
// npm run generate-client
```

### AVOID: Inline styles over Tailwind

```tsx
// BAD - Inline styles are harder to maintain
<div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>

// GOOD - Use Tailwind classes
<div className="flex items-center gap-2">
```

### AVOID: Direct state mutation

```typescript
// BAD - Mutating state directly
const [items, setItems] = useState<Item[]>([]);
items.push(newItem);  // Direct mutation!
setItems(items);

// GOOD - Create new array
setItems([...items, newItem]);
```

### AVOID: Ignoring loading/error states

```tsx
// BAD - No loading or error handling
function UserProfile({ userId }: { userId: string }) {
  const { data } = useQuery(['user', userId], () => fetchUser(userId));
  return <div>{data.name}</div>;  // Crashes if data is undefined!
}

// GOOD - Handle all states
function UserProfile({ userId }: { userId: string }) {
  const { data, isLoading, error } = useQuery(['user', userId], () => fetchUser(userId));

  if (isLoading) return <Spinner />;
  if (error) return <ErrorDisplay error={error} />;
  return <div>{data.name}</div>;
}
```

### AVOID: Prop drilling

```tsx
// BAD - Passing props through many layers
<App user={user}>
  <Dashboard user={user}>
    <Sidebar user={user}>
      <UserInfo user={user} />

// GOOD - Use context or state management
const { user } = useAuth();  // Access from any component
```

---

## AI Coding Anti-Patterns

These anti-patterns specifically arise when working with AI coding assistants:

### AVOID: Context Overflow

```markdown
# BAD - Sending same info multiple times
"Here's the User model again: [100 lines]"
"And here's the User model: [100 lines]"

# GOOD - Reference previously shared context
"Using the User model shown earlier..."
```

### AVOID: Lost Oversight

```markdown
# BAD - Accepting code without review
AI generates 500 lines → commit without reading

# GOOD - Always review security-sensitive code
AI generates auth code → review each line → understand implications → commit
```

### AVOID: Vibe Coding

```markdown
# BAD - Letting AI make all architectural decisions
"Just build me a user system"

# GOOD - Maintain architectural control
"Build user registration following our existing patterns in crud.py and routes/users.py"
```

### AVOID: Wrong Tool for Job

```markdown
# BAD - Asking LLM to count or calculate
"How many lines are in this file?"

# GOOD - Use code for computational tasks
wc -l file.py
```

---

## Type Safety Anti-Patterns

### NEVER: Use `Any` without justification

```python
# BAD - Defeats type checking
def process(data: Any) -> Any:
    return data["field"]

# GOOD - Use proper types
def process(data: dict[str, str]) -> str:
    return data["field"]

# If Any is truly needed, document why
def handle_external_data(data: Any) -> str:  # Any needed: external API returns untyped JSON
    ...
```

### NEVER: Suppress type errors without comment

```python
# BAD - Silent suppression
result = complex_function()  # type: ignore

# GOOD - Document why suppression is needed
result = complex_function()  # type: ignore[return-value] - FastAPI bug #1234
```

### AVOID: Missing type annotations

```python
# BAD - Untyped function
def get_user_items(session, user_id, skip=0, limit=100):
    ...

# GOOD - Fully typed
def get_user_items(
    session: Session,
    user_id: UUID,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[Item]:
    ...
```

---

## Testing Anti-Patterns

### AVOID: Tests without assertions

```python
# BAD - Test runs but asserts nothing
def test_create_user():
    response = client.post("/users/", json={"email": "test@test.com"})
    print(response.json())  # No assertions!

# GOOD - Clear assertions
def test_create_user():
    response = client.post("/users/", json={"email": "test@test.com", "password": "ValidPass123"})
    assert response.status_code == 201
    assert response.json()["email"] == "test@test.com"
    assert "id" in response.json()
```

### AVOID: Flaky tests with timing issues

```python
# BAD - Race condition / timing dependency
def test_async_operation():
    start_background_task()
    time.sleep(2)  # Hope it finishes in 2 seconds
    assert task_completed()

# GOOD - Use proper async patterns
async def test_async_operation():
    task = await start_background_task()
    result = await task  # Wait for actual completion
    assert result.completed
```

### AVOID: Tests that depend on other tests

```python
# BAD - Test order matters
def test_create_user():
    global created_user
    created_user = create_user(...)

def test_delete_user():
    delete_user(created_user.id)  # Fails if run in isolation!

# GOOD - Each test is independent
def test_delete_user(existing_user):  # Fixture provides user
    delete_user(existing_user.id)
```

---

## Database Anti-Patterns

### NEVER: N+1 queries

```python
# BAD - N+1 query problem
users = session.exec(select(User)).all()
for user in users:
    items = session.exec(select(Item).where(Item.owner_id == user.id)).all()  # N queries!

# GOOD - Use eager loading or single query
statement = select(User).options(selectinload(User.items))
users = session.exec(statement).all()
```

### AVOID: Missing indexes on frequently queried columns

```python
# BAD - Slow queries on unindexed columns
# Frequent query: SELECT * FROM users WHERE email = ?
# But email column has no index

# GOOD - Add index in SQLModel
class User(SQLModel, table=True):
    email: EmailStr = Field(index=True)  # Index on frequently queried column
```

### AVOID: Storing derived data that can be computed

```python
# BAD - Storing computed value
class Order(SQLModel, table=True):
    subtotal: float
    tax: float
    total: float  # Redundant: subtotal + tax

# GOOD - Compute when needed
class Order(SQLModel, table=True):
    subtotal: float
    tax: float

    @property
    def total(self) -> float:
        return self.subtotal + self.tax
```

---

## References

- [LLM Anti-Patterns - InstaVM](https://instavm.io/blog/llm-anti-patterns)
- [My LLM Coding Workflow - Addy Osmani](https://addyosmani.com/blog/ai-coding-workflow/)
- [AI Code Security Anti-Patterns](https://github.com/Arcanum-Sec/sec-context)
- [Coding with LLMs in 2025 - Antirez](https://antirez.com/news/154)
- [SonarSource: 15-43% of AI-generated code contains security flaws](https://www.sonarsource.com/blog/ai-generated-code-security/)
