FROM ecommerce-base

WORKDIR /app/gateway_service

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "gateway_service.wsgi:application"]
