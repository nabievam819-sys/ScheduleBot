import sqlite3


DB_NAME = "schedule.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            subject TEXT NOT NULL,
            time TEXT NOT NULL,
            room TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_lesson(day, subject, time, room):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO schedule (day, subject, time, room)
        VALUES (?, ?, ?, ?)
        """,
        (day, subject, time, room)
    )

    conn.commit()
    conn.close()


def get_all_lessons():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, day, subject, time, room
        FROM schedule
        ORDER BY
            CASE day
                WHEN 'Понедельник' THEN 1
                WHEN 'Вторник' THEN 2
                WHEN 'Среда' THEN 3
                WHEN 'Четверг' THEN 4
                WHEN 'Пятница' THEN 5
                WHEN 'Суббота' THEN 6
                WHEN 'Воскресенье' THEN 7
            END,
            time
    """)

    lessons = cursor.fetchall()

    conn.close()

    return lessons


def get_lessons_by_day(day):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, day, subject, time, room
        FROM schedule
        WHERE day = ?
        ORDER BY time
        """,
        (day,)
    )

    lessons = cursor.fetchall()

    conn.close()

    return lessons


def delete_lesson(lesson_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM schedule WHERE id = ?",
        (lesson_id,)
    )

    conn.commit()
    conn.close()
