.PHONY: help build test migrate up down restart clean logs shell

# Default target
help:
	@echo "Available commands:"
	@echo "  make build       - Build Docker containers"
	@echo "  make test        - Run all unit tests"
	@echo "  make migrate     - Run Django migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make up          - Start containers"
	@echo "  make down        - Stop containers"
	@echo "  make restart     - Restart containers"
	@echo "  make logs        - View container logs"
	@echo "  make shell       - Open Django shell"
	@echo "  make bash        - Open bash shell in web container"
	@echo "  make clean       - Remove containers, volumes, and images"
	@echo "  make setup       - Build, migrate, and start containers"
	@echo "  make ci          - Build, run tests (CI pipeline)"

# Build Docker containers
build:
	@echo "Building Docker containers..."
	docker-compose build

# Run unit tests
test:
	@echo "Running unit tests..."
	docker-compose exec web python manage.py test

# Run tests with verbose output
test-verbose:
	@echo "Running unit tests (verbose)..."
	docker-compose exec web python manage.py test -v 2

# Run specific app tests
test-photos:
	@echo "Running photos app tests..."
	docker-compose exec web python manage.py test photos

# Run specific test file
test-models:
	@echo "Running model tests..."
	docker-compose exec web python manage.py test photos.tests.test_models

test-views:
	@echo "Running view tests..."
	docker-compose exec web python manage.py test photos.tests.test_views

# Run migrations
migrate:
	@echo "Running migrations..."
	docker-compose exec web python manage.py migrate

# Create new migrations
makemigrations:
	@echo "Creating migrations..."
	docker-compose exec web python manage.py makemigrations

# Start containers
up:
	@echo "Starting containers..."
	docker-compose up -d

# Stop containers
down:
	@echo "Stopping containers..."
	docker-compose down

# Restart containers
restart:
	@echo "Restarting containers..."
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

# Open Django shell
shell:
	docker-compose exec web python manage.py shell

# Open bash shell in web container
bash:
	docker-compose exec web bash

# Clean up containers, volumes, and images
clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --rmi all

# Complete setup: build, migrate, and start
setup: build up migrate
	@echo "Setup complete!"

# CI pipeline: build and test
ci: build up migrate test
	@echo "CI pipeline complete!"

# Database reset (WARNING: destroys data)
reset-db:
	@echo "Resetting database..."
	docker-compose down -v
	docker-compose up -d db
	@sleep 5
	docker-compose exec web python manage.py migrate

# Create superuser
createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# Collect static files
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

# Show database migrations status
showmigrations:
	docker-compose exec web python manage.py showmigrations

# Check for issues
check:
	docker-compose exec web python manage.py check

# Run tests with coverage
coverage:
	@echo "Running tests with coverage..."
	docker-compose exec web coverage run --source='.' manage.py test
	docker-compose exec web coverage report
	docker-compose exec web coverage html
	@echo "Coverage report generated in htmlcov/"

# Install coverage if needed
install-coverage:
	docker-compose exec web pip install coverage

# Format and lint with Ruff
format:
	docker-compose exec web ruff format .

lint:
	docker-compose exec web ruff check .

lint-fix:
	docker-compose exec web ruff check --fix .

# Combined: lint and format
check-code: lint-fix format
	@echo "Code formatting and linting complete!"