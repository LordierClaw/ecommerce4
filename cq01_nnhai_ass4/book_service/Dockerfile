FROM ecommerce-base

WORKDIR /app/book_service

COPY . .

EXPOSE 8001

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "book_service.wsgi:application"]
