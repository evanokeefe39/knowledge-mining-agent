# Database Module Usage Policy

All database connections, introspection, and health checks should use the `db.py` module. This ensures consistent connection management, proper error handling, and adherence to configuration standards.

**For Ad Hoc Tasks:**
- Use `import db` and the convenience functions like `db.connect()`, `db.health_check()`, `db.get_schemas()`, etc.
- Always call `db.disconnect()` when done

**For Applications and Services:**
- Import the `DatabaseConnection` class for more control
- Use the module's introspection functions for schema exploration
- Implement proper connection pooling if needed for high-traffic services

**Example Usage:**
```python
import db

# Connect and check health
db.connect()
status = db.health_check()
if status['status'] != 'healthy':
    raise Exception("Database unhealthy")

# Perform operations
schemas = db.get_schemas()
tables = db.get_tables('dw')

# Always disconnect
db.disconnect()
```