.PHONY: server frontend

server:
	cd sneaker-server && poetry run uvicorn api.main:app

build:
	cd sneaker-frontend && npm install
	cd sneaker-frontend && npm run build

frontend:
	cd sneaker-frontend && npm start
