# Полный код векторного редактора (Lab4)
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QAction, QColorDialog
)
from PyQt5.QtGui import QPainter, QColor, QPen, QPolygon
from PyQt5.QtCore import Qt, QPoint

# Контейнер
class ShapeContainer:
    def __init__(self):
        self.shapes = []

    def add(self, shape):
        self.shapes.append(shape)

    def remove(self, shape):
        if shape in self.shapes:
            self.shapes.remove(shape)

    def get_all(self):
        return self.shapes


# Добавлены базовые классы Shape, фигуры и контейнер
# БАЗОВЫЙ КЛАССimport sys
import math
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import (QPainter, QColor, QPen, QBrush, QPolygonF,
                         QMouseEvent, QKeyEvent)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QToolBar,
                             QAction, QColorDialog, QDialog, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
class Shape:
    def __init__(self, position, color=Qt.green):
        self.position = position
        self.color = color
        self.selected = False
        self.bounds = None

    def draw(self, painter: QPainter):
        raise NotImplementedError

    def move(self, dx, dy):
        new_pos = self.position + QPointF(dx, dy)
        old_pos = self.position
        self.position = new_pos
        if self.check_bounds():
            return True
        else:
            self.position = old_pos
            return False

    def resize(self, dw, dh):
        raise NotImplementedError

    def contains(self, point: QPointF) -> bool:
        raise NotImplementedError

    def get_bounding_rect(self) -> QRectF:
        raise NotImplementedError

    def check_bounds(self, new_pos=None) -> bool:
    #Проверяет, находится ли фигура полностью в границах bounds
        if self.bounds is None:
            return True

        # Получаем bounding rect фигуры
        rect = self.get_bounding_rect()

        # Проверяем, что весь прямоугольник внутри bounds
        return (rect.left() >= self.bounds.left() and
                rect.top() >= self.bounds.top() and
                rect.right() <= self.bounds.right() and
                rect.bottom() <= self.bounds.bottom())

    def set_bounds(self, bounds: QRectF):
        self.bounds = bounds

    def set_selected(self, selected: bool):
        self.selected = selected

    def get_color(self):
        return self.color

    def set_color(self, color: QColor):
        self.color = color

    def get_size_params(self):
        raise NotImplementedError

    def set_size_params(self, params):
        raise NotImplementedError

class Circle(Shape):
    def __init__(self, center, radius=20, color=Qt.blue):
        super().__init__(center, color)
        self.radius = radius

    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        if self.selected:
            painter.setPen(QPen(Qt.red, 2))
        painter.drawEllipse(self.position, self.radius, self.radius)

    def get_bounding_rect(self):
        return QRectF(self.position.x() - self.radius,
                      self.position.y() - self.radius,
                      self.radius * 2, self.radius * 2)

    def contains(self, point):
        return (point.x() - self.position.x()) ** 2 + \
               (point.y() - self.position.y()) ** 2 <= self.radius ** 2

    def resize(self, dw, dh):
        new_radius = self.radius + (dw + dh) / 2
        if new_radius >= 1:
            old = self.radius
            self.radius = new_radius
            if not self.check_bounds():
                self.radius = old
                return False
            return True
        return False

    def get_size_params(self):
        return {"radius": self.radius}

    def set_size_params(self, params):
        new_radius = params.get("radius")
        if new_radius is not None and new_radius >= 1:
            self.radius = new_radius
            # Проверка границ после изменения
            if not self.check_bounds():
                self.radius = new_radius 
                return False
        return True


class Square(Shape):
    def __init__(self, center, side=40, color=Qt.blue):
        super().__init__(center, color)
        self.side = side

    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        if self.selected:
            painter.setPen(QPen(Qt.red, 2))
        painter.drawRect(QRectF(self.position.x() - self.side / 2,
                                self.position.y() - self.side / 2,
                                self.side, self.side))

    def get_bounding_rect(self):
        return QRectF(self.position.x() - self.side / 2,
                      self.position.y() - self.side / 2,
                      self.side, self.side)

    def contains(self, point):
        return self.get_bounding_rect().contains(point)

    def resize(self, dw, dh):
        new_side = self.side + (dw + dh) / 2
        if new_side >= 1:
            old = self.side
            self.side = new_side
            if not self.check_bounds():
                self.side = old
                return False
            return True
        return False

    def get_size_params(self):
        return {"side": self.side}

    def set_size_params(self, params):
        new_side = params.get("side")
        if new_side is not None and new_side >= 1:
            self.side = new_side
            if not self.check_bounds():
                return False
        return True


