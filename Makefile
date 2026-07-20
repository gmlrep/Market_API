up:
	cd app && mkdir certs
	openssl genrsa -out ./app/certs/jwt-private.pem 2048
	openssl rsa -in ./app/certs/jwt-private.pem -pubout -out ./app/certs/jwt-public.pem
	docker-compose up -d