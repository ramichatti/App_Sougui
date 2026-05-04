"""
Script pour vérifier la structure de toutes les tables nécessaires
"""
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

SQL_SERVER = os.getenv('DWH_SERVER', 'localhost,1433')
SQL_DATABASE = os.getenv('DWH_DATABASE', 'Sougui_DWH')
SQL_USER = os.getenv('DWH_USER', 'sa')
SQL_PASSWORD = os.getenv('DWH_PASSWORD', 'admin')

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    f"UID={SQL_USER};"
    f"PWD={SQL_PASSWORD};"
    f"TrustServerCertificate=yes;"
)

print("=" * 70)
print("STRUCTURE DE TOUTES LES TABLES NÉCESSAIRES")
print("=" * 70)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    tables_to_check = ['Dim_Client', 'Fact_Vente_B2C', 'Dim_Date']
    
    for table_name in tables_to_check:
        print(f"\n--- Table: {table_name} ---")
        
        # Structure de la table
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """)
        columns = cursor.fetchall()
        
        print(f"Colonnes ({len(columns)}):")
        for col_name, data_type, max_length, nullable in columns:
            length_info = f"({max_length})" if max_length else ""
            print(f"  - {col_name}: {data_type}{length_info} {'NULL' if nullable == 'YES' else 'NOT NULL'}")
        
        # Exemple de données
        print(f"\nExemple de données (2 premières lignes):")
        cursor.execute(f"SELECT TOP 2 * FROM dbo.{table_name}")
        rows = cursor.fetchall()
        if rows:
            col_names = [desc[0] for desc in cursor.description]
            print(f"  Colonnes: {', '.join(col_names)}")
            for i, row in enumerate(rows, 1):
                print(f"  Ligne {i}: {row}")
        else:
            print("  Aucune donnée trouvée")
    
    # Test de jointure simple
    print("\n" + "=" * 70)
    print("TEST DE JOINTURE SIMPLE")
    print("=" * 70)
    
    simple_join_query = """
        SELECT TOP 3
            c.Client_Key,
            c.Nom,
            c.Prenom,
            f.Numero_de_commande,
            f.Montant_total_de_la_commande,
            f.Quantite____Remboursement,
            f.Date_Key
        FROM dbo.Dim_Client c
        INNER JOIN dbo.Fact_Vente_B2C f ON c.Client_Key = f.Client_Key
        WHERE f.Numero_de_commande IS NOT NULL
    """
    
    print("\nExécution de la jointure simple...")
    cursor.execute(simple_join_query)
    join_results = cursor.fetchall()
    
    print(f"✅ Jointure réussie! {len(join_results)} lignes trouvées")
    for row in join_results:
        print(f"  Client {row[0]}: {row[1]} {row[2]} - Commande {row[3]} - Montant {row[4]} - Qté {row[5]} - Date_Key {row[6]}")
    
    # Test sans Dim_Date pour l'instant
    print("\n" + "=" * 70)
    print("TEST SEGMENTATION SANS DIM_DATE")
    print("=" * 70)
    
    segmentation_query = """
        SELECT TOP 3
            c.Client_Key,
            c.Nom,
            c.Prenom,
            -- Fréquence: nombre de commandes distinctes
            COUNT(DISTINCT f.Numero_de_commande) AS Frequency,
            -- Montant total dépensé
            COALESCE(SUM(f.Montant_total_de_la_commande), 0) AS Monetary,
            -- Panier moyen
            CASE 
                WHEN COUNT(DISTINCT f.Numero_de_commande) > 0 
                THEN COALESCE(SUM(f.Montant_total_de_la_commande), 0) / COUNT(DISTINCT f.Numero_de_commande)
                ELSE 0 
            END AS Panier_Moyen,
            -- Quantité totale (en tenant compte des remboursements)
            COALESCE(SUM(f.Quantite____Remboursement), 0) AS Quantite_Totale,
            -- Taux de réduction
            CASE 
                WHEN SUM(f.Montant_total_de_la_commande) > 0 
                THEN COALESCE(SUM(f.Reduction), 0) / SUM(f.Montant_total_de_la_commande)
                ELSE 0 
            END AS Taux_Reduction,
            -- Produits par commande
            CASE 
                WHEN COUNT(DISTINCT f.Numero_de_commande) > 0 
                THEN CAST(SUM(f.Quantite____Remboursement) AS FLOAT) / COUNT(DISTINCT f.Numero_de_commande)
                ELSE 0 
            END AS Produits_Par_Commande
        FROM dbo.Dim_Client c
        INNER JOIN dbo.Fact_Vente_B2C f ON c.Client_Key = f.Client_Key
        WHERE f.Numero_de_commande IS NOT NULL
        GROUP BY c.Client_Key, c.Nom, c.Prenom
        HAVING COUNT(DISTINCT f.Numero_de_commande) > 0
    """
    
    print("\nExécution de la requête de segmentation...")
    cursor.execute(segmentation_query)
    seg_results = cursor.fetchall()
    
    print(f"✅ Segmentation réussie! {len(seg_results)} clients trouvés")
    for row in seg_results:
        print(f"\nClient {row[0]}: {row[1]} {row[2]}")
        print(f"  Frequency: {row[3]} commandes")
        print(f"  Monetary: {row[4]:.2f} TND")
        print(f"  Panier Moyen: {row[5]:.2f} TND")
        print(f"  Quantité Totale: {row[6]}")
        print(f"  Taux Réduction: {row[7]:.4f}")
        print(f"  Produits/Commande: {row[8]:.2f}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Tests terminés avec succès!")
    
except pyodbc.Error as e:
    print(f"\n❌ Erreur SQL: {str(e)}")
except Exception as e:
    print(f"\n❌ Erreur: {str(e)}")
    import traceback
    traceback.print_exc()