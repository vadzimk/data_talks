CREATE DATABASE test;
CREATE TABLE IF NOT EXISTS orders (
    order_id varchar,
    date date,
    product_name varchar,
    quantity int,
    primary key (order_id)
);