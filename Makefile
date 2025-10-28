.PHONY: help start up build down clean logs ps shell shell-django shell-react restart migrate collectstatic test test-e2e lint lint-be lint-fe reset-db manage update

# Default target
.DEFAULT_GOAL := help

##@ General

help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

start: ## Start project from scratch with seeded data (uses ./scripts/start_local_dev)
	./scripts/start_local_dev

up: ## Start all containers (docker compose up -d)
	docker compose up -d

stop: ## Stop all containers (docker compose stop)
	docker compose stop

build: ## Build all Docker images
	docker compose build

build-up: ## Build and start all containers
	docker compose up --build -d

down: ## Stop all containers
	docker compose down

clean: ## Stop containers and remove volumes
	docker compose down -v

restart: ## Restart all containers
	docker compose restart

update: ## Build images and run migrations (uses ./scripts/update)
	./scripts/update

##@ Logs & Status

logs: ## Show logs from all containers (follow)
	docker compose logs -f

logs-django: ## Show Django logs (follow)
	docker compose logs -f django

logs-react: ## Show React logs (follow)
	docker compose logs -f react

logs-api: ## Show API logs (follow)
	docker compose logs -f api-app

ps: ## Show status of all containers
	docker compose ps

##@ Shell Access

shell: shell-django ## Open Django shell (default shell command)

shell-django: ## Open Django Python shell
	docker compose exec django python manage.py shell

shell-bash: ## Open bash in Django container
	docker compose exec django bash

shell-react: ## Open bash in React container
	docker compose exec react sh

shell-db: ## Open PostgreSQL shell
	docker compose exec database psql -U opensupplyhub -d opensupplyhub

##@ Database

migrate: ## Run Django migrations
	docker compose run --rm --entrypoint python django manage.py migrate --no-input

makemigrations: ## Create Django migrations
	docker compose run --rm --entrypoint python django manage.py makemigrations

reset-db: ## Reset database and populate with fixture data
	./scripts/reset_database

##@ Django Commands

collectstatic: ## Collect Django static files
	docker compose run --rm --entrypoint sh django -c "mkdir -p /usr/local/src/static/static && chmod -R 755 /usr/local/src/static/static"
	docker compose run --rm --entrypoint python django manage.py collectstatic --noinput

manage: ## Run Django management command (usage: make manage CMD="your command")
	@if [ -z "$(CMD)" ]; then \
		echo "Usage: make manage CMD=\"your command\""; \
		exit 1; \
	fi
	docker compose run --rm --entrypoint python django manage.py $(CMD)

console: ## Open Django management console (uses ./scripts/console)
	./scripts/console

##@ Testing & Quality

test: ## Run Django tests
	docker compose run --rm --entrypoint python django manage.py test

test-e2e: ## Run end-to-end tests
	cd src/e2e && npm test

lint: ## Run all linters
	./scripts/run_bash_script_linter
	./scripts/run_be_code_quality
	./scripts/run_fe_code_quality

lint-be: ## Run backend code quality checks
	./scripts/run_be_code_quality

lint-fe: ## Run frontend code quality checks
	./scripts/run_fe_code_quality

##@ Utilities

dump-db: ## Create database dump
	docker compose exec database pg_dump -U opensupplyhub opensupplyhub > dumps/local_dump_$$(date +%Y%m%d_%H%M%S).dump

restore-db: ## Restore database from dump (usage: make restore-db DUMP=dumps/your_dump.dump)
	@if [ -z "$(DUMP)" ]; then \
		echo "Usage: make restore-db DUMP=dumps/your_dump.dump"; \
		exit 1; \
	fi
	docker compose exec -T database psql -U opensupplyhub -d opensupplyhub < $(DUMP)

prune: ## Remove all stopped containers, unused networks, dangling images
	docker system prune -f

prune-all: ## Remove all stopped containers, unused networks, images (WARNING: destructive)
	docker system prune -af --volumes

