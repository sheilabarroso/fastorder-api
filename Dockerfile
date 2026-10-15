FROM python:3.12-slim

WORKDIR /app

# Dependências primeiro: aproveita o cache de camadas do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código depois: muda com frequência, não invalida a camada acima
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
