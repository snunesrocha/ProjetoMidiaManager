import sqlite3
import logging
import os

class DatabaseService:
    def __init__(self, db_path: str = "database/midia_manager.db"):
        os.makedirs("database", exist_ok=True)
        self.db_path = db_path
        self.connection = None
        self._connect()
        self._create_tables()
        logging.info("DatabaseService initialized")

    def _connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            logging.info(f"Connected to SQLite database at {self.db_path}")
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")

    def _create_tables(self):
        try:
            cursor = self.connection.cursor()

            # Tabela de mídias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS media (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    hash TEXT NOT NULL UNIQUE,
                    folder TEXT NOT NULL
                )
            """)

            # Tabela de pessoas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS people (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    hash TEXT NOT NULL UNIQUE
                )
            """)

            # Tabela intermediária para vínculos pessoa-mídia
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS people_media (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_id INTEGER NOT NULL,
                    media_id INTEGER NOT NULL,
                    FOREIGN KEY(person_id) REFERENCES people(id),
                    FOREIGN KEY(media_id) REFERENCES media(id),
                    UNIQUE(person_id, media_id)
                )
            """)

            self.connection.commit()
            logging.info("Tables 'media', 'people' and 'people_media' ensured in database")
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")

    # ------------------------------------------------------------
    # Inserções básicas
    # ------------------------------------------------------------
    def insert_media_record(self, file_name: str, img_hash: str, folder: str):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO media (file_name, hash, folder)
                VALUES (?, ?, ?)
            """, (file_name, img_hash, folder))
            self.connection.commit()
            logging.info(f"Inserted media record: {file_name}")
        except sqlite3.Error as e:
            logging.error(f"Error inserting media record {file_name}: {e}")

    def insert_person_record(self, name: str, img_hash: str):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO people (name, hash)
                VALUES (?, ?)
            """, (name, img_hash))
            self.connection.commit()
            logging.info(f"Inserted person record: {name}")
        except sqlite3.Error as e:
            logging.error(f"Error inserting person record {name}: {e}")

    def get_person_by_hash(self, img_hash: str):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM people WHERE hash = ?", (img_hash,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except sqlite3.Error as e:
            logging.error(f"Error fetching person by hash {img_hash}: {e}")
            return None

    # ------------------------------------------------------------
    # Métodos auxiliares para vínculos pessoa-mídia
    # ------------------------------------------------------------
    def link_person_to_media(self, person_id: int, media_id: int):
        """Vincula uma pessoa a uma mídia"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO people_media (person_id, media_id)
                VALUES (?, ?)
            """, (person_id, media_id))
            self.connection.commit()
            logging.info(f"Linked person {person_id} to media {media_id}")
        except sqlite3.Error as e:
            logging.error(f"Error linking person {person_id} to media {media_id}: {e}")

    def unlink_person_from_media(self, link_id: int):
        """Remove vínculo entre pessoa e mídia"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM people_media WHERE id = ?", (link_id,))
            self.connection.commit()
            logging.info(f"Unlinked person-media relation {link_id}")
        except sqlite3.Error as e:
            logging.error(f"Error unlinking relation {link_id}: {e}")

    def get_media_by_person(self, person_id: int):
        """Retorna todas as mídias vinculadas a uma pessoa"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT m.id, m.file_name, m.folder, pm.id
                FROM people_media pm
                JOIN media m ON pm.media_id = m.id
                WHERE pm.person_id = ?
            """, (person_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error fetching media for person {person_id}: {e}")
            return []

    def close(self):
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed")
