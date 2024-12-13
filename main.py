import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QMessageBox,
    QFileDialog, QDialog
)
import xlwt  # Для работы с Excel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class TaskManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Менеджер задач")
        self.setGeometry(100, 100, 900, 800)

        # Данные задач
        self.tasks = []
        self.next_id = 1

        # Основной интерфейс
        self.init_ui()

    def init_ui(self):
        # Основной виджет и макет
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Кнопки управления
        button_layout = QHBoxLayout()
        add_button = QPushButton("Добавить задачу")
        add_button.clicked.connect(self.add_task_dialog)
        save_button = QPushButton("Сохранить задачи в JSON")
        save_button.clicked.connect(self.save_to_file_json)
        save_xls_button = QPushButton("Сохранить задачи в XLS")
        save_xls_button.clicked.connect(self.save_to_file_xls)
        load_button = QPushButton("Загрузить задачи")
        load_button.clicked.connect(self.load_from_file)
        button_layout.addWidget(add_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(save_xls_button)
        button_layout.addWidget(load_button)

        # Таблица задач
        self.table = QTableWidget(0, 6)  # Теперь 6 столбцов
        self.table.setHorizontalHeaderLabels(
            ["ID", "Название", "Описание", "Исполнитель", "Срок", "Статус"]
        )
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 200)

        # Кнопки управления задачами
        task_button_layout = QHBoxLayout()
        complete_button = QPushButton("Отметить выполненной")
        complete_button.clicked.connect(self.mark_completed)
        in_progress_button = QPushButton("Отметить в процессе")
        in_progress_button.clicked.connect(self.mark_in_progress)
        delete_button = QPushButton("Удалить задачу")
        delete_button.clicked.connect(self.delete_task)
        task_button_layout.addWidget(complete_button)
        task_button_layout.addWidget(in_progress_button)
        task_button_layout.addWidget(delete_button)

        # График эффективности
        self.figure = plt.Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        graph_layout = QVBoxLayout()
        graph_layout.addWidget(self.canvas)

        # Компоновка
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)
        main_layout.addLayout(task_button_layout)
        main_layout.addLayout(graph_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def add_task_dialog(self):
        """Открывает диалог для добавления новой задачи."""
        dialog = TaskDialog()
        if dialog.exec():
            task_data = dialog.get_data()
            if all(task_data.values()):
                self.add_task(**task_data)
            else:
                QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")

    def add_task(self, title, description, assignee, deadline):
        """Добавляет новую задачу."""
        task = {
            "id": self.next_id,
            "title": title.strip(),
            "description": description.strip(),
            "assignee": assignee.strip(),
            "deadline": deadline.strip(),
            "status": "Не начата",
        }
        self.tasks.append(task)
        self.next_id += 1
        self.refresh_table()
        self.update_performance_graph()

    def mark_completed(self):
        """Отмечает выбранную задачу как выполненной."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу для выполнения.")
            return
        task_id = int(self.table.item(selected_row, 0).text())
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = "Выполнена"
                break
        self.refresh_table()
        self.update_performance_graph()

    def mark_in_progress(self):
        """Отмечает выбранную задачу как находящуюся в процессе."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу для изменения статуса.")
            return
        task_id = int(self.table.item(selected_row, 0).text())
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = "В процессе"
                break
        self.refresh_table()
        self.update_performance_graph()

    def delete_task(self):
        """Удаляет выбранную задачу."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу для удаления.")
            return
        task_id = int(self.table.item(selected_row, 0).text())
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.refresh_table()
        self.update_performance_graph()

    def save_to_file_json(self):
        """Сохраняет задачи в файл JSON."""
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить задачи", "", "JSON Files (*.json)")
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Успех", "Задачи успешно сохранены в JSON.")

    def save_to_file_xls(self):
        """Сохраняет задачи в файл XLS."""
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить задачи", "", "Excel Files (*.xls)")
        if filename:
            workbook = xlwt.Workbook()
            sheet = workbook.add_sheet("Задачи")

            # Заголовки
            headers = ["ID", "Название", "Описание", "Исполнитель", "Срок", "Статус"]
            for col, header in enumerate(headers):
                sheet.write(0, col, header)

            # Данные
            for row, task in enumerate(self.tasks, start=1):
                sheet.write(row, 0, task["id"])
                sheet.write(row, 1, task["title"])
                sheet.write(row, 2, task["description"])
                sheet.write(row, 3, task["assignee"])
                sheet.write(row, 4, task["deadline"])
                sheet.write(row, 5, task["status"])

            # Сохранение файла
            try:
                workbook.save(filename)
                QMessageBox.information(self, "Успех", "Задачи успешно сохранены в XLS.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")

    def load_from_file(self):
        """Загружает задачи из файла JSON."""
        filename, _ = QFileDialog.getOpenFileName(self, "Загрузить задачи", "", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
                self.next_id = max(task["id"] for task in self.tasks) + 1 if self.tasks else 1
                self.refresh_table()
                self.update_performance_graph()
                QMessageBox.information(self, "Успех", "Задачи успешно загружены.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить задачи: {e}")

    def refresh_table(self):
        """Обновляет таблицу задач."""
        self.table.setRowCount(0)
        for task in self.tasks:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(task["id"])))
            self.table.setItem(row_position, 1, QTableWidgetItem(task["title"]))
            self.table.setItem(row_position, 2, QTableWidgetItem(task["description"]))
            self.table.setItem(row_position, 3, QTableWidgetItem(task["assignee"]))
            self.table.setItem(row_position, 4, QTableWidgetItem(task["deadline"]))
            self.table.setItem(row_position, 5, QTableWidgetItem(task["status"]))

    def update_performance_graph(self):
        """Обновляет график эффективности по исполнителям."""
        assignees = {}
        for task in self.tasks:
            if task["status"] == "Выполнена":
                assignee = task["assignee"]
                assignees[assignee] = assignees.get(assignee, 0) + 1

        # Данные для графика
        names = list(assignees.keys())
        completed_counts = list(assignees.values())

        # Очистка графика
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Построение столбчатой диаграммы
        bars = ax.bar(names, completed_counts, color="skyblue")
        ax.set_title("Эффективность исполнителей", fontsize=14)
        ax.set_xlabel("Исполнитель", fontsize=12)
        ax.set_ylabel("Количество выполненных задач", fontsize=12)
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha="right", fontsize=10)

        # Добавление значений на вершины столбцов
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, str(yval), ha="center", fontsize=10)

        # Отображение графика
        self.canvas.draw()


class TaskDialog(QDialog):
    """Диалог для добавления новой задачи."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить задачу")
        self.setGeometry(150, 150, 400, 300)

        self.layout = QVBoxLayout()

        # Поля ввода
        self.title_input = QLineEdit()
        self.description_input = QTextEdit()
        self.assignee_input = QLineEdit()
        self.deadline_input = QLineEdit()

        # Добавление элементов в макет
        self.layout.addWidget(QLabel("Название"))
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(QLabel("Описание"))
        self.layout.addWidget(self.description_input)
        self.layout.addWidget(QLabel("Исполнитель"))
        self.layout.addWidget(self.assignee_input)
        self.layout.addWidget(QLabel("Срок выполнения"))
        self.layout.addWidget(self.deadline_input)

        # Кнопки
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.cancel_button)

        self.setLayout(self.layout)

    def get_data(self):
        """Возвращает данные задачи."""
        return {
            "title": self.title_input.text(),
            "description": self.description_input.toPlainText(),
            "assignee": self.assignee_input.text(),
            "deadline": self.deadline_input.text(),
        }


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = TaskManagerApp()
    main_window.show()
    sys.exit(app.exec())
