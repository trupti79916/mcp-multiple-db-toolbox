# MCP Multi-DB Toolkit

Connect to multiple databases using 1 MCP server.

## Overview

This MCP (Model Context Protocol) server provides a unified gateway to interact with multiple databases simultaneously. It supports PostgreSQL, MongoDB, and Redis, with automatic tool generation based on your configuration.

### Architecture

- **Single MCP Server**: One server instance handles all database connections
- **Dynamic Tool Generation**: Tools are automatically created based on your `config.yaml`
- **Connection Pooling**: Efficient connection management for optimal performance
- **SSE/HTTP Protocol**: Streamable HTTP transport for remote server access
- **Secure Credentials**: Environment variables for sensitive data

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/trupti79916/mcp-multiple-db-toolbox.git
cd mcp-multiple-db-toolbox
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your databases:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

4. Update `config.yaml` with your database configurations (see Configuration section)

## Configuration

### config.yaml

**Configure only the databases you need!** You don't have to set up all database types - just uncomment and configure the ones you want to use.

The MCP server will automatically create tools for only the databases you configure.

**Example 1: PostgreSQL Only**
```yaml
databases:
  - id: "prod_postgres"
    type: "postgres"
    host: "localhost"
    port: 5432
    user: "${PROD_POSTGRES_USER}"
    password: "${PROD_POSTGRES_PASSWORD}"
    dbname: "prod"
```

**Example 2: MongoDB Atlas (Cloud)**
```yaml
databases:
  - id: "atlas_mongo"
    type: "mongodb"
    uri: "${MONGODB_ATLAS_URI}"
    database: "production"
```

Set in `.env`:
```bash
MONGODB_ATLAS_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**Example 3: Multiple Databases**
```yaml
databases:
  - id: "prod_postgres"
    type: "postgres"
    host: "localhost"
    port: 5432
    user: "${PROD_POSTGRES_USER}"
    password: "${PROD_POSTGRES_PASSWORD}"
    dbname: "prod"

  - id: "atlas_mongo"
    type: "mongodb"
    uri: "${MONGODB_ATLAS_URI}"
    database: "production"

  - id: "cache_redis"
    type: "redis"
    host: "localhost"
    port: 6379
    db: 0
```

**Example 3: Multiple PostgreSQL Instances**
```yaml
databases:
  - id: "prod_postgres"
    type: "postgres"
    host: "prod-db.example.com"
    port: 5432
    user: "${PROD_POSTGRES_USER}"
    password: "${PROD_POSTGRES_PASSWORD}"
    dbname: "prod"

  - id: "analytics_postgres"
    type: "postgres"
    host: "analytics-db.example.com"
    port: 5432
    user: "${ANALYTICS_POSTGRES_USER}"
    password: "${ANALYTICS_POSTGRES_PASSWORD}"
    dbname: "analytics"
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# PostgreSQL
PROD_POSTGRES_USER=your_username
PROD_POSTGRES_PASSWORD=your_password

# Add other credentials as needed
```

**Note**: Values in `config.yaml` using `${VAR_NAME}` syntax will be replaced with environment variables.

## Running the Server

Start the MCP server with SSE transport:

```bash
python main.py
```

The server will:
1. Load configuration from `config.yaml`
2. Validate environment variables
3. Initialize database connectors
4. Start the MCP server with HTTP/SSE protocol
5. Listen for incoming requests

## Available Tools

Tools are automatically generated based on your database configurations:

### PostgreSQL Tools

#### `query_postgres`
Execute SQL queries against a PostgreSQL database.

**Parameters:**
- `db_id` (str): Database identifier (e.g., "prod_postgres")
- `query` (str): SQL query to execute
- `params` (str, optional): JSON string of query parameters

**Example:**
```python
query_postgres(
    db_id="prod_postgres",
    query="SELECT * FROM users WHERE id = %s",
    params='[1]'
)
```

### MongoDB Tools

#### `find_mongodb`
Find documents in a MongoDB collection.

**Parameters:**
- `db_id` (str): Database identifier (e.g., "dev_mongo")
- `collection` (str): Collection name
- `query` (str): Query filter as JSON string
- `projection` (str, optional): Projection as JSON string

**Example:**
```python
find_mongodb(
    db_id="dev_mongo",
    collection="users",
    query='{"age": {"$gt": 18}}',
    projection='{"name": 1, "email": 1}'
)
```

#### `insert_mongodb`
Insert a document into a MongoDB collection.

**Parameters:**
- `db_id` (str): Database identifier
- `collection` (str): Collection name
- `document` (str): Document to insert as JSON string

**Example:**
```python
insert_mongodb(
    db_id="dev_mongo",
    collection="users",
    document='{"name": "John", "age": 30}'
)
```

### Redis Tools

#### `get_redis`
Get a value from Redis cache.

**Parameters:**
- `db_id` (str): Database identifier (e.g., "cache_redis")
- `key` (str): Key to retrieve

#### `set_redis`
Set a value in Redis cache.

**Parameters:**
- `db_id` (str): Database identifier
- `key` (str): Key to set
- `value` (str): Value to store
- `expiry` (int, optional): Expiry time in seconds

#### `delete_redis`
Delete a key from Redis cache.

**Parameters:**
- `db_id` (str): Database identifier
- `key` (str): Key to delete

## Project Structure

```
mcp-multiple-db-toolbox/
├── main.py                 # Main MCP server with FastMCP
├── config.yaml            # Database configurations
├── config_parser.py       # Configuration loader with validation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── connectors/           # Database connector modules
│   ├── postgres.py       # PostgreSQL connector
│   ├── mongodb.py        # MongoDB connector
│   └── redis.py          # Redis connector
└── README.md
```

## Error Handling

The server includes comprehensive error handling:

- **Configuration Errors**: Validates config.yaml and environment variables on startup
- **Connection Errors**: Graceful handling of database connection failures
- **Query Errors**: Detailed error messages for malformed queries
- **Logging**: All operations are logged for debugging

## Common Use Cases

### Use Case 1: PostgreSQL Only
Perfect for teams using only PostgreSQL databases:
- Configure just your PostgreSQL databases in `config.yaml`
- Tools created: `query_postgres` for each database
- Set only PostgreSQL environment variables

### Use Case 2: Microservices Architecture
Different services use different databases:
- Configure Postgres for main app data
- Configure MongoDB for document storage
- Configure Redis for caching
- All accessible through one MCP server!

### Use Case 3: Multi-Environment
Same database type, different environments:
```yaml
databases:
  - id: "prod_postgres"
    # Production database config
  - id: "staging_postgres"
    # Staging database config
  - id: "dev_postgres"
    # Development database config
```

### Use Case 4: Analytics + Operational
Separate databases for different purposes:
- Operational PostgreSQL for transactional data
- Analytics MongoDB for aggregated data
- Redis for real-time caching

## Adding New Databases

1. Add a new entry to `config.yaml`:
```yaml
databases:
  - id: "new_db"
    type: "postgres"  # or mongodb, redis
    # ... connection details
```

2. Set required environment variables in `.env`

3. Restart the server

The tools will be automatically generated!

## Development

### Testing Configuration

Test your configuration:
```bash
python config_parser.py
```

### Adding Support for New Database Types

1. Create a new connector in `connectors/`
2. Add tool functions in `main.py` using `@mcp.tool()` decorator
3. Update configuration validation in `config_parser.py`

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