class Rectangle(Shape):
    def __init__(self, center, width=40, height=30, color=Qt.blue):
        super().__init__(center, color)
        self.width = width
        self.height = height

    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        if self.selected:
            painter.setPen(QPen(Qt.red, 2))
        painter.drawRect(QRectF(self.position.x() - self.width / 2,
                                self.position.y() - self.height / 2,
                                self.width, self.height))

    def get_bounding_rect(self):
        return QRectF(self.position.x() - self.width / 2,
                      self.position.y() - self.height / 2,
                      self.width, self.height)

    def contains(self, point):
        return self.get_bounding_rect().contains(point)

    def resize(self, dw, dh):
        new_w = self.width + dw
        new_h = self.height + dh
        if new_w >= 1 and new_h >= 1:
            old_w, old_h = self.width, self.height
            self.width, self.height = new_w, new_h
            if not self.check_bounds():
                self.width, self.height = old_w, old_h
                return False
            return True
        return False

    def get_size_params(self):
        return {"width": self.width, "height": self.height}

    def set_size_params(self, params):
        new_w = params.get("width")
        new_h = params.get("height")
        if new_w is not None and new_h is not None and new_w >= 1 and new_h >= 1:
            self.width = new_w
            self.height = new_h
            if not self.check_bounds():
                return False
        return True


class Ellipse(Rectangle):
    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        if self.selected:
            painter.setPen(QPen(Qt.red, 2))
        painter.drawEllipse(QRectF(self.position.x() - self.width / 2,
                                   self.position.y() - self.height / 2,
                                   self.width, self.height))

    def get_size_params(self):
        return {"width": self.width, "height": self.height}

    def set_size_params(self, params):
        return super().set_size_params(params)


class Triangle(Shape):
    def __init__(self, center, base=40, height=40, color=Qt.blue):
        super().__init__(center, color)
        self.base = base
        self.height = height
        self.points = self._calc_points()

    def _calc_points(self):
        cx, cy = self.position.x(), self.position.y()
        top = QPointF(cx, cy - self.height / 2)
        bottom_left = QPointF(cx - self.base / 2, cy + self.height / 2)
        bottom_right = QPointF(cx + self.base / 2, cy + self.height / 2)
        return [top, bottom_left, bottom_right]

    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        if self.selected:
            painter.setPen(QPen(Qt.red, 2))
        polygon = QPolygonF(self.points)
        painter.drawPolygon(polygon)

    def get_bounding_rect(self):
        xs = [p.x() for p in self.points]
        ys = [p.y() for p in self.points]
        return QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))

    def contains(self, point):
        poly = QPolygonF(self.points)
        return poly.containsPoint(point, Qt.OddEvenFill)

    def resize(self, dw, dh):
        new_base = self.base + dw
        new_height = self.height + dh
        if new_base >= 5 and new_height >= 5: 
            old_base, old_height = self.base, self.height
            old_points = self.points.copy()
            self.base, self.height = new_base, new_height
            self.points = self._calc_points()
            if not self.check_bounds():
                self.base, self.height = old_base, old_height
                self.points = old_points
                return False
            return True
        return False

    def move(self, dx, dy):
        old_position = self.position
        old_points = self.points.copy()

        new_pos = self.position + QPointF(dx, dy)
        self.position = new_pos
        self.points = self._calc_points()

        if self.check_bounds():
            return True
        else:
            self.position = old_position
            self.points = old_points
            return False

    def check_bounds(self, new_pos=None):
        #Проверяет, находится ли треугольник полностью в границах.
        if self.bounds is None:
            return True

        # Получаем текущие точки
        points_to_check = self.points

        # Проверяем каждую вершину треугольника
        for point in points_to_check:
            if not (self.bounds.left() <= point.x() <= self.bounds.right() and
                    self.bounds.top() <= point.y() <= self.bounds.bottom()):
                return False
        return True

    def get_size_params(self):
        return {"base": self.base, "height": self.height}

    def set_size_params(self, params):
        new_base = params.get("base")
        new_height = params.get("height")
        if new_base is not None and new_height is not None and new_base >= 5 and new_height >= 5:
            old_base, old_height = self.base, self.height
            old_points = self.points.copy()
            self.base = new_base
            self.height = new_height
            self.points = self._calc_points()
            if not self.check_bounds():
                self.base, self.height = old_base, old_height
                self.points = old_points
                return False
            return True
        return False


