-- Fake Data Generation Script for E-commerce Microservices
-- This script generates test data for customers, items, orders, and ratings

-- PostgreSQL: Customer Service Data
-- Insert Customers (Django's auth_user table + custom fields)
INSERT INTO auth_user (username, email, password, first_name, last_name, is_active, date_joined)
VALUES 
    ('john_doe', 'john@example.com', 'pbkdf2_sha256$600000$hash1', 'John', 'Doe', true, NOW()),
    ('jane_smith', 'jane@example.com', 'pbkdf2_sha256$600000$hash2', 'Jane', 'Smith', true, NOW()),
    ('bob_wilson', 'bob@example.com', 'pbkdf2_sha256$600000$hash3', 'Bob', 'Wilson', true, NOW()),
    ('alice_brown', 'alice@example.com', 'pbkdf2_sha256$600000$hash4', 'Alice', 'Brown', true, NOW()),
    ('charlie_davis', 'charlie@example.com', 'pbkdf2_sha256$600000$hash5', 'Charlie', 'Davis', true, NOW());

-- Insert Customer Service custom fields
INSERT INTO customer_service_customer (user_id, customer_type, phone, date_of_birth, loyalty_points, preferences)
VALUES 
    (1, 'registered', '+1234567890', '1990-01-15', 100, '{"theme": "dark", "notifications": true}'),
    (2, 'vip', '+1987654321', '1985-05-20', 500, '{"theme": "light", "notifications": true}'),
    (3, 'guest', '+1122334455', '1995-08-10', 0, '{}'),
    (4, 'registered', '+1555666777', '1988-12-25', 250, '{"theme": "dark", "notifications": false}'),
    (5, 'vip', '+1999888777', '1992-03-30', 1000, '{"theme": "light", "notifications": true}');

-- Insert Addresses
INSERT INTO customer_service_address (customer_id, address_type, address_line1, address_line2, city, state, postal_code, country, is_default)
VALUES 
    (1, 'both', '123 Main St', 'Apt 4B', 'New York', 'NY', '10001', 'USA', true),
    (2, 'both', '456 Oak Ave', '', 'Los Angeles', 'CA', '90001', 'USA', true),
    (3, 'shipping', '789 Pine St', 'Suite 2', 'Chicago', 'IL', '60601', 'USA', true),
    (4, 'billing', '321 Elm St', '', 'Houston', 'TX', '77001', 'USA', true),
    (5, 'both', '654 Maple Dr', 'Unit 3', 'Miami', 'FL', '33101', 'USA', true);

-- MongoDB: Items Service Data
-- Insert Categories
db.categories.insertMany([
    {
        name: "Electronics",
        slug: "electronics",
        description: "Electronic devices and accessories",
        parent: null,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        name: "Books",
        slug: "books",
        description: "Books and publications",
        parent: null,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        name: "Clothing",
        slug: "clothing",
        description: "Apparel and accessories",
        parent: null,
        created_at: new Date(),
        updated_at: new Date()
    }
]);

-- Insert Items
db.items.insertMany([
    {
        name: "MacBook Pro 2023",
        slug: "macbook-pro-2023",
        sku: "LAP-001",
        description: "Latest MacBook Pro with M2 chip",
        price: 1299.99,
        sale_price: 1199.99,
        stock_quantity: 50,
        category_id: ObjectId("electronics_id"),
        weight: 2.1,
        dimensions: {length: 35.6, width: 24.8, height: 1.6},
        features: {
            processor: "M2",
            ram: "16GB",
            storage: "512GB"
        },
        status: "published",
        is_featured: true,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        name: "Python Programming Guide",
        slug: "python-programming-guide",
        sku: "BK-001",
        description: "Comprehensive Python programming guide",
        price: 49.99,
        sale_price: null,
        stock_quantity: 100,
        category_id: ObjectId("books_id"),
        weight: 0.5,
        dimensions: {length: 23.5, width: 15.5, height: 2.5},
        features: {
            author: "John Smith",
            pages: 450,
            format: "Paperback"
        },
        status: "published",
        is_featured: false,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        name: "Classic T-Shirt",
        slug: "classic-t-shirt",
        sku: "CLT-001",
        description: "Comfortable cotton t-shirt",
        price: 19.99,
        sale_price: 15.99,
        stock_quantity: 200,
        category_id: ObjectId("clothing_id"),
        weight: 0.2,
        dimensions: {length: 70, width: 50, height: 1},
        features: {
            material: "100% Cotton",
            sizes: ["S", "M", "L", "XL"],
            colors: ["Black", "White", "Blue"]
        },
        status: "published",
        is_featured: true,
        created_at: new Date(),
        updated_at: new Date()
    }
]);

-- MySQL: Order Service Data
-- Insert Orders
INSERT INTO order_service_order (
    customer_id, customer_type, order_date, status,
    shipping_address, billing_address,
    payment_method, payment_id,
    shipping_method, shipping_cost,
    tax, total_price,
    delivery_date, tracking_number,
    notes
) VALUES 
(1, 'registered', NOW(), 'delivered',
 '{"address_line1": "123 Main St", "city": "New York", "state": "NY", "postal_code": "10001", "country": "USA"}',
 '{"address_line1": "123 Main St", "city": "New York", "state": "NY", "postal_code": "10001", "country": "USA"}',
 'credit_card', 'PAY-123456',
 'express', 15.99,
 25.99, 1299.99,
 NOW(), 'TRACK-123456',
 'Please deliver during business hours'),
(2, 'vip', NOW(), 'processing',
 '{"address_line1": "456 Oak Ave", "city": "Los Angeles", "state": "CA", "postal_code": "90001", "country": "USA"}',
 '{"address_line1": "456 Oak Ave", "city": "Los Angeles", "state": "CA", "postal_code": "90001", "country": "USA"}',
 'paypal', 'PAY-789012',
 'standard', 9.99,
 19.99, 49.99,
 NULL, NULL,
 'Gift wrapping requested');

-- Insert Order Items
INSERT INTO order_service_orderitem (
    order_id, item_id, item_type, quantity, price
) VALUES 
(1, 'LAP-001', 'laptop', 1, 1199.99),
(2, 'BK-001', 'book', 1, 49.99);

-- PostgreSQL: Rating Service Data
-- Insert Ratings
INSERT INTO rating_service_rating (
    customer_id, customer_type, item_id, item_type,
    order_id, rating, comment
) VALUES 
(1, 'registered', 'LAP-001', 'laptop', 1, 5, 'Excellent product, fast delivery!'),
(2, 'vip', 'BK-001', 'book', 2, 4, 'Great book, very informative'); 