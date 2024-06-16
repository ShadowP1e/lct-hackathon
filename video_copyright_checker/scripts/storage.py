import uuid
import sqlite3
from collections import defaultdict
from contextlib import contextmanager
from . import settings


@contextmanager
def get_cursor():
    """Соединяемся с БД

    :returns: (connection, cursor)
    """
    try:
        conn = sqlite3.connect(settings.DB_PATH, timeout=30)
        yield conn, conn.cursor()
    finally:
        conn.close()


def setup_db():
    """
    Инициализируем БД и таблицы в ней

    """
    with get_cursor() as (conn, c):
        c.execute("CREATE TABLE IF NOT EXISTS hash (hash int, offset real, offset_b real, video_id text)")
        c.execute("CREATE TABLE IF NOT EXISTS video_info (title text, video_id text)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_hash ON hash (hash)")
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA wal_autocheckpoint=300")


def checkpoint_db():
    with get_cursor() as (conn, c):
        c.execute("PRAGMA wal_checkpoint(FULL)")


def video_in_db(filename):
    """Добавили ли уже лицензионное видео

    :param filename: Путь к видео
    :returns: True/False
    """
    with get_cursor() as (conn, c):
        video_id = str(uuid.uuid5(uuid.NAMESPACE_OID, filename).int)
        c.execute("SELECT * FROM video_info WHERE video_id=?", (video_id,))
        return c.fetchone() is not None


def store_video(hashes, video_info):
    """Сохраняем видео в базу данных

    :param hashes: List of tuples (hash, time offset for 1st peak, time offset for 2nd peak, video_id)
    :param video_info: Информация о видео
    """

    if len(hashes) < 1:
        return
    with get_cursor() as (conn, c):
        c.executemany("INSERT INTO hash VALUES (?, ?, ?, ?)", hashes)
        insert_info = video_info
        c.execute("INSERT INTO video_info VALUES (?, ?)", (insert_info, hashes[0][3]))
        conn.commit()


def get_matches(hashes):
    """Получаем совпадения хэшей с лицензионными видео

    :param hashes: Список хэшей
    :returns: Dict {video_id: (start_time_licence, start_time_piracy, end_time_piracy)}
    """
    h_dict = {}
    for h, t, end_time, _ in hashes:
        h_dict[h] = (t, end_time)
    in_values = f"({','.join([str(h[0]) for h in hashes])})"
    with get_cursor() as (conn, c):
        c.execute(f"SELECT hash, offset, offset_b, video_id FROM hash WHERE hash IN {in_values}")
        results = c.fetchall()
    result_dict = defaultdict(list)
    for r in results:
        result_dict[r[3]].append((r[1], h_dict[r[0]][0], h_dict[r[0]][1])) # start_time_licence, start_time_piracy, end_time_piracy
    return result_dict


def get_info_for_video_id(video_id):
    """Получаем информацию о видео из БД по video_id
    :param video_id: ID видео
    """

    with get_cursor() as (conn, c):
        c.execute("SELECT title FROM video_info WHERE video_id = ?", (video_id,))
        return c.fetchone()
