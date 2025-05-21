#!/bin/bash

# Esperar a que MySQL esté listo
echo "Esperando a que MySQL esté disponible..."
until mysql -h db -uuser -proot -e "SELECT 1;" APIGestionAcademica-DB; do
  >&2 echo "MySQL no está listo. Esperando..."
  sleep 3
done

echo "MySQL está listo. Ejecutando migraciones Alembic..."
alembic upgrade head

echo "Iniciando FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload