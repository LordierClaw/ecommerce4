FROM ecommerce-base

WORKDIR /app/items_service

COPY . .

EXPOSE 8005

CMD ["gunicorn", "--bind", "0.0.0.0:8005", "items_service.wsgi:application"]
