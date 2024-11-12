.PHONY: clean dev stop deploy

DEV_IMAGE="uncmath25/django_bitcoin_assets"

default: dev

clean:
	@echo "*** Cleaning unnecessary caches ***"
	rm -rf `find . -name __pycache__`
	rm -rf src/db.sqlite3

dev: clean
	@echo "*** Starting Django dev server ***"
	docker build -t $(DEV_IMAGE) -f Dockerfile .
	docker run 
		-d --rm \
		-p 8000:8000 \
		-v $$(pwd):/django_project \
		$(DEV_IMAGE)

stop:
	@echo "*** Stopping Django dev server ***"
	docker rm -f "$$(docker ps -q --filter ancestor=$(DEV_IMAGE))"

deploy:
	@echo "*** Deploying Django Dockerized Webserver at http://localhost:8000 ***"
	docker run \
		-d --rm \
		-e MYSQL_DATABASE="bitcoin_assets" \
		-e MYSQL_ROOT_PASSWORD="PASSWORD" \
		-p 3306:3306 \
		mariadb:11.3.2
	docker build -t $(DEV_IMAGE) -f Dockerfile .
	docker run 
		-d --rm \
		-p 8000:8000 \
		-v $$(pwd):/django_project \
		$(DEV_IMAGE)
