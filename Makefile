help:  ## Show this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nmake \033[36m<target>\033[0m\n"} /^([a-zA-Z_-]+|.*-%*):.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

##@ Development

create-env-files:  ## Create .env file for local development
ifeq ("$(wildcard .env)","")
	@echo "POSTGRES_USER=dataminr" > .env
	@echo "POSTGRES_PASSWORD=CHANGEME" >> .env
	@echo "POSTGRES_DB=dataminr" >> .env
	@echo "POSTGRES_HOST=postgres" >> .env
	@echo "POSTGRES_PORT=5432" >> .env
	@echo "OPEN_WEATHER_MAP_API_KEY=CHANGE" >> .env
endif

install-pip-tools:
	pip install pip-tools

compile-requirements: install-pip-tools
	pip-compile --upgrade requirements.in

build: create-env-files  ## Build all services in docker-compose.yml
	docker-compose build

test: build  ## Run all tests
	docker-compose run web bash -c "py.test"

lint: build  ## Run all linters
	docker-compose run web bash -c "flake8 ."
	docker-compose run web bash -c "black --check ."
	docker-compose run web bash -c "mypy ."

##@ Application

up:  ## Run all services
	docker-compose up

down:  ## Shut down all services
	docker-compose down --remove-orphans
