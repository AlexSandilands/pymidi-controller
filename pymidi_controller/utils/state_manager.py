import sqlite3
from pymidi_controller.utils.config_manager import CFG_DIR, ensure_config_dir

# Ensure config dir exists
ensure_config_dir()

# Path to our SQLite database
DB_FILE = CFG_DIR / "state.db"

# Initialize the database and create tables if they don't exist
def _get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS group_colors (
            group_name TEXT PRIMARY KEY,
            last_color TEXT
        )
        '''
    )
    conn.commit()
    return conn


def get_last_color(group_name: str) -> str | None:
    """
    Retrieve the last color for a given group from the state DB.
    Returns None if not found.
    """
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT last_color FROM group_colors WHERE group_name = ?",
        (group_name,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def set_last_color(group_name: str, color: str) -> None:
    """
    Insert or update the last color for a given group in the state DB.
    """
    conn = _get_connection()
    conn.execute(
        "INSERT INTO group_colors (group_name, last_color) VALUES (?, ?) ON CONFLICT(group_name) DO UPDATE SET last_color=excluded.last_color",
        (group_name, color)
    )
    conn.commit()
    conn.close()
