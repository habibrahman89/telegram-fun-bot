from services.database import get_connection


def add_db_queue(chat_id, query):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT MAX(position) FROM queues WHERE chat_id = ?
    """, (chat_id,))

    max_pos = cur.fetchone()[0]
    pos = (max_pos or 0) + 1

    cur.execute("""
        INSERT INTO queues (chat_id, query, position)
        VALUES (?, ?, ?)
    """, (chat_id, query, pos))

    conn.commit()
    conn.close()


def pop_db_queue(chat_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, query FROM queues
        WHERE chat_id = ?
        ORDER BY position ASC
        LIMIT 1
    """, (chat_id,))

    row = cur.fetchone()

    if not row:
        conn.close()
        return None

    q_id, query = row

    cur.execute("DELETE FROM queues WHERE id = ?", (q_id,))
    conn.commit()
    conn.close()

    return query


def list_db_queue(chat_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT query FROM queues
        WHERE chat_id = ?
        ORDER BY position ASC
    """, (chat_id,))

    rows = cur.fetchall()
    conn.close()

    return [r[0] for r in rows]


def clear_db_queue(chat_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM queues WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()