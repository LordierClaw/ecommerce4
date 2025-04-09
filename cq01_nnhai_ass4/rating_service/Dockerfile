FROM ecommerce-base

WORKDIR /app/rating_service

COPY . .

EXPOSE 8010

CMD ["gunicorn", "--bind", "0.0.0.0:8010", "rating_service.wsgi:application"]
