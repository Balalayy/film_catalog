# windows/movie_dialog.py
import os
import shutil
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from utils.constants import BASE_DIR
from db.models import Movie
from utils.constants import ASSETS_DIR


class MovieDialog(QDialog):
    def __init__(self, db, movie: Movie = None, parent=None):
        super().__init__(parent)

        # Динамическая загрузка интерфейса из файла QtDesigner
        uic.loadUi(os.path.join(BASE_DIR, "ui", "movie_dialog.ui"), self)

        self.db = db
        self.movie = movie
        self.current_poster_path = ""

        self.load_genres()

        if self.movie:
            self.fill_fields()

        # Привязка кнопки выбора постера
        if hasattr(self, 'selectPosterBtn'):
            self.selectPosterBtn.clicked.connect(self.select_poster)

        # ВАЖНО: переопределяем кнопку ОК, чтобы она вызывала наш метод сохранения
        if hasattr(self, 'buttonBox'):
            self.buttonBox.accepted.connect(self.save_movie)
            self.buttonBox.rejected.connect(self.reject)

    def load_genres(self):
        if not hasattr(self, 'genreCombo'):
            return
        genres = self.db.get_all_genres()
        self.genreCombo.clear()
        for genre in genres:
            self.genreCombo.addItem(genre.name, genre.id)

    def fill_fields(self):
        if hasattr(self, 'titleEdit'):
            self.titleEdit.setText(self.movie.title)
        if hasattr(self, 'yearSpin'):
            self.yearSpin.setValue(self.movie.year)
        if hasattr(self, 'ratingSpin'):
            self.ratingSpin.setValue(self.movie.rating)
        if hasattr(self, 'descriptionEdit'):
            self.descriptionEdit.setPlainText(self.movie.description)

        if hasattr(self, 'genreCombo'):
            index = self.genreCombo.findData(self.movie.genre_id)
            if index >= 0:
                self.genreCombo.setCurrentIndex(index)

        if self.movie.poster_path and os.path.exists(self.movie.poster_path):
            self.current_poster_path = self.movie.poster_path
            self.update_poster_preview()

    def select_poster(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите постер", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(ASSETS_DIR, filename)

            # Копируем файл в папку проекта, если его там еще нет
            if file_path != dest_path and not os.path.exists(dest_path):
                shutil.copy(file_path, dest_path)

            self.current_poster_path = dest_path
            self.update_poster_preview()

    def update_poster_preview(self):
        if not hasattr(self, 'posterLabel'):
            return
        pixmap = QPixmap(self.current_poster_path)
        if not pixmap.isNull():
            self.posterLabel.setPixmap(
                pixmap.scaled(
                    self.posterLabel.width(),
                    self.posterLabel.height(),
                    Qt.AspectRatioMode.KeepAspectRatio
                )
            )

    def save_movie(self):
        print("=== НАЧАЛО СОХРАНЕНИЯ ===")
        try:
            title = self.titleEdit.text().strip() if hasattr(self, 'titleEdit') else ""
            year = self.yearSpin.value() if hasattr(self, 'yearSpin') else 0
            genre_id = self.genreCombo.currentData() if hasattr(self, 'genreCombo') else 1
            rating = self.ratingSpin.value() if hasattr(self, 'ratingSpin') else 0.0
            description = self.descriptionEdit.toPlainText().strip() if hasattr(self, 'descriptionEdit') else ""

            print(f"Данные: Название='{title}', Год={year}, Жанр_ID={genre_id}, Рейтинг={rating}")

            if not title:
                QMessageBox.warning(self, "Ошибка", "Введите название фильма!")
                return

            new_movie = Movie(
                id=self.movie.id if self.movie else 0,
                title=title,
                year=year,
                genre_id=genre_id,
                rating=rating,
                description=description,
                poster_path=self.current_poster_path
            )

            if self.movie:
                self.db.update_movie(new_movie)
                print("=== ОБНОВЛЕНО В БД ===")
            else:
                self.db.add_movie(new_movie)
                print("=== ДОБАВЛЕНО В БД ===")

            self.accept()
        except Exception as e:
            print(f"!!! ОШИБКА: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")