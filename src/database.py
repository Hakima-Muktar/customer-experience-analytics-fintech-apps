"""
Database Module for Bank Reviews
Task 3: Store Cleaned Data in PostgreSQL

This module handles:
1. Database connection using credentials from .env
2. Table creation (banks, reviews)
3. Data insertion from processed CSV
4. Verification queries

Why PostgreSQL?
- Robust, production-ready database
- Supports complex queries and joins
- Industry standard for data engineering
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import create_engine, text, Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from datetime import datetime

from config import DATA_PATHS, BANK_NAMES, APP_IDS

# Load environment variables
load_dotenv()

# SQLAlchemy Base for ORM
Base = declarative_base()


class DatabaseManager:
    """
    Database Manager for PostgreSQL operations.
    
    Purpose:
    - Manage database connections
    - Create and manage tables
    - Insert and query data
    """

    def __init__(self):
        """
        Initialize database connection using .env credentials.
        
        Connection string format:
        postgresql://username:password@host:port/database
        """
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'bank_reviews')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        
        self.engine = None
        self.session = None
        
    def connect(self):
        """
        Establish connection to PostgreSQL database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create connection string
            connection_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            
            print(f"Connecting to PostgreSQL database '{self.database}'...")
            
            # Create engine
            self.engine = create_engine(connection_string, echo=False)
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"Connected successfully!")
                print(f"PostgreSQL version: {version[:50]}...")
            
            # Create session
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            return True
            
        except SQLAlchemyError as e:
            print(f"Connection failed: {str(e)}")
            return False
    
    def create_tables(self):
        """
        Create the database schema (banks and reviews tables).
        
        Schema Design:
        
        banks table:
        - bank_id (PRIMARY KEY): Unique identifier
        - bank_code: Short code (CBE, BOA, Dashen)
        - bank_name: Full name
        - app_id: Google Play Store app ID
        
        reviews table:
        - review_id (PRIMARY KEY): Unique identifier
        - bank_id (FOREIGN KEY): References banks.bank_id
        - review_text: The actual review content
        - rating: 1-5 stars
        - review_date: Date of review
        - sentiment_label: POSITIVE/NEGATIVE/NEUTRAL
        - sentiment_score: Confidence score (0-1)
        - themes: Identified themes (comma-separated)
        - primary_theme: Main theme
        - source: Data source (Google Play)
        """
        print("\nCreating database tables...")
        
        # SQL for creating banks table
        create_banks_sql = """
        CREATE TABLE IF NOT EXISTS banks (
            bank_id SERIAL PRIMARY KEY,
            bank_code VARCHAR(20) UNIQUE NOT NULL,
            bank_name VARCHAR(100) NOT NULL,
            app_id VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # SQL for creating reviews table
        create_reviews_sql = """
        CREATE TABLE IF NOT EXISTS reviews (
            review_id SERIAL PRIMARY KEY,
            bank_id INTEGER REFERENCES banks(bank_id),
            review_text TEXT,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            review_date DATE,
            sentiment_label_vader VARCHAR(20),
            sentiment_score_vader FLOAT,
            sentiment_label_distilbert VARCHAR(20),
            sentiment_score_distilbert FLOAT,
            themes TEXT,
            primary_theme VARCHAR(100),
            source VARCHAR(50) DEFAULT 'Google Play',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            with self.engine.connect() as conn:
                # Create banks table
                conn.execute(text(create_banks_sql))
                print("  ✓ Created 'banks' table")
                
                # Create reviews table
                conn.execute(text(create_reviews_sql))
                print("  ✓ Created 'reviews' table")
                
                conn.commit()
            
            print("\nTables created successfully!")
            return True
            
        except SQLAlchemyError as e:
            print(f"Error creating tables: {str(e)}")
            return False
    
    def insert_banks(self):
        """
        Insert bank information into the banks table.
        
        Uses BANK_NAMES and APP_IDS from config.py
        """
        print("\nInserting bank data...")
        
        insert_sql = """
        INSERT INTO banks (bank_code, bank_name, app_id)
        VALUES (:code, :name, :app_id)
        ON CONFLICT (bank_code) DO UPDATE SET
            bank_name = EXCLUDED.bank_name,
            app_id = EXCLUDED.app_id;
        """
        
        try:
            with self.engine.connect() as conn:
                for code, name in BANK_NAMES.items():
                    app_id = APP_IDS.get(code, '')
                    conn.execute(text(insert_sql), {
                        'code': code,
                        'name': name,
                        'app_id': app_id
                    })
                    print(f"  ✓ Inserted: {name}")
                
                conn.commit()
            
            return True
            
        except SQLAlchemyError as e:
            print(f"Error inserting banks: {str(e)}")
            return False
    
    def get_bank_id_mapping(self):
        """
        Get mapping of bank names to bank IDs.
        
        Returns:
            dict: {bank_name: bank_id}
        """
        query = "SELECT bank_id, bank_name FROM banks;"
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                mapping = {row[1]: row[0] for row in result}
                return mapping
        except SQLAlchemyError as e:
            print(f"Error getting bank mapping: {str(e)}")
            return {}
    
    def insert_reviews(self, csv_path=None):
        """
        Insert reviews from CSV file into the reviews table.
        
        Args:
            csv_path (str): Path to CSV file with processed reviews
            
        Expected CSV columns:
        - review_text, rating, review_date, bank_name
        - sentiment_label_vader, sentiment_score_vader (optional)
        - sentiment_label_distilbert, sentiment_score_distilbert (optional)
        - themes, primary_theme (optional)
        """
        csv_path = csv_path or 'data/processed/reviews_with_sentiment_themes.csv'
        
        # Try alternative path if main doesn't exist
        if not os.path.exists(csv_path):
            csv_path = DATA_PATHS.get('final_results', 'data/processed/reviews_processed.csv')
        
        if not os.path.exists(csv_path):
            csv_path = 'data/processed/reviews_processed.csv'
            
        print(f"\nLoading reviews from {csv_path}...")
        
        try:
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} reviews")
        except FileNotFoundError:
            print(f"Error: File not found at {csv_path}")
            print("Please run Task 2 notebook first to generate the file.")
            return False
        
        # Get bank ID mapping
        bank_mapping = self.get_bank_id_mapping()
        if not bank_mapping:
            print("Error: No banks found in database. Run insert_banks() first.")
            return False
        
        print(f"\nBank ID mapping: {bank_mapping}")
        
        # Prepare insert statement
        insert_sql = """
        INSERT INTO reviews (
            bank_id, review_text, rating, review_date,
            sentiment_label_vader, sentiment_score_vader,
            sentiment_label_distilbert, sentiment_score_distilbert,
            themes, primary_theme, source
        ) VALUES (
            :bank_id, :review_text, :rating, :review_date,
            :sentiment_label_vader, :sentiment_score_vader,
            :sentiment_label_distilbert, :sentiment_score_distilbert,
            :themes, :primary_theme, :source
        );
        """
        
        print(f"\nInserting {len(df)} reviews into database...")
        
        inserted = 0
        errors = 0
        
        try:
            with self.engine.connect() as conn:
                for idx, row in df.iterrows():
                    try:
                        # Get bank_id from bank_name
                        bank_name = row.get('bank_name', '')
                        bank_id = bank_mapping.get(bank_name)
                        
                        if not bank_id:
                            # Try to find by partial match
                            for name, bid in bank_mapping.items():
                                if bank_name in name or name in bank_name:
                                    bank_id = bid
                                    break
                        
                        if not bank_id:
                            errors += 1
                            continue
                        
                        # Parse date
                        review_date = None
                        if 'review_date' in row and pd.notna(row['review_date']):
                            try:
                                review_date = pd.to_datetime(row['review_date']).date()
                            except:
                                review_date = None
                        
                        # Convert themes list to string if needed
                        themes = row.get('themes', '')
                        if isinstance(themes, list):
                            themes = ', '.join(themes)
                        
                        # Prepare data
                        data = {
                            'bank_id': bank_id,
                            'review_text': str(row.get('review_text', ''))[:5000],  # Limit length
                            'rating': int(row.get('rating', 0)) if pd.notna(row.get('rating')) else None,
                            'review_date': review_date,
                            'sentiment_label_vader': row.get('sentiment_label_vader', None),
                            'sentiment_score_vader': float(row.get('sentiment_score_vader', 0)) if pd.notna(row.get('sentiment_score_vader')) else None,
                            'sentiment_label_distilbert': row.get('sentiment_label_distilbert', None),
                            'sentiment_score_distilbert': float(row.get('sentiment_score_distilbert', 0)) if pd.notna(row.get('sentiment_score_distilbert')) else None,
                            'themes': str(themes) if pd.notna(themes) else None,
                            'primary_theme': row.get('primary_theme', None),
                            'source': row.get('source', 'Google Play')
                        }
                        
                        conn.execute(text(insert_sql), data)
                        inserted += 1
                        
                        # Progress update
                        if inserted % 200 == 0:
                            print(f"  Inserted {inserted} reviews...")
                        
                    except Exception as e:
                        errors += 1
                        if errors <= 5:
                            print(f"  Error on row {idx}: {str(e)[:50]}")
                
                conn.commit()
            
            print(f"\n✓ Successfully inserted {inserted} reviews")
            if errors > 0:
                print(f"✗ Failed to insert {errors} reviews")
            
            return True
            
        except SQLAlchemyError as e:
            print(f"Database error: {str(e)}")
            return False
    
    def verify_data(self):
        """
        Run verification queries to check data integrity.
        
        Queries:
        1. Total reviews count
        2. Reviews per bank
        3. Average rating per bank
        4. Sentiment distribution
        """
        print("\n" + "=" * 60)
        print("DATA VERIFICATION QUERIES")
        print("=" * 60)
        
        queries = {
            "Total Reviews": "SELECT COUNT(*) FROM reviews;",
            "Reviews per Bank": """
                SELECT b.bank_name, COUNT(r.review_id) as review_count
                FROM banks b
                LEFT JOIN reviews r ON b.bank_id = r.bank_id
                GROUP BY b.bank_name
                ORDER BY review_count DESC;
            """,
            "Average Rating per Bank": """
                SELECT b.bank_name, ROUND(AVG(r.rating)::numeric, 2) as avg_rating
                FROM banks b
                JOIN reviews r ON b.bank_id = r.bank_id
                GROUP BY b.bank_name
                ORDER BY avg_rating DESC;
            """,
            "Sentiment Distribution (DistilBERT)": """
                SELECT sentiment_label_distilbert, COUNT(*) as count
                FROM reviews
                WHERE sentiment_label_distilbert IS NOT NULL
                GROUP BY sentiment_label_distilbert
                ORDER BY count DESC;
            """,
            "Top Themes": """
                SELECT primary_theme, COUNT(*) as count
                FROM reviews
                WHERE primary_theme IS NOT NULL AND primary_theme != 'Other'
                GROUP BY primary_theme
                ORDER BY count DESC
                LIMIT 5;
            """
        }
        
        try:
            with self.engine.connect() as conn:
                for name, query in queries.items():
                    print(f"\n{name}:")
                    print("-" * 40)
                    result = conn.execute(text(query))
                    rows = result.fetchall()
                    
                    if len(rows) == 1 and len(rows[0]) == 1:
                        print(f"  {rows[0][0]}")
                    else:
                        for row in rows:
                            print(f"  {row}")
            
            return True
            
        except SQLAlchemyError as e:
            print(f"Error running queries: {str(e)}")
            return False
    
    def export_schema(self, output_path='schema.sql'):
        """
        Export the database schema to a SQL file.
        
        Args:
            output_path (str): Path to save the schema file
        """
        schema_sql = """
-- Bank Reviews Database Schema
-- Created for Customer Experience Analytics Project

-- Banks Table
-- Stores information about the three Ethiopian banks
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_code VARCHAR(20) UNIQUE NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    app_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews Table
-- Stores scraped reviews with sentiment and theme analysis
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER REFERENCES banks(bank_id),
    review_text TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_date DATE,
    sentiment_label_vader VARCHAR(20),
    sentiment_score_vader FLOAT,
    sentiment_label_distilbert VARCHAR(20),
    sentiment_score_distilbert FLOAT,
    themes TEXT,
    primary_theme VARCHAR(100),
    source VARCHAR(50) DEFAULT 'Google Play',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment_label_distilbert);
CREATE INDEX IF NOT EXISTS idx_reviews_theme ON reviews(primary_theme);

-- Sample Queries

-- Count reviews per bank
-- SELECT b.bank_name, COUNT(r.review_id) as review_count
-- FROM banks b
-- LEFT JOIN reviews r ON b.bank_id = r.bank_id
-- GROUP BY b.bank_name;

-- Average rating per bank
-- SELECT b.bank_name, ROUND(AVG(r.rating)::numeric, 2) as avg_rating
-- FROM banks b
-- JOIN reviews r ON b.bank_id = r.bank_id
-- GROUP BY b.bank_name;

-- Sentiment distribution
-- SELECT sentiment_label_distilbert, COUNT(*) as count
-- FROM reviews
-- GROUP BY sentiment_label_distilbert;
"""
        
        try:
            with open(output_path, 'w') as f:
                f.write(schema_sql)
            print(f"\nSchema exported to {output_path}")
            return True
        except Exception as e:
            print(f"Error exporting schema: {str(e)}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
        print("\nDatabase connection closed.")


def setup_database():
    """
    Main function to set up the database and insert data.
    
    Pipeline:
    1. Connect to PostgreSQL
    2. Create tables
    3. Insert bank information
    4. Insert reviews from CSV
    5. Verify data
    6. Export schema
    """
    print("=" * 60)
    print("DATABASE SETUP PIPELINE")
    print("=" * 60)
    
    db = DatabaseManager()
    
    # Step 1: Connect
    print("\n[1/6] Connecting to database...")
    if not db.connect():
        return None
    
    # Step 2: Create tables
    print("\n[2/6] Creating tables...")
    if not db.create_tables():
        db.close()
        return None
    
    # Step 3: Insert banks
    print("\n[3/6] Inserting bank data...")
    if not db.insert_banks():
        db.close()
        return None
    
    # Step 4: Insert reviews
    print("\n[4/6] Inserting reviews...")
    if not db.insert_reviews():
        db.close()
        return None
    
    # Step 5: Verify
    print("\n[5/6] Verifying data...")
    db.verify_data()
    
    # Step 6: Export schema
    print("\n[6/6] Exporting schema...")
    db.export_schema('schema.sql')
    
    print("\n" + "=" * 60)
    print("✓ DATABASE SETUP COMPLETE!")
    print("=" * 60)
    
    return db


if __name__ == "__main__":
    db = setup_database()
    if db:
        db.close()