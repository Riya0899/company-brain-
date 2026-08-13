import sqlite3

DB_PATH = "company_brain.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        source_name TEXT UNIQUE,
        chunk_count INTEGER,
        summary TEXT,
        indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS topics (
        cluster_id INTEGER PRIMARY KEY,
        name TEXT
    );
    CREATE TABLE IF NOT EXISTS query_history (
        id INTEGER PRIMARY KEY,
        question TEXT,
        score REAL,
        faithfulness REAL,
        relevancy REAL,
        topic TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY,
        question TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS chat_memory (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        summary TEXT DEFAULT '',
        summarized_count INTEGER DEFAULT 0
    );

    """)
    conn.commit()
    conn.close()

def add_document(source_name, chunk_count, summary):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO documents (source_name, chunk_count, summary) VALUES (?, ?, ?)",
        (source_name, chunk_count, summary),
    )
    conn.commit()
    conn.close()

def list_documents():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM documents").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_topics(topic_names: dict):
    conn = get_conn()
    for cid, name in topic_names.items():
        conn.execute("INSERT OR REPLACE INTO topics (cluster_id, name) VALUES (?, ?)", (cid, name))
    conn.commit()
    conn.close()

def list_topics():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM topics").fetchall()
    conn.close()
    return {r["cluster_id"]: r["name"] for r in rows}

def add_query(question, score, faithfulness, relevancy, topic):
    conn = get_conn()
    conn.execute(
        "INSERT INTO query_history (question, score, faithfulness, relevancy, topic) VALUES (?, ?, ?, ?, ?)",
        (question, score, faithfulness, relevancy, topic),
    )
    conn.commit()
    conn.close()

def list_queries():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM query_history ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_gap(question):
    conn = get_conn()
    conn.execute("INSERT INTO knowledge_gaps (question) VALUES (?)", (question,))
    conn.commit()
    conn.close()

def list_gaps():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM knowledge_gaps ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_suggestion(question):
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO suggestions (question) VALUES (?)", (question,))
    conn.commit()
    conn.close()

def list_suggestions():
    conn = get_conn()
    rows = conn.execute("SELECT question FROM suggestions ORDER BY id DESC LIMIT 20").fetchall()
    conn.close()
    return [r["question"] for r in rows]

def get_chat_memory():
    conn = get_conn()
    row = conn.execute("SELECT * FROM chat_memory WHERE id = 1").fetchone()
    conn.close()
    if row is None:
        return {"summary": "", "summarized_count": 0}
    return {"summary": row["summary"] or "", "summarized_count": row["summarized_count"] or 0}

def save_chat_memory(summary: str, summarized_count: int):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO chat_memory (id, summary, summarized_count) VALUES (1, ?, ?)",
        (summary, summarized_count),
    )
    conn.commit()
    conn.close()

def reset_chat_memory():
    conn = get_conn()
    conn.execute("DELETE FROM chat_memory WHERE id = 1")
    conn.commit()
    conn.close()