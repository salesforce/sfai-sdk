FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]
