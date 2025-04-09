FROM ecommerce-base

WORKDIR /app/clothes_service

COPY . .

EXPOSE 8003

CMD ["gunicorn", "--bind", "0.0.0.0:8003", "clothes_service.wsgi:application"]
