# Версия 1: базовое приложение
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen

РАДИУС = 30  
# Версия 2: добавил CCircle
# CCircle объект знает всё о себе
class CCircle:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y
        self._selected = False

    def contains(self, px: int, py: int) -> bool:
        return (px - self._x) ** 2 + (py - self._y) ** 2 <= РАДИУС ** 2

    def toggle_selection(self):
        self._selected = not self._selected

    def set_selected(self, value: bool):
        self._selected = value

    def is_selected(self) -> bool:
        return self._selected

    def draw(self, painter: QPainter):
        if self._selected:
            color = QColor("red")
            color.setAlpha(80)             
            painter.setPen(QPen(QColor("red"), 3))
            painter.setBrush(color)
        else:
            color = QColor("blue")
            color.setAlpha(60)
            painter.setPen(QPen(QColor("blue"), 2))
            painter.setBrush(color)

        painter.drawEllipse(QPoint(self._x, self._y), РАДИУС, РАДИУС)

# Версия 3: добавил CircleStorage
# CircleStorage собственный контейнер
class CircleStorage:
    def __init__(self):
        self._data: list[CCircle] = []

    def add(self, circle: CCircle):
        self._data.append(circle)

    def remove_selected(self):
        self._data = [c for c in self._data if not c.is_selected()]

    # интерфейс списка
    def first(self):
        self._iter = iter(self._data)
        self._current = next(self._iter, None)

    def eol(self) -> bool:
        return self._current is None

    def next_item(self):
        self._current = next(self._iter, None)

    def get_object(self) -> CCircle:
        return self._current

    # для удобства (но контейнер остаётся инкапсулированным)
    def __iter__(self):
        return iter(self._data)

    def reversed(self):
        return reversed(self._data)

# область рисования
class DrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._storage = CircleStorage()

        # чтобы работал Delete
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for circle in self._storage:
            circle.draw(painter)

    def mousePressEvent(self, event):
        px, py = event.x(), event.y()
        ctrl = event.modifiers() & Qt.ControlModifier
        clicked = []

        # идём с конца — верхний круг первый
        for circle in self._storage.reversed():
            if circle.contains(px, py):
                clicked.append(circle)

        if clicked:
            if ctrl:
                # Ctrl — переключаем несколько
                for c in clicked:
                    c.toggle_selection()
            else:
                # обычный клик — выбираем один (верхний)
                for c in self._storage:
                    c.set_selected(False)
                clicked[0].set_selected(True)
        else:
            if not ctrl:
                for c in self._storage:
                    c.set_selected(False)
            self._storage.add(CCircle(px, py))

        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self._storage.remove_selected()
            self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лаб. 3 – Часть 1: Круги на форме")
        self.setMinimumSize(400, 300)

        self._canvas = DrawingWidget()
        self.setCentralWidget(self._canvas)

    def resizeEvent(self, event):
        self._canvas.update()
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(700, 500)
    win.show()
    sys.exit(app.exec_())
    sys.exit(app.exec_())