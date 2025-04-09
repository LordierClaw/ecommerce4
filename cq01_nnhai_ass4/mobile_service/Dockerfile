FROM ecommerce-base

WORKDIR /app/mobile_service

COPY . .

EXPOSE 8007

CMD ["gunicorn", "--bind", "0.0.0.0:8007", "mobile_service.wsgi:application"]
