import sys
import pickle
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QMessageBox, QShortcut
from PyQt5.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qtaskst")
        self.layout = QVBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Type here to add new tasks")
        self.task_input.returnPressed.connect(self.add_task)
        self.layout.addWidget(self.task_input)
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.shortcuts_button = QPushButton("Shortcuts")
        self.shortcuts_button.clicked.connect(self.shortcuts)
        self.layout.addWidget(self.shortcuts_button)

        self.setLayout(self.layout)
        screen = QApplication.primaryScreen()
        width = screen.size().width()
        height = screen.size().height()
        self.resize(int(width * 0.7), int(height * 0.6))
        self.setStyleSheet("background-color: #2b2a34; color: white;")
        self.load_tasks()
        self.create_shortcuts()

    def create_shortcuts(self):
        QShortcut(Qt.CTRL + Qt.Key_W, self).activated.connect(self.close)
        QShortcut(Qt.SHIFT + Qt.Key_Delete, self).activated.connect(self.show_deleted_tasks)
        QShortcut(Qt.SHIFT + Qt.ALT + Qt.Key_Delete, self).activated.connect(self.clear_deleted_tasks)
        QShortcut(Qt.CTRL + Qt.Key_O, self).activated.connect(self.shortcuts)
        

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_items = self.list_widget.selectedItems()
            if selected_items:
                for item in selected_items:
                    font = item.font()
                    font.setStrikeOut(True)
                    item.setFont(font)
                    item.setForeground(Qt.gray)
                    item.setFlags(item.flags() & ~Qt.ItemIsSelectable)

                    current_time = datetime.now().strftime("%d/%m/%Y %I:%M%p")
                    original_text = item.text()
                    deleted_text = f"{original_text} (Deleted {current_time})"
                    item.setText(deleted_text)

                    self.save_tasks()
        else:
            super().keyPressEvent(event)

    def add_task(self):
            task = self.task_input.text()
            if task:
                current_time = datetime.now().strftime("%d/%m/%Y %I:%M%p")
                task_with_time = f"{task} (Added {current_time})"
                self.list_widget.addItem(QListWidgetItem(task_with_time))
                self.task_input.clear()
                self.save_tasks()

    def save_tasks(self):
        active_tasks = [self.list_widget.item(i).text() for i in range(self.list_widget.count()) if self.list_widget.item(i).flags() & Qt.ItemIsSelectable]
        deleted_tasks = [self.list_widget.item(i).text() for i in range(self.list_widget.count()) if not self.list_widget.item(i).flags() & Qt.ItemIsSelectable]
        with open("tasks_active.pkl", "wb") as f:
            pickle.dump(active_tasks, f)
        with open("tasks_deleted.pkl", "wb") as f:
            pickle.dump(deleted_tasks, f)

    def load_tasks(self):
        try:
            with open("tasks_active.pkl", "rb") as f:
                active_tasks = pickle.load(f)
                for task in active_tasks:
                    self.list_widget.addItem(QListWidgetItem(task))
        except FileNotFoundError:
            pass

    def show_deleted_tasks(self):
        try:
            with open("tasks_deleted.pkl", "rb") as f:
                deleted_tasks = pickle.load(f)
                if deleted_tasks:
                    msg = QMessageBox()
                    msg.setWindowTitle("Deleted Tasks")
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("\n".join(deleted_tasks))
                    msg.exec_()
                else:
                    QMessageBox.information(self, "Deleted Tasks", "No deleted tasks found.")
        except Exception:
            QMessageBox.information(self, "Deleted Tasks", "No deleted tasks could be found.")

    def clear_deleted_tasks(self):
        try:
            open("tasks_deleted.pkl", "wb").close()
            QMessageBox.information(self, "Deleted Tasks", "Deleted tasks cleared successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def shortcuts(self):
        try:
            shortcuts_list = [["Del (when task selected)","Deletes task"], ["Control + W", "Close the application"],["Shift + Del", "Show deleted tasks"],["Alt + Shift + Del", "Clear deleted tasks"], ["Control + O", "Open this shortcuts pop-up"]]
            msg = QMessageBox()
            msg.setWindowTitle("Shortcuts")
            msg.setIcon(QMessageBox.Information)
            msg.setText("\n".join([" - ".join(shortcut) for shortcut in shortcuts_list]))
            msg.exec_()
        except Exception:
            QMessageBox.information(self, "Error", "Shortcuts cannot be shown.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
