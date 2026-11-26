import sqlite3
from typing import Optional

from db.models import Movie, Genre
from utils.constants import DB_PATH, DEFAULT_GENRES


class Database:
    # Класс для работы с базой данных SQLitе

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    # открытие соединения и создание таблиц, если их нет
    def connect(self) -> None:
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self._create_tables()
        self._fill_default_genres()

    # закрытие соединения
    def close(self) -> None:
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    # создание таблиц
    def _create_tables(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS genres (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                year        INTEGER,
                genre_id    INTEGER,
                rating      REAL,
                description TEXT,
                poster_path TEXT,
                FOREIGN KEY (genre_id) REFERENCES genres(id)
            )
        """)
        self.connection.commit()

    # если жанров нет - добавляются стандартные
    def _fill_default_genres(self) -> None:
        self.cursor.execute("SELECT COUNT(*) FROM genres")
        count = self.cursor.fetchone()[0]
        if count == 0:
            for genre_name in DEFAULT_GENRES:
                self.cursor.execute(
                    "INSERT INTO genres (name) VALUES (?)", (genre_name,)
                )
            self.connection.commit()

    # Жанры
    def get_all_genres(self) -> list[Genre]:
        self.cursor.execute("SELECT id, name FROM genres ORDER BY name")
        rows = self.cursor.fetchall()
        return [Genre(id=row["id"], name=row["name"]) for row in rows]

    def add_genre(self, name: str) -> int:
        self.cursor.execute("INSERT INTO genres (name) VALUES (?)", (name,))
        self.connection.commit()
        return self.cursor.lastrowid

    # Фильмы
    def get_all_movies(self) -> list[Movie]:
        self.cursor.execute(
            "SELECT id, title, year, genre_id, rating, description, poster_path "
            "FROM movies ORDER BY title"
        )
        return [self._row_to_movie(row) for row in self.cursor.fetchall()]

    def get_movies_filtered(
        self,
        search_text: str = "",
        genre_id: Optional[int] = None,
    ) -> list[Movie]:

        # поиск по названию и фильтр по жанру
        query = (
            "SELECT id, title, year, genre_id, rating, description, poster_path "
            "FROM movies WHERE 1=1"
        )
        params: list = []

        if search_text:
            query += " AND title LIKE ?"
            params.append(f"%{search_text}%")

        if genre_id is not None:
            query += " AND genre_id = ?"
            params.append(genre_id)

        query += " ORDER BY title"
        self.cursor.execute(query, params)
        return [self._row_to_movie(row) for row in self.cursor.fetchall()]

    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        self.cursor.execute(
            "SELECT id, title, year, genre_id, rating, description, poster_path "
            "FROM movies WHERE id = ?",
            (movie_id,),
        )
        row = self.cursor.fetchone()
        return self._row_to_movie(row) if row else None

    def add_movie(self, movie: Movie) -> int:
        self.cursor.execute(
            "INSERT INTO movies "
            "(title, year, genre_id, rating, description, poster_path) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                movie.title, movie.year, movie.genre_id,
                movie.rating, movie.description, movie.poster_path,
            ),
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def update_movie(self, movie: Movie) -> None:
        self.cursor.execute(
            "UPDATE movies SET title=?, year=?, genre_id=?, rating=?, "
            "description=?, poster_path=? WHERE id=?",
            (
                movie.title, movie.year, movie.genre_id,
                movie.rating, movie.description, movie.poster_path,
                movie.id,
            ),
        )
        self.connection.commit()

    def delete_movie(self, movie_id: int) -> None:
        self.cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        self.connection.commit()

    def _row_to_movie(self, row) -> Movie:
        return Movie(
            id=row["id"],
            title=row["title"],
            year=row["year"] or 0,
            genre_id=row["genre_id"] or 0,
            rating=row["rating"] or 0.0,
            description=row["description"] or "",
            poster_path=row["poster_path"] or "",
        )