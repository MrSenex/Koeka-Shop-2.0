"""
Database connection manager for Tembie's Spaza Shop POS System
Handles SQLite database setup, connections, and initialization
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Optional

class DatabaseManager:
    """Manages SQLite database connections and initialization"""
    
    def __init__(self, db_path: str = "spaza_shop.db"):
        """Initialize database manager with database path"""
        self.db_path = db_path
        self.schema_path = Path(__file__).parent / "base_schema.sql"
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database and tables if they don't exist"""
        if not os.path.exists(self.db_path):
            self._create_database()
        
        # Always ensure schema is up to date
        self._initialize_schema()
    
    def _create_database(self):
        """Create new database file"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.close()
            print(f"Database created: {self.db_path}")
        except sqlite3.Error as e:
            raise Exception(f"Failed to create database: {e}")
    
    def _initialize_schema(self):
        """Initialize database schema from SQL file"""
        try:
            with open(self.schema_path, 'r') as schema_file:
                schema_sql = schema_file.read()
            
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
                conn.commit()
                print("Database schema initialized successfully")
        except FileNotFoundError:
            raise Exception(f"Schema file not found: {self.schema_path}")
        except sqlite3.Error as e:
            raise Exception(f"Failed to initialize schema: {e}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise Exception(f"Database error: {e}")
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """Execute SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
    
    def get_last_insert_id(self, query: str, params: tuple = None) -> int:
        """Execute INSERT query and return the new row ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.lastrowid

# Global database manager instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager
