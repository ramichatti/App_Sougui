-- =============================================================================
-- Sougui Database Setup Script
-- =============================================================================
-- Run this in phpMyAdmin or MySQL CLI to create the full database with
-- users, roles, privileges, dashboards, and notifications.
--
-- Prerequisites: XAMPP with MySQL running
-- Usage:
--   Option 1: Import via phpMyAdmin (http://localhost/phpmyadmin)
--   Option 2: mysql -u root < setup_database.sql
-- =============================================================================

-- ── Create database ─────────────────────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS sougui_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sougui_db;

-- ── Drop existing tables (clean slate) ──────────────────────────────────────
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS role_privileges;
DROP TABLE IF EXISTS app_notifications;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS privileges;
DROP TABLE IF EXISTS powerbi_dashboards;
DROP TABLE IF EXISTS roles;
SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================================
-- TABLE: roles
-- =============================================================================
CREATE TABLE roles (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_admin    BOOLEAN DEFAULT FALSE,
    is_system   BOOLEAN DEFAULT FALSE,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_roles_name (name),
    INDEX idx_roles_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLE: powerbi_dashboards
-- =============================================================================
CREATE TABLE powerbi_dashboards (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    dashboard_name  VARCHAR(200) NOT NULL,
    embed_url       TEXT NOT NULL,
    description     TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_dashboards_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLE: privileges
-- Each privilege optionally references a dashboard (controls access to it)
-- =============================================================================
CREATE TABLE privileges (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(200) NOT NULL,
    description   TEXT,
    dashboard_id  INT NULL,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_privilege_dashboard
        FOREIGN KEY (dashboard_id)
        REFERENCES powerbi_dashboards(id)
        ON DELETE CASCADE,

    INDEX idx_privilege_dashboard (dashboard_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLE: role_privileges  (M2M: Role <-> Privilege)
-- =============================================================================
CREATE TABLE role_privileges (
    role_id       INT NOT NULL,
    privilege_id  INT NOT NULL,

    PRIMARY KEY (role_id, privilege_id),

    CONSTRAINT fk_rp_role
        FOREIGN KEY (role_id)
        REFERENCES roles(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_rp_privilege
        FOREIGN KEY (privilege_id)
        REFERENCES privileges(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLE: users
-- =============================================================================
CREATE TABLE users (
    id                            INT AUTO_INCREMENT PRIMARY KEY,
    email                         VARCHAR(120) NOT NULL UNIQUE,
    password_hash                 VARCHAR(255) NOT NULL,
    first_name                    VARCHAR(100) NOT NULL,
    last_name                     VARCHAR(100) NOT NULL,
    role_id                       INT NULL,
    is_active                     BOOLEAN DEFAULT TRUE,
    profile_image                 LONGBLOB NULL,
    created_at                    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at                    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Password reset (forgot password flow)
    reset_code                    VARCHAR(6) NULL,
    reset_code_expires            DATETIME NULL,

    -- Password change (profile flow)
    password_change_code          VARCHAR(6) NULL,
    password_change_code_expires  DATETIME NULL,

    -- Email change (profile flow)
    email_change_code             VARCHAR(6) NULL,
    email_change_code_expires     DATETIME NULL,
    pending_email                 VARCHAR(120) NULL,

    CONSTRAINT fk_user_role
        FOREIGN KEY (role_id)
        REFERENCES roles(id)
        ON DELETE SET NULL,

    INDEX idx_users_email (email),
    INDEX idx_users_role (role_id),
    INDEX idx_users_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- TABLE: app_notifications
-- =============================================================================
CREATE TABLE app_notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    title       VARCHAR(255) NOT NULL,
    message     TEXT NOT NULL,
    type        VARCHAR(50) DEFAULT 'privilege',
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notification_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    INDEX idx_notif_user (user_id),
    INDEX idx_notif_read (is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================================
-- SEED DATA
-- =============================================================================

-- ── 1. System Roles ─────────────────────────────────────────────────────────
INSERT INTO roles (id, name, description, is_admin, is_system, is_active) VALUES
    (1, 'admin',           'Administrateur système — accès complet',  TRUE,  TRUE, TRUE),
    (2, 'directeur_vente', 'Directeur des ventes',                    FALSE, TRUE, TRUE),
    (3, 'directeur_achat', 'Directeur des achats',                    FALSE, TRUE, TRUE);

-- ── 2. Sample Dashboards ────────────────────────────────────────────────────
INSERT INTO powerbi_dashboards (id, dashboard_name, embed_url, description, is_active) VALUES
    (1, 'Dashboard Admin — Vue Globale',
        'https://app.powerbi.com/view?r=YOUR_ADMIN_REPORT_ID',
        'Vue d''ensemble complète de l''entreprise',
        TRUE),
    (2, 'Dashboard Ventes',
        'https://app.powerbi.com/view?r=YOUR_SALES_REPORT_ID',
        'Analyse des ventes et performances commerciales',
        TRUE),
    (3, 'Dashboard Achats',
        'https://app.powerbi.com/view?r=YOUR_PURCHASE_REPORT_ID',
        'Suivi des achats et gestion des fournisseurs',
        TRUE);

-- ── 3. Privileges (one per dashboard) ───────────────────────────────────────
INSERT INTO privileges (id, name, description, dashboard_id) VALUES
    (1, 'Voir Vue Globale',       'Accès au dashboard vue globale (admin)', 1),
    (2, 'Voir Dashboard Ventes',  'Accès au dashboard des ventes',         2),
    (3, 'Voir Dashboard Achats',  'Accès au dashboard des achats',         3);

-- ── 4. Role ↔ Privilege Assignments ─────────────────────────────────────────
-- Admin gets ALL privileges
INSERT INTO role_privileges (role_id, privilege_id) VALUES
    (1, 1),   -- admin  → Vue Globale
    (1, 2),   -- admin  → Ventes
    (1, 3);   -- admin  → Achats

-- Directeur Vente gets ventes only
INSERT INTO role_privileges (role_id, privilege_id) VALUES
    (2, 2);   -- directeur_vente → Ventes

-- Directeur Achat gets achats only
INSERT INTO role_privileges (role_id, privilege_id) VALUES
    (3, 3);   -- directeur_achat → Achats

-- ── 5. Default Users ────────────────────────────────────────────────────────
-- Passwords are bcrypt-hashed.
-- admin123   → $2b$12$LJ3m4ys3GZxkGJXkYL9MNOxPWqGy7KVzYvKtVGqM3HqNnLRtICxXy
-- vente123   → $2b$12$8zS1VHiXVH7bZpZ3YhX6ZOKjZ9aQfZ3YhX6ZOKjZ9aQfZ3YhX6ZOK
-- achat123   → $2b$12$rQzV5qJ8KVzYvKtVGqM3HqNnLRtICxXyLJ3m4ys3GZxkGJXkYL9MNO
--
-- NOTE: The Python init_db.py script generates proper bcrypt hashes at runtime.
--       The hashes below are placeholders. For production use, run init_db.py
--       which will generate real bcrypt hashes.
--       OR use the Python helper script below to generate hashes.
-- =============================================================================

INSERT INTO users (email, password_hash, first_name, last_name, role_id, is_active) VALUES
    ('ramichatti14@gmail.com',  '$2b$12$gsTdmErUZgDOomcxEAosI.zpON45EBZd6lG2/seGQwuBsNVWjqe82',  'Rami',   'Chatti',   1, TRUE),
    ('chattir318@gmail.com',   '$2b$12$gsTdmErUZgDOomcxEAosI.zpON45EBZd6lG2/seGQwuBsNVWjqe82',  'Chatti', 'Rami',     2, TRUE),
    ('achat@sougui.com',       '$2b$12$gsTdmErUZgDOomcxEAosI.zpON45EBZd6lG2/seGQwuBsNVWjqe82',  'Fatima', 'Trabelsi', 3, TRUE);

-- NOTE: All 3 users above use password "admin123".
-- To generate a different hash, run:
--   python -c "import bcrypt; print(bcrypt.hashpw(b'YOUR_PASSWORD', bcrypt.gensalt()).decode())"


-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Show all roles with privilege count
SELECT
    r.id, r.name, r.is_admin, r.is_system,
    COUNT(rp.privilege_id) AS privilege_count
FROM roles r
LEFT JOIN role_privileges rp ON r.id = rp.role_id
GROUP BY r.id;

-- Show all privileges with their dashboards
SELECT
    p.id, p.name AS privilege_name,
    d.dashboard_name, d.is_active AS dashboard_active
FROM privileges p
LEFT JOIN powerbi_dashboards d ON p.dashboard_id = d.id;

-- Show role → privilege → dashboard mapping
SELECT
    r.name AS role_name,
    p.name AS privilege_name,
    d.dashboard_name
FROM roles r
JOIN role_privileges rp ON r.id = rp.role_id
JOIN privileges p ON rp.privilege_id = p.id
LEFT JOIN powerbi_dashboards d ON p.dashboard_id = d.id
ORDER BY r.name, p.name;
