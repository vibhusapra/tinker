import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import os

class Database:
    def __init__(self, db_path: str = "learning_copilot.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_content TEXT,
                    curriculum_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    path_id INTEGER NOT NULL,
                    module_id TEXT NOT NULL,
                    status TEXT DEFAULT 'not_started',
                    projects_completed TEXT,
                    notes TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (path_id) REFERENCES learning_paths (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    path_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (path_id) REFERENCES learning_paths (id)
                )
            ''')
            
            conn.commit()
    
    def create_user(self, username: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (username) VALUES (?)",
                    (username,)
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                cursor.execute(
                    "SELECT id FROM users WHERE username = ?",
                    (username,)
                )
                return cursor.fetchone()[0]
    
    def create_learning_path(
        self,
        user_id: int,
        title: str,
        source_type: str,
        source_content: str,
        curriculum: Dict[str, Any]
    ) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO learning_paths 
                   (user_id, title, source_type, source_content, curriculum_json)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, title, source_type, source_content, json.dumps(curriculum))
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_learning_paths(self, user_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM learning_paths 
                   WHERE user_id = ? 
                   ORDER BY created_at DESC''',
                (user_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_learning_path(self, path_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM learning_paths WHERE id = ?",
                (path_id,)
            )
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['curriculum'] = json.loads(result['curriculum_json'])
                return result
            return None
    
    def update_progress(
        self,
        user_id: int,
        path_id: int,
        module_id: str,
        status: str,
        projects_completed: Optional[List[str]] = None,
        notes: Optional[str] = None
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                '''SELECT id FROM progress 
                   WHERE user_id = ? AND path_id = ? AND module_id = ?''',
                (user_id, path_id, module_id)
            )
            existing = cursor.fetchone()
            
            projects_json = json.dumps(projects_completed) if projects_completed else None
            
            if existing:
                cursor.execute(
                    '''UPDATE progress 
                       SET status = ?, projects_completed = ?, notes = ?, 
                           updated_at = CURRENT_TIMESTAMP
                       WHERE id = ?''',
                    (status, projects_json, notes, existing[0])
                )
            else:
                cursor.execute(
                    '''INSERT INTO progress 
                       (user_id, path_id, module_id, status, projects_completed, notes)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (user_id, path_id, module_id, status, projects_json, notes)
                )
            
            conn.commit()
    
    def get_progress(self, user_id: int, path_id: int) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM progress 
                   WHERE user_id = ? AND path_id = ?
                   ORDER BY updated_at DESC''',
                (user_id, path_id)
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                if result['projects_completed']:
                    result['projects_completed'] = json.loads(result['projects_completed'])
                results.append(result)
            return results
    
    def add_chat_message(
        self,
        user_id: int,
        path_id: int,
        role: str,
        content: str
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO chat_history (user_id, path_id, role, content)
                   VALUES (?, ?, ?, ?)''',
                (user_id, path_id, role, content)
            )
            conn.commit()
    
    def get_chat_history(
        self,
        user_id: int,
        path_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM chat_history 
                   WHERE user_id = ? AND path_id = ?
                   ORDER BY timestamp DESC
                   LIMIT ?''',
                (user_id, path_id, limit)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]