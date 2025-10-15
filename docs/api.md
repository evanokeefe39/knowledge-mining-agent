# API Reference

## Agent Module

### KnowledgeMiningAgent

A class for the knowledge mining agent.

#### Methods

- `__init__()`: Initializes the agent with config, tools, and prompt.
- `run(query: str)`: Runs the agent with the given query.

## Config Module

### get_config()

Returns configuration settings parsed from config.yaml and .env.

## Database Module

### get_db()

Returns a configured PostgreSQL database connection from the connection pool.

### close_db(conn)

Returns a database connection to the pool.

### test_connection()

Tests the database connection and logs the result.

### describe_schema()

Inspects and logs the structure of the configured database schema, including tables, columns, and row counts.

## Tools Module

### get_tools()

Returns a list of tools for the agent.

### ExampleTool

A placeholder tool.

#### Methods

- `_run(query: str)`: Processes the query.

## Prompts Module

### get_agent_prompt()

Returns the prompt template for the agent.

## Health Check

### health_check()

Performs a health check on the database connection.