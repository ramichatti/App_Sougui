-- Sougui Database Schema
-- Execute this in phpMyAdmin if you prefer manual setup

CREATE DATABASE IF NOT EXISTS sougui_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE sougui_db;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'directeur_vente', 'directeur_achat') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    reset_code VARCHAR(6) NULL,
    reset_code_expires DATETIME NULL,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Power BI Dashboards Table
CREATE TABLE IF NOT EXISTS powerbi_dashboards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role ENUM('admin', 'directeur_vente', 'directeur_achat') NOT NULL,
    dashboard_name VARCHAR(200) NOT NULL,
    embed_url TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
