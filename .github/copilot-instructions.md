# Python Coding Practices

> Essential practices for clean, maintainable Python code.

## Code Style

**Follow PEP 8 with modern tooling:**
- Use Ruff for formatting and linting
- 4 spaces for indentation (never tabs)
- 88-character line limit
- 2 blank lines between classes/functions, 1 between methods

```python
# Good
def process_user_data(
    user_id: int,
    settings: dict[str, Any] | None = None,
) -> ProcessedUser:
    """Process user data with optional settings."""
    pass
```

## Type Annotations

**Use Python 3.10+ syntax:**
```python
def transform_items(
    items: list[dict[str, int | float]], 
    threshold: float = 0.5
) -> tuple[list[dict[str, Any]], int]:
    """Transform items above threshold."""
    pass
```

## Error Handling

**Handle errors specifically with logging:**
```python
import logging

logger = logging.getLogger(__name__)

try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise ProcessingError(f"Failed to process: {e}") from e
```

## Testing

**Write tests first:**
```python
def test_process_valid_data_succeeds():
    """Test that valid data processes correctly."""
    # Given
    data = {"id": 1, "value": 100}
    
    # When 
    result = process_data(data)
    
    # Then
    assert result.status == "success"
```

## Documentation

**Use clear docstrings:**
```python
def calculate_total(items: list[Item]) -> Decimal:
    """Calculate total value of items.
    
    Args:
        items: List of items to sum. Must not be empty.
    
    Returns:
        Total value as Decimal.
        
    Raises:
        ValueError: If items list is empty.
    """
```

## Naming

**Use descriptive names:**
```python
# Variables/functions: snake_case
user_count = len(active_users)
def get_user_preferences(): pass

# Classes: PascalCase  
class PaymentProcessor: pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
```

## Common Anti-Patterns to Avoid

```python
# ❌ Mutable defaults
def process(items, results=[]):
    
# ✅ Use None  
def process(items, results=None):
    if results is None:
        results = []

# ❌ Silent errors
try:
    operation()
except:
    pass

# ✅ Handle specifically
try:
    operation()
except SpecificError as e:
    logger.warning(f"Expected error: {e}")

# ❌ Complex comprehensions
result = [x.value for group in data for x in group.items if x.valid and x.value > 10]

# ✅ Break into readable loops
result = []
for group in data:
    for item in group.items:
        if item.valid and item.value > 10:
            result.append(item.value)
```

## Performance Tips

```python
# Use appropriate data structures
user_lookup = {user.id: user for user in users}  # O(1) vs O(n)

# Use generators for large data
total = sum(item.value for item in large_dataset)

# Use built-in functions
for index, item in enumerate(items):  # vs range(len())
    pass
```