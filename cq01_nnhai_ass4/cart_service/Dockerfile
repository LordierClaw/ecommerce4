FROM ecommerce-base

WORKDIR /app/cart_service

COPY . .

EXPOSE 8002

CMD ["gunicorn", "--bind", "0.0.0.0:8002", "cart_service.wsgi:application"]
