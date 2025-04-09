FROM ecommerce-base

WORKDIR /app/customer_service

COPY . .

EXPOSE 8004

CMD ["gunicorn", "--bind", "0.0.0.0:8004", "customer_service.wsgi:application"]
