import pymysql
import sys

def create_database():
    """Create the sougui_db database in MySQL"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',  # Default XAMPP password is empty
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Connexion à MySQL réussie!")
        
        with connection.cursor() as cursor:
            # Create database if not exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS sougui_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ Base de données 'sougui_db' créée avec succès!")
            
            # Use the database
            cursor.execute("USE sougui_db")
            
            # Create users table
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Table 'users' créée!")
            
            # Create powerbi_dashboards table
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Table 'powerbi_dashboards' créée!")
            
        connection.commit()
        connection.close()
        
        print("\n" + "="*50)
        print("✅ Base de données configurée avec succès!")
        print("="*50)
        print("\nProchaine étape: Exécutez 'python init_db.py' pour créer les utilisateurs par défaut")
        
        return True
        
    except pymysql.Error as e:
        print(f"\n❌ Erreur MySQL: {e}")
        print("\n⚠️  Assurez-vous que:")
        print("   1. XAMPP est démarré")
        print("   2. MySQL est en cours d'exécution")
        print("   3. Le port 3306 est disponible")
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

if __name__ == '__main__':
    success = create_database()
    sys.exit(0 if success else 1)
