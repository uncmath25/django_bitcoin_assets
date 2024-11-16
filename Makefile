.PHONY: clean run-dev stop-dev run-prod stop-prod

DB_IMAGE="mariadb:11.5"
DEV_IMAGE="uncmath25/django_bitcoin_assets_dev"
REMOTE_DEV_DIR="/django_project"
PROD_IMAGE="uncmath25/django_bitcoin_assets_prod"
REMOTE_PROD_IMAGE="uncmath25/django_bitcoin_assets"
REMOTE_PROD_CONTAINER="django_bitcoin_assets"
REMOTE_SERVER_PROFILE="testinglab"
REMOTE_PARENT_WEBSITE_DIR="/home/player1/websites/django_bitcoin_assets"

default: run-dev

clean:
	@echo "*** Cleaning unnecessary caches ***"
	rm -rf `find . -name __pycache__`
	rm -rf `find . -name migrations`
	rm -rf src/db.sqlite3
	rm -rf src/static

run-dev: clean
	@echo "*** Running Django dev server ***"
	docker run -d --rm -e MYSQL_HOST=host.docker.internal -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 \
		-v $$(pwd)/database/sample_dump_dev.sql:/docker-entrypoint-initdb.d/dump.sql $(DB_IMAGE)
	sleep 5
	docker build -t $(DEV_IMAGE) -f Dockerfile-dev .
	docker run --rm --env-file=.env.dev -p 8000:8000 -v $$(pwd)/src:$(REMOTE_DEV_DIR) $(DEV_IMAGE)

stop-dev:
	@echo "*** Stopping Django dev server ***"
	docker rm -f "$$(docker ps -q --filter ancestor=$(DB_IMAGE))"
	docker rm -f "$$(docker ps -q --filter ancestor=$(DEV_IMAGE))"

run-prod: clean
	@echo "*** Running Django prod server ***"
	docker run -d --rm -e MYSQL_HOST=host.docker.internal -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 \
		-v $$(pwd)/database/sample_dump_prod.sql:/docker-entrypoint-initdb.d/dump.sql $(DB_IMAGE)
	sleep 5
	docker build -t $(PROD_IMAGE) -f Dockerfile-prod .
	docker run --rm --env-file=.env.dev -p 8000:8000 $(PROD_IMAGE)

stop-prod:
	@echo "*** Stopping Django prod server ***"
	docker rm -f "$$(docker ps -q --filter ancestor=$(DB_IMAGE))"
	docker rm -f "$$(docker ps -q --filter ancestor=$(PROD_IMAGE))"

deploy: clean
	@echo "*** Deploying Dockerized Django app to DigitalOcean droplet... ***"
	docker build --platform=linux/x86_64 -t $(REMOTE_PROD_IMAGE) -f Dockerfile-prod .
	docker save $(REMOTE_PROD_IMAGE) | ssh -C $(REMOTE_SERVER_PROFILE) docker load
	ssh $(REMOTE_SERVER_PROFILE) "\
		docker rm -f $(REMOTE_PROD_CONTAINER); \
		docker run --rm -d --network host --name $(REMOTE_PROD_CONTAINER) $(REMOTE_PROD_IMAGE); \
	"
	# ssh $(REMOTE_SERVER_PROFILE) rm -rf $(REMOTE_PARENT_WEBSITE_DIR)
	# scp -r ./* $(REMOTE_SERVER_PROFILE):$(REMOTE_PARENT_WEBSITE_DIR)
	# ssh $(REMOTE_SERVER_PROFILE) "\
	# 	cd $(REMOTE_PARENT_WEBSITE_DIR); \
	# 	docker rm -f $(PROD_IMAGE); \
	# 	docker build -t $(PROD_IMAGE) -f Dockerfile-prod .; \
	# 	docker run --rm --env-file=.env --network host --name $(PROD_CONTAINER_NAME) $(PROD_IMAGE); \
	# "
	@echo "*** Restart the remote server with _restart_server.sh ***"
