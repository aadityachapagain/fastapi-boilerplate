# Fastapi Boilerplate Project

Project to rapidly setup python fastapi project with tests, middleware for auth , payment , life cycle management , ... .

## Architecture

The application follows a layered architecture:

1. **Routes Layer** (`routes.py`): API endpoints definitions and request handling
2. **Service Layer** (`service.py`): Business logic implementation
3. **Data Layer** (`models.py`): Database schema and data access
4. **Event System** (`events.py`): Pub/sub event handling for async operations

### Key Components

- **Authentication**: Bearer token authentication implemented as middleware
- **Validation**: Generic utilities for input validation
- **Error Handling**: Consistent error responses
- **Event System**: Pub/sub pattern for decoupling operations
- **Logging**: Comprehensive logging for operations and errors

## Structured Segregation of Routers/endpoint

Inside routers, you can see `items` directory which refers to endpoint related to items.
Similarly, in future if you had to add new set of endpoints for new tasks, you would just create new directory
where you put your implementation logic and import it directly to main.py as a router. 

```py

app.include_router(items_router, prefix="/api/v1")
app.include_router(tasks, prefix="/api/v1/")

# so on
```

## Requirements

- Python 3.10+
- MongoDB 4.4+
- FastAPI 0.110.0+
- MongoEngine 0.28.0+
- See `requirements.txt` for all dependencies

## Setup & Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd items-api
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables (create a `.env` file in the project root):
   ```
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB_NAME=items_db
   LOG_LEVEL=DEBUG
   ```

4. Start the application:
   ```bash
   uvicorn src.main:app --reload
   ```

### Using Docker

1. Make sure Docker and Docker Compose are installed

2. Run the application:
   ```bash
   docker-compose up -d
   ```

## API Endpoints

All endpoints require authentication with a Bearer token (any non-empty string is accepted).

- `POST /items`: Create a new item
- `GET /items`: List all items
- `GET /items/{id}`: Get a specific item by ID
- `PATCH /items/{id}`: Update an item
- `DELETE /items/{id}`: Delete an item

### Data Format

- Input data should use **camelCase** for property names
- Output data will be returned with **camelCase** property names
- Internally, the application uses **snake_case** for property names

## Running Tests

Run tests with pytest:

```bash
pytest
```

Run tests with coverage:

```bash
coverage run -m pytest
coverage report
```