class Line(Shape):
    def __init__(self, start_point, end_point, color=Qt.blue):
        super().__init__(start_point, color)
        self.end_point = end_point
        self.width = 2

    def draw(self, painter):
        painter.setPen(QPen(self.color, self.width))
        if self.selected:
            painter.setPen(QPen(Qt.red, self.width + 1))
        painter.drawLine(self.position, self.end_point)

    def get_bounding_rect(self):
        x1, y1 = self.position.x(), self.position.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        return QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

    def contains(self, point):
        a = self.position
        b = self.end_point
        ab = b - a
        t = ((point.x() - a.x()) * ab.x() + (point.y() - a.y()) * ab.y())
        t /= (ab.x() * ab.x() + ab.y() * ab.y() + 1e-10)
        if t < 0:
            t = 0
        if t > 1:
            t = 1
        proj = a + ab * t
        return math.hypot(point.x() - proj.x(), point.y() - proj.y()) <= 5

    def get_center(self):
        return QPointF((self.position.x() + self.end_point.x()) / 2,
                       (self.position.y() + self.end_point.y()) / 2)

    def resize(self, dw, dh):
        center = self.get_center()

        half_vector = QPointF((self.end_point.x() - self.position.x()) / 2,
                              (self.end_point.y() - self.position.y()) / 2)

        current_length = math.hypot(half_vector.x(), half_vector.y()) * 2

        delta = (dw + dh) / 2
        new_length = current_length + delta

        if new_length < 4:
            return False

        if current_length > 0:
            scale = new_length / current_length
            new_half_vector = QPointF(half_vector.x() * scale, half_vector.y() * scale)
        else:
            new_half_vector = QPointF(10, 0)  # Если длина была 0, создаём горизонтальный отрезок

        new_start = QPointF(center.x() - new_half_vector.x(), center.y() - new_half_vector.y())
        new_end = QPointF(center.x() + new_half_vector.x(), center.y() + new_half_vector.y())

        old_start = self.position
        old_end = self.end_point

        self.position = new_start
        self.end_point = new_end

        if not self.check_bounds():
            self.position = old_start
            self.end_point = old_end
            return False
        return True

    def move(self, dx, dy):
        new_start = self.position + QPointF(dx, dy)
        new_end = self.end_point + QPointF(dx, dy)
        old_start, old_end = self.position, self.end_point
        self.position, self.end_point = new_start, new_end
        if not self.check_bounds():
            self.position, self.end_point = old_start, old_end
            return False
        return True

    def check_bounds(self, new_pos=None, new_end=None):
        if self.bounds is None:
            return True
        if new_pos is not None:
            start = new_pos
            end = new_end if new_end is not None else self.end_point
        else:
            start = self.position
            end = self.end_point
        # Проверяем, что обе точки находятся в границах
        return (self.bounds.left() <= start.x() <= self.bounds.right() and
                self.bounds.top() <= start.y() <= self.bounds.bottom() and
                self.bounds.left() <= end.x() <= self.bounds.right() and
                self.bounds.top() <= end.y() <= self.bounds.bottom())

    def get_size_params(self):
        dx = self.end_point.x() - self.position.x()
        dy = self.end_point.y() - self.position.y()
        length = math.hypot(dx, dy)
        angle = math.degrees(math.atan2(dy, dx))
        return {"length": length, "angle": angle}

    def set_size_params(self, params):
        length = params.get("length")
        angle = params.get("angle")
        if length is not None and angle is not None and length >= 4:
            center = self.get_center()

            rad = math.radians(angle)
            half_length = length / 2
            dx = half_length * math.cos(rad)
            dy = half_length * math.sin(rad)

            new_start = QPointF(center.x() - dx, center.y() - dy)
            new_end = QPointF(center.x() + dx, center.y() + dy)

            old_start, old_end = self.position, self.end_point
            self.position, self.end_point = new_start, new_end

            if not self.check_bounds():
                self.position, self.end_point = old_start, old_end
                return False
        return True
