FROM ecommerce-base

WORKDIR /app/laptop_service

COPY . .

EXPOSE 8006

CMD ["gunicorn", "--bind", "0.0.0.0:8006", "laptop_service.wsgi:application"]
