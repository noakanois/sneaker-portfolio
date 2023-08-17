FROM python:3.11-slim

WORKDIR /app

COPY . /app

WORKDIR /app/sneaker-frontend
RUN apt-get update && apt-get install -y npm
RUN npm install
RUN npm run build

WORKDIR /app/sneaker-server
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