# Контейнер фигур
class ShapeContainer:
    def __init__(self):
        self.shapes = []
        self.selected_indices = set()

    def add(self, shape):
        self.shapes.append(shape)
        return len(self.shapes) - 1

    def remove(self, index):
        if 0 <= index < len(self.shapes):
            if index in self.selected_indices:
                self.selected_indices.remove(index)
            new_selected = set()
            for i in self.selected_indices:
                if i > index:
                    new_selected.add(i - 1)
                elif i < index:
                    new_selected.add(i)
            self.selected_indices = new_selected
            del self.shapes[index]

    def get(self, index):
        return self.shapes[index] if 0 <= index < len(self.shapes) else None

    def get_all(self):
        return self.shapes

    def clear_selection(self):
        for i in self.selected_indices:
            self.shapes[i].set_selected(False)
        self.selected_indices.clear()

    def select_one(self, index, add_to_selection=False):
        if add_to_selection:
            if index in self.selected_indices:
                self.shapes[index].set_selected(False)
                self.selected_indices.remove(index)
            else:
                self.shapes[index].set_selected(True)
                self.selected_indices.add(index)
        else:
            self.clear_selection()
            if 0 <= index < len(self.shapes):
                self.shapes[index].set_selected(True)
                self.selected_indices.add(index)

    def get_selected(self):
        return [self.shapes[i] for i in self.selected_indices]

    def move_selected(self, dx, dy):
        for i in self.selected_indices:
            self.shapes[i].move(dx, dy)

    def resize_selected(self, dw, dh):
        for i in self.selected_indices:
            self.shapes[i].resize(dw, dh)

    def set_color_to_selected(self, color):
        for i in self.selected_indices:
            self.shapes[i].set_color(color)

    def delete_selected(self):
        indices = sorted(list(self.selected_indices), reverse=True)
        for idx in indices:
            self.remove(idx)
        self.selected_indices.clear()

    def set_size_for_selected(self, params):
        for i in self.selected_indices:
            self.shapes[i].set_size_params(params)


class ResizeDialog(QDialog):
    def __init__(self, shape, parent=None):
        super().__init__(parent)
        self.shape = shape
        self.setWindowTitle("Изменение размера")
        layout = QVBoxLayout()

        # Получаем параметры размера для данной фигуры
        self.params = shape.get_size_params()
        self.inputs = {}

        for key, value in self.params.items():
            label = QLabel(f"{key.capitalize()}:")
            layout.addWidget(label)
            edit = QLineEdit(str(value))
            layout.addWidget(edit)
            self.inputs[key] = edit

        button_ok = QPushButton("OK")
        button_ok.clicked.connect(self.accept)
        layout.addWidget(button_ok)

        button_cancel = QPushButton("Отмена")
        button_cancel.clicked.connect(self.reject)
        layout.addWidget(button_cancel)

        self.setLayout(layout)

    def get_new_params(self):
        new_params = {}
        for key, edit in self.inputs.items():
            try:
                new_params[key] = float(edit.text())
            except ValueError:
                return None
        return new_params

class SceneWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.container = ShapeContainer()
        self.current_tool = 'circle'
        self.temp_line_start = None
        self.setMinimumSize(400, 300)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

        # Переменные для перетаскивания мышью
        self.dragging = False
        self.drag_start_pos = None
        self.dragged_indices = set() 

    def set_tool(self, tool):
        self.current_tool = tool
        if tool != 'line':
            self.temp_line_start = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.white)
        painter.setPen(Qt.gray)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

        bounds = QRectF(0, 0, self.width(), self.height())
        for shape in self.container.get_all():
            shape.set_bounds(bounds)
            shape.draw(painter)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.LeftButton:
            return

        pos = event.pos()
        shapes = self.container.get_all()
        # Поиск фигуры под курсором
        clicked_index = -1
        for i in range(len(shapes) - 1, -1, -1):
            if shapes[i].contains(pos):
                clicked_index = i
                break

        if clicked_index != -1:
            # Выделение
            if event.modifiers() & Qt.ControlModifier:
                self.container.select_one(clicked_index, add_to_selection=True)
            else:
                self.container.select_one(clicked_index, add_to_selection=False)
            self.update()

            # Начинаем перетаскивание
            self.dragging = True
            self.drag_start_pos = pos
            self.dragged_indices = set(self.container.selected_indices)  # копия
        else:
            # Клик по пустому месту – снять выделение
            self.container.clear_selection()
            self.update()
            # Создание новой фигуры
            bounds = QRectF(0, 0, self.width(), self.height())
            if self.current_tool == 'line':
                if self.temp_line_start is None:
                    self.temp_line_start = pos
                else:
                    line = Line(self.temp_line_start, pos, Qt.blue)
                    line.set_bounds(bounds)
                    if not line.check_bounds():
                        end = line.end_point
                        if end.x() < 0:
                            end.setX(0)
                        if end.y() < 0:
                            end.setY(0)
                        if end.x() > bounds.right():
                            end.setX(bounds.right())
                        if end.y() > bounds.bottom():
                            end.setY(bounds.bottom())
                        line.end_point = end
                    self.container.add(line)
                    self.temp_line_start = None
                    self.update()
            else:
                shape = None
                if self.current_tool == 'circle':
                    shape = Circle(pos, 20, Qt.blue)
                elif self.current_tool == 'square':
                    shape = Square(pos, 40, Qt.blue)
                elif self.current_tool == 'rectangle':
                    shape = Rectangle(pos, 40, 30, Qt.blue)
                elif self.current_tool == 'ellipse':
                    shape = Ellipse(pos, 40, 30, Qt.blue)
                elif self.current_tool == 'triangle':
                    shape = Triangle(pos, 40, 40, Qt.blue)
                if shape:
                    shape.set_bounds(bounds)
                    if not shape.check_bounds():
                        rect = shape.get_bounding_rect()
                        dx = dy = 0
                        if rect.left() < 0:
                            dx = -rect.left()
                        if rect.top() < 0:
                            dy = -rect.top()
                        if rect.right() > bounds.right():
                            dx = bounds.right() - rect.right()
                        if rect.bottom() > bounds.bottom():
                            dy = bounds.bottom() - rect.bottom()
                        shape.move(dx, dy)
                    self.container.add(shape)
                    self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and self.drag_start_pos is not None:
            pos = event.pos()
            delta = pos - self.drag_start_pos
            if delta.x() != 0 or delta.y() != 0:
                for idx in self.dragged_indices:
                    shape = self.container.get(idx)
                    if shape:
                        shape.move(delta.x(), delta.y())
                self.drag_start_pos = pos
                self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.drag_start_pos = None
            self.dragged_indices.clear()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        # Двойной клик для изменения размера фигуры
        pos = event.pos()
        shapes = self.container.get_all()
        for i in range(len(shapes) - 1, -1, -1):
            if shapes[i].contains(pos):
                # Выделяем эту фигуру (если ещё не выделена)
                if not shapes[i].selected:
                    self.container.select_one(i, add_to_selection=False)
                    self.update()
                # Показываем диалог изменения размера
                selected_shapes = self.container.get_selected()
                if len(selected_shapes) == 1:
                    dlg = ResizeDialog(selected_shapes[0], self)
                    if dlg.exec_() == QDialog.Accepted:
                        new_params = dlg.get_new_params()
                        if new_params is not None:
                            if selected_shapes[0].set_size_params(new_params):
                                self.update()
                            else:
                                QMessageBox.warning(self, "Ошибка", "Новые размеры выходят за границы области.")
                else:
                    QMessageBox.information(self, "Информация", "Изменение размера доступно только для одной фигуры.")
                break

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()
        selected = self.container.get_selected()
        if not selected:
            return

        step = 5
        if modifiers & Qt.ControlModifier:
            if key == Qt.Key_Left:
                self.container.resize_selected(-step, 0)
            elif key == Qt.Key_Right:
                self.container.resize_selected(step, 0)
            elif key == Qt.Key_Up:
                self.container.resize_selected(0, -step)
            elif key == Qt.Key_Down:
                self.container.resize_selected(0, step)
            else:
                return
        else:
            if key == Qt.Key_Left:
                self.container.move_selected(-step, 0)
            elif key == Qt.Key_Right:
                self.container.move_selected(step, 0)
            elif key == Qt.Key_Up:
                self.container.move_selected(0, -step)
            elif key == Qt.Key_Down:
                self.container.move_selected(0, step)
            elif key in (Qt.Key_Delete, Qt.Key_Backspace):
                self.container.delete_selected()
            elif key == Qt.Key_C:
                color = QColorDialog.getColor(selected[0].get_color(), self, "Выберите цвет")
                if color.isValid():
                    self.container.set_color_to_selected(color)
            else:
                return
        self.update()

    def resizeEvent(self, event):
        bounds = QRectF(0, 0, self.width(), self.height())
        for shape in self.container.get_all():
            shape.set_bounds(bounds)
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Векторный редактор")
        self.setGeometry(100, 100, 800, 600)

        self.scene_widget = SceneWidget(self)
        self.setCentralWidget(self.scene_widget)

        self.create_toolbar()
        self.create_menu()
        self.statusBar().showMessage("Готов")

    def create_toolbar(self):
        toolbar = self.addToolBar("Инструменты")
        toolbar.setMovable(False)

        tools = {
            "Круг": "circle",
            "Квадрат": "square",
            "Прямоугольник": "rectangle",
            "Эллипс": "ellipse",
            "Треугольник": "triangle",
            "Отрезок": "line"
        }
        for name, tool in tools.items():
            action = QAction(name, self)
            action.triggered.connect(lambda checked, t=tool: self.set_tool(t))
            toolbar.addAction(action)

        toolbar.addSeparator()
        color_action = QAction("Изменить цвет", self)
        color_action.triggered.connect(self.change_color)
        toolbar.addAction(color_action)

        delete_action = QAction("Удалить", self)
        delete_action.triggered.connect(self.delete_selected)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()
        increase_action = QAction("Увеличить размер", self)
        increase_action.triggered.connect(lambda: self.resize_selected(5, 5))
        toolbar.addAction(increase_action)
        decrease_action = QAction("Уменьшить размер", self)
        decrease_action.triggered.connect(lambda: self.resize_selected(-5, -5))
        toolbar.addAction(decrease_action)

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("Правка")
        color_action = QAction("Изменить цвет", self)
        color_action.triggered.connect(self.change_color)
        edit_menu.addAction(color_action)

        delete_action = QAction("Удалить", self)
        delete_action.triggered.connect(self.delete_selected)
        edit_menu.addAction(delete_action)

    def set_tool(self, tool):
        self.scene_widget.set_tool(tool)
        self.statusBar().showMessage(f"Выбран инструмент: {tool}")

    def change_color(self):
        selected = self.scene_widget.container.get_selected()
        if selected:
            color = QColorDialog.getColor(selected[0].get_color(), self, "Выберите цвет")
            if color.isValid():
                self.scene_widget.container.set_color_to_selected(color)
                self.scene_widget.update()

    def delete_selected(self):
        self.scene_widget.container.delete_selected()
        self.scene_widget.update()

    def resize_selected(self, dw, dh):
        self.scene_widget.container.resize_selected(dw, dh)
        self.scene_widget.update()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


