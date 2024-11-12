.PHONY: clean dev stop deploy stop-deploy

DEV_IMAGE="uncmath25/django_bitcoin_assets_dev"
REMOTE_DEV_DIR="/django_project"
PROD_IMAGE="uncmath25/django_bitcoin_assets_prod"

default: dev

clean:
	@echo "*** Cleaning unnecessary caches ***"
	rm -rf `find . -name __pycache__`
	rm -rf src/db.sqlite3
	rm -rf src/static

dev: clean
	@echo "*** Starting Django dev server ***"
	docker build -t $(DEV_IMAGE) -f Dockerfile-dev .
	docker run \
		--rm \
		-p 8000:8000 \
		-v $$(pwd):$(REMOTE_DEV_DIR) \
		$(DEV_IMAGE)

stop:
	@echo "*** Stopping Django dev server ***"
	docker rm -f "$$(docker ps -q --filter ancestor=$(DEV_IMAGE))"

deploy: clean
	@echo "*** Deploying Django Dockerized Webserver at http://localhost:8000 ***"
	# docker run \
	# 	-d --rm \
	# 	-e MYSQL_DATABASE="bitcoin_assets" \
	# 	-e MYSQL_ROOT_PASSWORD="PASSWORD" \
	# 	-p 3306:3306 \
	# 	mariadb:11.3.2
	docker build -t $(PROD_IMAGE) -f Dockerfile-prod .
	docker run \
		--rm \
		-p 8000:8000 \
		-v $$(pwd):/django_project \
		$(PROD_IMAGE)

stop-deploy:
	@echo "*** Stopping Django prod server ***"
	docker rm -f "$$(docker ps -q --filter ancestor=$(PROD_IMAGE))"
