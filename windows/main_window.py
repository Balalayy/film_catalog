import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QMenu
from PyQt6.QtGui import QPixmap, QShortcut, QKeySequence
from PyQt6.QtCore import Qt
from utils.constants import BASE_DIR
from windows.movie_dialog import MovieDialog


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()

        # Загрузка интерфейса
        uic.loadUi(os.path.join(BASE_DIR, "ui", "main_window.ui"), self)

        self.db = db
        self.selected_movie_id = None

        self.setup_ui()
        self.load_filters()
        self.load_movies()
        self.setup_shortcuts()

    def setup_ui(self):
        # Настройка режима выделения строк в таблице
        self.moviesTable.setSelectionBehavior(
            self.moviesTable.SelectionBehavior.SelectRows
        )
        self.moviesTable.setEditTriggers(
            self.moviesTable.EditTrigger.NoEditTriggers
        )

        # Привязка обработчиков к кнопкам интерфейса
        self.addBtn.clicked.connect(self.add_movie)
        self.editBtn.clicked.connect(self.edit_movie)
        self.deleteBtn.clicked.connect(self.delete_movie)

        # Привязка обработчиков к элементам поиска и фильтрации
        self.searchEdit.textChanged.connect(self.load_movies)
        self.genreFilterCombo.currentIndexChanged.connect(self.load_movies)

        # Обработка кликов мыши по таблице
        self.moviesTable.cellDoubleClicked.connect(self.on_double_click)
        self.moviesTable.cellClicked.connect(self.on_single_click)

        # Настройка контекстного меню (ПКМ)
        self.moviesTable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.moviesTable.customContextMenuRequested.connect(self.show_context_menu)

        # Обработка нажатий клавиатуры
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.add_movie)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.edit_movie)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.delete_movie)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(lambda: self.searchEdit.setFocus())
        QShortcut(QKeySequence("F1"), self).activated.connect(self.show_about)

    def setup_shortcuts(self):
        pass

    def keyPressEvent(self, event):
        # Обработка клавиши Esc
        if event.key() == Qt.Key.Key_Escape:
            self.searchEdit.clear()
            self.genreFilterCombo.setCurrentIndex(0)
        super().keyPressEvent(event)

    def load_filters(self):
        # Загрузка жанров в выпадающий список
        self.genreFilterCombo.clear()
        self.genreFilterCombo.addItem("Все жанры", None)
        for genre in self.db.get_all_genres():
            self.genreFilterCombo.addItem(genre.name, genre.id)

    def load_movies(self):
        if not hasattr(self, 'moviesTable'):
            print("ОШИБКА: таблица moviesTable не найдена!")
            return

        search_text = self.searchEdit.text().strip() if hasattr(self, 'searchEdit') else ""
        genre_id = self.genreFilterCombo.currentData() if hasattr(self, 'genreFilterCombo') else None

        # Отладка БД
        print(f"Загрузка таблицы")
        print(f"Поиск: '{search_text}', Жанр_ID: {genre_id}")

        movies = self.db.get_movies_filtered(search_text, genre_id)

        # Отладка: сколько фильмов пришло из базы
        print(f"Найдено фильмов в БД: {len(movies)}")

        self.moviesTable.setRowCount(0)
        for row_idx, movie in enumerate(movies):
            # Отладка: какие данные у первого фильма
            if row_idx == 0:
                print(f"Первый фильм: {movie}")

            self.moviesTable.insertRow(row_idx)
            self.moviesTable.setItem(row_idx, 0, QTableWidgetItem(movie.title))
            self.moviesTable.setItem(row_idx, 1, QTableWidgetItem(str(movie.year)))

            genre_name = ""
            for g in self.db.get_all_genres():
                if g.id == movie.genre_id:
                    genre_name = g.name
                    break
            self.moviesTable.setItem(row_idx, 2, QTableWidgetItem(genre_name))
            self.moviesTable.setItem(row_idx, 3, QTableWidgetItem(str(movie.rating)))

            self.moviesTable.item(row_idx, 0).setData(Qt.ItemDataRole.UserRole, movie.id)

        print("Таблица обновлена")

    def get_selected_movie_id(self):
        # Получение ID фильма, выделенного в таблице
        selected_items = self.moviesTable.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(Qt.ItemDataRole.UserRole)

    def add_movie(self):
        # Открытие диалога добавления нового фильма
        dialog = MovieDialog(self.db, parent=self)
        dialog.exec()
        self.load_movies()

    def edit_movie(self):
        movie_id = self.get_selected_movie_id()
        if not movie_id:
            QMessageBox.warning(self, "Внимание", "Выберите фильм для редактирования.")
            return

        movie = self.db.get_movie_by_id(movie_id)
        if movie:
            dialog = MovieDialog(self.db, movie=movie, parent=self)
            dialog.exec()
            self.load_movies()

    def delete_movie(self):
        movie_id = self.get_selected_movie_id()
        if not movie_id:
            QMessageBox.warning(self, "Внимание", "Выберите фильм для удаления.")
            return

        # Вызов диалога подтверждения действия
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить этот фильм?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_movie(movie_id)
            self.load_movies()

    def on_single_click(self, row, column):
        # Обработка одиночного клика по строке (отображение постера)
        movie_id = self.moviesTable.item(row, 0).data(Qt.ItemDataRole.UserRole)
        movie = self.db.get_movie_by_id(movie_id)

        if movie and movie.poster_path and os.path.exists(movie.poster_path):
            pixmap = QPixmap(movie.poster_path)
            self.posterPreviewLabel.setPixmap(
                pixmap.scaled(200, 300, Qt.AspectRatioMode.KeepAspectRatio)
            )
        else:
            # Очистка области предпросмотра при отсутствии постера
            self.posterPreviewLabel.setText("Нет постера")
            self.posterPreviewLabel.setPixmap(QPixmap())

    def on_double_click(self, row, column):
        # Двойной клик по строке вызывает окно редактирования
        self.edit_movie()

    def show_context_menu(self, pos):
        # Вызов контекстного меню
        menu = QMenu(self)
        edit_action = menu.addAction("Редактировать")
        delete_action = menu.addAction("Удалить")

        action = menu.exec(self.moviesTable.mapToGlobal(pos))

        if action == edit_action:
            self.edit_movie()
        elif action == delete_action:
            self.delete_movie()

    def show_about(self):
        # Отображение информации о программе
        QMessageBox.about(
            self, "О программе",
            "Каталог фильмов\n\n"
            "Семестровая работа.\n"
        )