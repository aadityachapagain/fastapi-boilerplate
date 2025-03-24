# Fastapi Boilerplate Project

Project to rapidly setup python fastapi project with tests, middleware for auth , payment , life cycle management , ... .

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