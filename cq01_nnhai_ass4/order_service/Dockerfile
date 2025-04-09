FROM ecommerce-base

WORKDIR /app/order_service

COPY . .

EXPOSE 8008

CMD ["gunicorn", "--bind", "0.0.0.0:8008", "order_service.wsgi:application"]
