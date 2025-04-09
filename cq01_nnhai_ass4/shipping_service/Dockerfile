FROM ecommerce-base

WORKDIR /app/shipping_service

COPY . .

EXPOSE 8011

CMD ["gunicorn", "--bind", "0.0.0.0:8011", "shipping_service.wsgi:application"]