class Shape:
    def __init__(self, x, y, w, h, color=Qt.blue):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = QColor(color)
        self.selected = False

    def draw(self, painter):
        pass

    def contains(self, px, py):
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    def move(self, dx, dy, max_w, max_h):
        nx, ny = self.x + dx, self.y + dy
        if self.check_bounds(nx, ny, self.w, self.h, max_w, max_h):
            self.x, self.y = nx, ny

    def resize(self, dw, dh, max_w, max_h):
        nw, nh = max(10, self.w + dw), max(10, self.h + dh)
        if self.check_bounds(self.x, self.y, nw, nh, max_w, max_h):
            self.w, self.h = nw, nh

    def check_bounds(self, x, y, w, h, max_w, max_h):
        return 0 <= x and 0 <= y and x + w <= max_w and y + h <= max_h

    def draw_selection(self, painter):
        if self.selected:
            pen = QPen(Qt.red, 2, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.x, self.y, self.w, self.h)


# ФИГУРЫ
class Rectangle(Shape):
    def draw(self, painter):
        painter.setBrush(self.color)
        painter.drawRect(self.x, self.y, self.w, self.h)
        self.draw_selection(painter)


class Square(Rectangle):
    def resize(self, dw, dh, max_w, max_h):
        size = max(10, self.w + dw)
        if self.check_bounds(self.x, self.y, size, size, max_w, max_h):
            self.w = self.h = size


class Ellipse(Shape):
    def draw(self, painter):
        painter.setBrush(self.color)
        painter.drawEllipse(self.x, self.y, self.w, self.h)
        self.draw_selection(painter)


