FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 8081
EXPOSE 8765
EXPOSE 9989

CMD ["python", "main.py"]