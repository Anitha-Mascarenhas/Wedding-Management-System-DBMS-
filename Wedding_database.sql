CREATE DATABASE IF NOT EXISTS wedding_management;
USE wedding_management;

CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  password VARCHAR(255),
  is_admin TINYINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS services (
  service_id INT AUTO_INCREMENT PRIMARY KEY,
  service_name VARCHAR(100),
  description TEXT
);

CREATE TABLE IF NOT EXISTS vendors (
  vendor_id INT AUTO_INCREMENT PRIMARY KEY,
  vendor_name VARCHAR(150),
  service_id INT,
  contact VARCHAR(100),
  details TEXT,
  image_path VARCHAR(255),
  FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS bookings (
  booking_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  vendor_id INT,
  service_id INT,
  style_choice VARCHAR(200),
  booking_date DATE,
  created_at DATETIME,
  status VARCHAR(30) DEFAULT 'Pending',
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE SET NULL,
  FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS notifications (
  notification_id INT AUTO_INCREMENT PRIMARY KEY,
  vendor_id INT,
  booking_id INT,
  message TEXT,
  created_at DATETIME,
  sent TINYINT DEFAULT 0,
  FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE,
  FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
);

ALTER TABLE vendors
ADD price INT NOT NULL DEFAULT 0,
ADD rating FLOAT DEFAULT 0;

ALTER TABLE bookings
ADD price INT NOT NULL DEFAULT 0;

ALTER TABLE bookings ADD COLUMN rating FLOAT DEFAULT 0.0;

ALTER TABLE bookings
ADD CONSTRAINT unique_vendor_date UNIQUE (vendor_id, booking_date);

ALTER TABLE bookings ADD COLUMN payment_status VARCHAR(20) DEFAULT 'Unpaid';

SELECT * FROM users;
SELECT * FROM services;
SELECT * FROM vendors;
SELECT * FROM bookings;
SELECT * FROM notifications;



UPDATE services SET description='Elegeant, Personalized, Creative floral and stage designs' WHERE service_id=6;

DESC users;
DESC services;
DESC vendors;
DESC bookings;
DESC notifications;