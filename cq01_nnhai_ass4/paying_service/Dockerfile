FROM ecommerce-base

WORKDIR /app/paying_service

COPY . .

EXPOSE 8009

CMD ["gunicorn", "--bind", "0.0.0.0:8009", "paying_service.wsgi:application"]