class Circle(Ellipse):
    def resize(self, dw, dh, max_w, max_h):
        size = max(10, self.w + dw)
        if self.check_bounds(self.x, self.y, size, size, max_w, max_h):
            self.w = self.h = size


class Line(Shape):
    def draw(self, painter):
        painter.setPen(QPen(self.color, 3))
        painter.drawLine(self.x, self.y, self.x + self.w, self.y + self.h)
        self.draw_selection(painter)


class Triangle(Shape):
    def draw(self, painter):
        painter.setBrush(self.color)
        points = QPolygon([
            QPoint(self.x + self.w // 2, self.y),
            QPoint(self.x, self.y + self.h),
            QPoint(self.x + self.w, self.y + self.h)
        ])
        painter.drawPolygon(points)
        self.draw_selection(painter)


# CANVAS
class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.container = ShapeContainer()
        self.selected_shapes = []

    def paintEvent(self, event):
        painter = QPainter(self)
        for s in self.container.get_all():
            s.draw(painter)

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()

        if not (event.modifiers() & Qt.ControlModifier):
            self.clear_selection()

        for s in reversed(self.container.get_all()):
            if s.contains(x, y):
                s.selected = True
                self.selected_shapes.append(s)
                break

        self.update()

    def clear_selection(self):
        for s in self.selected_shapes:
            s.selected = False
        self.selected_shapes.clear()

    def keyPressEvent(self, event):
        for s in self.selected_shapes:
            if event.key() == Qt.Key_Left:
                s.move(-5, 0, self.width(), self.height())
            elif event.key() == Qt.Key_Right:
                s.move(5, 0, self.width(), self.height())
            elif event.key() == Qt.Key_Up:
                s.move(0, -5, self.width(), self.height())
            elif event.key() == Qt.Key_Down:
                s.move(0, 5, self.width(), self.height())
            elif event.key() == Qt.Key_Delete:
                self.container.remove(s)

        self.update()

    # действия меню
    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            for s in self.selected_shapes:
                s.color = color
        self.update()

    def delete_selected(self):
        for s in self.selected_shapes[:]:
            self.container.remove(s)
        self.selected_shapes.clear()
        self.update()

    def resize_up(self):
        for s in self.selected_shapes:
            s.resize(10, 10, self.width(), self.height())
        self.update()

    def resize_down(self):
        for s in self.selected_shapes:
            s.resize(-10, -10, self.width(), self.height())
        self.update()


# ГЛАВНОЕ ОКНО
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Editor")
        self.resize(800, 600)

        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)

        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()

        # Файл
        file_menu = menubar.addMenu("Файл")

        # Правка
        edit_menu = menubar.addMenu("Правка")

        # фигуры
        shapes_menu = menubar.addMenu("Фигуры")

        shapes_menu.addAction("Круг", self.add_circle)
        shapes_menu.addAction("Квадрат", self.add_square)
        shapes_menu.addAction("Прямоугольник", self.add_rectangle)
        shapes_menu.addAction("Эллипс", self.add_ellipse)
        shapes_menu.addAction("Треугольник", self.add_triangle)
        shapes_menu.addAction("Отрезок", self.add_line)

        # правка
        edit_menu.addAction("Изменить цвет", self.canvas.change_color)
        edit_menu.addAction("Удалить", self.canvas.delete_selected)
        edit_menu.addAction("Увеличить размер", self.canvas.resize_up)
        edit_menu.addAction("Уменьшить размер", self.canvas.resize_down)

    # создание фигур
    def add_rectangle(self):
        self.canvas.container.add(Rectangle(50, 50, 120, 80))
        self.canvas.update()

    def add_square(self):
        self.canvas.container.add(Square(100, 100, 80, 80))
        self.canvas.update()

    def add_circle(self):
        self.canvas.container.add(Circle(150, 150, 80, 80))
        self.canvas.update()

    def add_ellipse(self):
        self.canvas.container.add(Ellipse(200, 200, 120, 80))
        self.canvas.update()

    def add_triangle(self):
        self.canvas.container.add(Triangle(250, 250, 100, 80))
        self.canvas.update()

    def add_line(self):
        self.canvas.container.add(Line(300, 300, 100, 50))
        self.canvas.update()


# ЗАПУСК
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())