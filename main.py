import sys
from PyQt6.QtWidgets import QApplication
from db.database import Database
from windows.main_window import MainWindow

def main():
    # Инициализация  приложения
    app = QApplication(sys.argv)

    # Создание объекта базы данных и подключение к ней
    db = Database()
    db.connect()

    # Создание и отображение главного окна приложения
    window = MainWindow(db)
    window.show()

    # Запуск обработки событий
    exit_code = app.exec()

    # Закрытие соединения с БД перед завершением программы
    db.close()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()