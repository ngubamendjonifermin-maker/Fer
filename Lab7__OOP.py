# -*- coding: utf-8 -*-
import sys
import math
import json
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QToolBar, QAction, QColorDialog,
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QSplitter, QComboBox
)

# Базовый класс Shape
class Shape(QObject):
    def __init__(self, position, color=None):
        super().__init__()
        self.position = position
        self.color = color if color is not None else QColor(0, 255, 0)
        self.selected = False
        self.bounds = None

    def draw(self, painter): raise NotImplementedError
    def move(self, dx, dy):
        if self.position is None: return False
        new_pos = self.position + QPointF(dx, dy)
        old = self.position
        self.position = new_pos
        if self.check_bounds():
            return True
        self.position = old
        return False
    def resize(self, dw, dh): raise NotImplementedError
    def contains(self, point): raise NotImplementedError
    def get_bounding_rect(self): raise NotImplementedError
    def check_bounds(self, new_pos=None):
        if self.bounds is None: return True
        rect = self.get_bounding_rect()
        if rect is None: return False
        return (rect.left() >= self.bounds.left() and rect.top() >= self.bounds.top() and
                rect.right() <= self.bounds.right() and rect.bottom() <= self.bounds.bottom())
    def set_bounds(self, bounds): self.bounds = bounds
    def set_selected(self, selected): self.selected = selected
    def get_color(self): return self.color
    def set_color(self, color): self.color = color
    def get_size_params(self): raise NotImplementedError
    def set_size_params(self, params): raise NotImplementedError
    def center_in_bounds(self):
        if self.bounds is None: return
        rect = self.get_bounding_rect()
        if rect is None: return
        dx = dy = 0
        if rect.left() < self.bounds.left(): dx = self.bounds.left() - rect.left()
        if rect.top() < self.bounds.top(): dy = self.bounds.top() - rect.top()
        if rect.right() > self.bounds.right(): dx = self.bounds.right() - rect.right()
        if rect.bottom() > self.bounds.bottom(): dy = self.bounds.bottom() - rect.bottom()
        if dx != 0 or dy != 0: self.move(dx, dy)
    def get_type_name(self): return self.__class__.__name__
    def save(self):
        data = {
            "type": self.get_type_name(),
            "x": self.position.x(), "y": self.position.y(),
            "color_r": self.color.red(), "color_g": self.color.green(),
            "color_b": self.color.blue(), "color_a": self.color.alpha()
        }
        data.update(self.get_size_params())
        return data
    def load(self, data):
        self.position = QPointF(data.get("x", 0), data.get("y", 0))
        self.color = QColor(data.get("color_r", 0), data.get("color_g", 0),
                            data.get("color_b", 255), data.get("color_a", 255))
        self.set_size_params(data)

# Круг
class Circle(Shape):
    def __init__(self, center, radius=20, color=None):
        super().__init__(center, color if color else QColor(0,0,255))
        self.radius = radius
    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        if self.selected: painter.setPen(QPen(Qt.red, 2))
        painter.drawEllipse(self.position, self.radius, self.radius)
    def get_bounding_rect(self):
        return QRectF(self.position.x()-self.radius, self.position.y()-self.radius,
                      self.radius*2, self.radius*2)
    def contains(self, point):
        return (point.x()-self.position.x())**2 + (point.y()-self.position.y())**2 <= self.radius**2
    def resize(self, dw, dh):
        delta = max(abs(dw), abs(dh))
        if dw < 0 or dh < 0: delta = -delta
        new_r = self.radius + delta
        if new_r >= 2:
            old = self.radius
            self.radius = new_r
            if not self.check_bounds():
                self.radius = old
                return False
            return True
        return False
    def get_size_params(self): return {"radius": self.radius}
    def set_size_params(self, params):
        r = params.get("radius")
        if r is not None and r >= 2:
            self.radius = r
            self.center_in_bounds()
            return True
        return False

# Квадрат
class Square(Shape):
    def __init__(self, center, side=40, color=None):
        super().__init__(center, color if color else QColor(0,0,255))
        self.side = side
    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        if self.selected: painter.setPen(QPen(Qt.red, 2))
        r = QRectF(self.position.x()-self.side/2, self.position.y()-self.side/2, self.side, self.side)
        painter.drawRect(r)
    def get_bounding_rect(self):
        return QRectF(self.position.x()-self.side/2, self.position.y()-self.side/2, self.side, self.side)
    def contains(self, point): return self.get_bounding_rect().contains(point)
    def resize(self, dw, dh):
        delta = max(abs(dw), abs(dh))
        if dw < 0 or dh < 0: delta = -delta
        new_side = self.side + delta
        if new_side >= 2:
            old = self.side
            self.side = new_side
            if not self.check_bounds():
                self.side = old
                return False
            return True
        return False
    def get_size_params(self): return {"side": self.side}
    def set_size_params(self, params):
        s = params.get("side")
        if s is not None and s >= 2:
            self.side = s
            self.center_in_bounds()
            return True
        return False

# Прямоугольник
class Rectangle(Shape):
    def __init__(self, center, width=40, height=30, color=None):
        super().__init__(center, color if color else QColor(0,0,255))
        self.width, self.height = width, height
    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        if self.selected: painter.setPen(QPen(Qt.red, 2))
        r = QRectF(self.position.x()-self.width/2, self.position.y()-self.height/2,
                   self.width, self.height)
        painter.drawRect(r)
    def get_bounding_rect(self):
        return QRectF(self.position.x()-self.width/2, self.position.y()-self.height/2,
                      self.width, self.height)
    def contains(self, point): return self.get_bounding_rect().contains(point)
    def resize(self, dw, dh):
        nw, nh = self.width+dw, self.height+dh
        if nw >= 2 and nh >= 2:
            old_w, old_h = self.width, self.height
            self.width, self.height = nw, nh
            if not self.check_bounds():
                self.width, self.height = old_w, old_h
                return False
            return True
        return False
    def get_size_params(self): return {"width": self.width, "height": self.height}
    def set_size_params(self, params):
        w = params.get("width"); h = params.get("height")
        if w is not None and h is not None and w >= 2 and h >= 2:
            self.width, self.height = w, h
            self.center_in_bounds()
            return True
        return False

# Эллипс
class Ellipse(Rectangle):
    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        if self.selected: painter.setPen(QPen(Qt.red, 2))
        r = QRectF(self.position.x()-self.width/2, self.position.y()-self.height/2,
                   self.width, self.height)
        painter.drawEllipse(r)

# Треугольник
class Triangle(Shape):
    def __init__(self, center, base=40, height=40, color=None):
        super().__init__(center, color if color else QColor(0,0,255))
        self.base, self.height = base, height
        self.points = self._calc_points()
    def _calc_points(self):
        cx, cy = self.position.x(), self.position.y()
        top = QPointF(cx, cy - self.height/2)
        bl = QPointF(cx - self.base/2, cy + self.height/2)
        br = QPointF(cx + self.base/2, cy + self.height/2)
        return [top, bl, br]
    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        if self.selected: painter.setPen(QPen(Qt.red, 2))
        painter.drawPolygon(QPolygonF(self.points))
    def get_bounding_rect(self):
        xs = [p.x() for p in self.points]
        ys = [p.y() for p in self.points]
        return QRectF(min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys))
    def contains(self, point):
        return QPolygonF(self.points).containsPoint(point, Qt.OddEvenFill)
    def resize(self, dw, dh):
        nb, nh = self.base+dw, self.height+dh
        if nb >= 5 and nh >= 5:
            old_b, old_h = self.base, self.height
            old_pts = self.points.copy()
            self.base, self.height = nb, nh
            self.points = self._calc_points()
            if not self.check_bounds():
                self.base, self.height = old_b, old_h
                self.points = old_pts
                return False
            return True
        return False
    def move(self, dx, dy):
        old_pos = self.position
        old_pts = self.points.copy()
        self.position += QPointF(dx, dy)
        self.points = self._calc_points()
        if self.check_bounds(): return True
        self.position = old_pos
        self.points = old_pts
        return False
    def check_bounds(self, new_pos=None):
        if self.bounds is None: return True
        for p in self.points:
            if not (self.bounds.left() <= p.x() <= self.bounds.right() and
                    self.bounds.top() <= p.y() <= self.bounds.bottom()):
                return False
        return True
    def center_in_bounds(self):
        if self.bounds is None: return
        rect = self.get_bounding_rect()
        if rect is None: return
        dx = dy = 0
        if rect.left() < self.bounds.left(): dx = self.bounds.left() - rect.left()
        if rect.top() < self.bounds.top(): dy = self.bounds.top() - rect.top()
        if rect.right() > self.bounds.right(): dx = self.bounds.right() - rect.right()
        if rect.bottom() > self.bounds.bottom(): dy = self.bounds.bottom() - rect.bottom()
        if dx != 0 or dy != 0: self.move(dx, dy)
    def get_size_params(self): return {"base": self.base, "height": self.height}
    def set_size_params(self, params):
        b = params.get("base"); h = params.get("height")
        if b is not None and h is not None and b >= 5 and h >= 5:
            self.base, self.height = b, h
            self.points = self._calc_points()
            self.center_in_bounds()
            return True
        return False

# Обычная линия
class Line(Shape):
    def __init__(self, start_point, end_point, color=None):
        super().__init__(start_point, color if color else QColor(0,0,255))
        self.end_point = end_point
        self.width = 2
    def draw(self, painter):
        painter.setPen(QPen(self.color, self.width))
        if self.selected: painter.setPen(QPen(Qt.red, self.width+1))
        painter.drawLine(self.position, self.end_point)
    def get_bounding_rect(self):
        if self.position is None or self.end_point is None:
            return QRectF(0,0,0,0)
        x1, y1 = self.position.x(), self.position.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        return QRectF(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
    def contains(self, point):
        if self.position is None or self.end_point is None: return False
        a, b = self.position, self.end_point
        ab = b - a
        denom = ab.x()*ab.x() + ab.y()*ab.y() + 1e-10
        t = ((point.x()-a.x())*ab.x() + (point.y()-a.y())*ab.y()) / denom
        t = max(0, min(1, t))
        proj = a + ab * t
        return math.hypot(point.x()-proj.x(), point.y()-proj.y()) <= 5
    def get_center(self):
        return QPointF((self.position.x()+self.end_point.x())/2, (self.position.y()+self.end_point.y())/2)
    def resize(self, dw, dh):
        if self.position is None or self.end_point is None: return False
        center = self.get_center()
        half = QPointF((self.end_point.x()-self.position.x())/2, (self.end_point.y()-self.position.y())/2)
        cur_len = math.hypot(half.x(), half.y())*2
        delta = max(abs(dw), abs(dh))
        if dw < 0 or dh < 0: delta = -delta
        new_len = cur_len + delta
        if new_len < 4: return False
        if cur_len > 0:
            scale = new_len / cur_len
            new_half = QPointF(half.x()*scale, half.y()*scale)
        else:
            new_half = QPointF(10,0)
        new_start = QPointF(center.x()-new_half.x(), center.y()-new_half.y())
        new_end   = QPointF(center.x()+new_half.x(), center.y()+new_half.y())
        old_s, old_e = self.position, self.end_point
        self.position, self.end_point = new_start, new_end
        if not self.check_bounds():
            self.position, self.end_point = old_s, old_e
            return False
        return True
    def move(self, dx, dy):
        if self.position is None or self.end_point is None: return False
        ns = self.position + QPointF(dx, dy)
        ne = self.end_point + QPointF(dx, dy)
        old_s, old_e = self.position, self.end_point
        self.position, self.end_point = ns, ne
        if not self.check_bounds():
            self.position, self.end_point = old_s, old_e
            return False
        return True
    def check_bounds(self, new_pos=None, new_end=None):
        if self.bounds is None: return True
        s, e = self.position, self.end_point
        if s is None or e is None: return False
        return (self.bounds.left() <= s.x() <= self.bounds.right() and
                self.bounds.top() <= s.y() <= self.bounds.bottom() and
                self.bounds.left() <= e.x() <= self.bounds.right() and
                self.bounds.top() <= e.y() <= self.bounds.bottom())
    def center_in_bounds(self):
        if self.bounds is None: return
        rect = self.get_bounding_rect()
        if rect is None: return
        dx = dy = 0
        if rect.left() < self.bounds.left(): dx = self.bounds.left() - rect.left()
        if rect.top() < self.bounds.top(): dy = self.bounds.top() - rect.top()
        if rect.right() > self.bounds.right(): dx = self.bounds.right() - rect.right()
        if rect.bottom() > self.bounds.bottom(): dy = self.bounds.bottom() - rect.bottom()
        if dx != 0 or dy != 0:
            self.position += QPointF(dx, dy)
            self.end_point += QPointF(dx, dy)
    def get_size_params(self):
        if self.position is None or self.end_point is None:
            return {"length": 10, "angle": 0}
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
            half_len = length/2
            dx = half_len * math.cos(rad)
            dy = half_len * math.sin(rad)
            new_start = QPointF(center.x()-dx, center.y()-dy)
            new_end   = QPointF(center.x()+dx, center.y()+dy)
            old_s, old_e = self.position, self.end_point
            self.position, self.end_point = new_start, new_end
            if not self.check_bounds():
                self.position, self.end_point = old_s, old_e
                return False
            return True
        return False
    def save(self):
        data = super().save()
        data.update({"start_x": self.position.x(), "start_y": self.position.y(),
                     "end_x": self.end_point.x(), "end_y": self.end_point.y()})
        return data
    def load(self, data):
        super().load(data)
        self.end_point = QPointF(data.get("end_x", 0), data.get("end_y", 0))
        self.set_size_params(data)
        if self.bounds is not None:
            self.center_in_bounds()

# Стрелка (Arrow) – наблюдает за перемещением источника
class Arrow(Shape):
    def __init__(self, source, target, color=None):
        super().__init__(QPointF(0,0), color if color else QColor(255,0,0))
        self.source = source
        self.target = target
        self.width = 2
    def draw(self, painter):
        if self.source is None or self.target is None:
            return
        start = self.source.position
        end = self.target.position
        painter.setPen(QPen(self.color, self.width))
        painter.drawLine(start, end)
        # Рисуем наконечник стрелки
        angle = math.atan2(end.y() - start.y(), end.x() - start.x())
        arrow_size = 10
        p1 = end - QPointF(arrow_size * math.cos(angle - math.pi/6),
                           arrow_size * math.sin(angle - math.pi/6))
        p2 = end - QPointF(arrow_size * math.cos(angle + math.pi/6),
                           arrow_size * math.sin(angle + math.pi/6))
        painter.drawLine(end, p1)
        painter.drawLine(end, p2)
        if self.selected:
            painter.setPen(QPen(Qt.red, 2, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            rect = self.get_bounding_rect()
            if rect:
                painter.drawRect(rect)
    def get_bounding_rect(self):
        if self.source is None or self.target is None:
            return QRectF(0,0,0,0)
        s = self.source.position
        e = self.target.position
        return QRectF(min(s.x(), e.x()), min(s.y(), e.y()),
                      abs(e.x()-s.x()), abs(e.y()-s.y()))
    def contains(self, point):
        if self.source is None or self.target is None:
            return False
        a = self.source.position
        b = self.target.position
        ab = b - a
        denom = ab.x()*ab.x() + ab.y()*ab.y() + 1e-10
        t = ((point.x()-a.x())*ab.x() + (point.y()-a.y())*ab.y()) / denom
        t = max(0, min(1, t))
        proj = a + ab * t
        return math.hypot(point.x()-proj.x(), point.y()-proj.y()) <= 8
    def move(self, dx, dy):
        # Стрелка не перемещается сама, только её источник и цель
        return True
    def resize(self, dw, dh): return True
    def set_selected(self, selected):
        self.selected = selected
    def get_size_params(self): return {}
    def set_size_params(self, params): pass
    def center_in_bounds(self): pass
    def save(self):
        return {
            "type": "Arrow",
            "source_idx": self.container_index(self.source) if hasattr(self, 'container_index') else -1,
            "target_idx": self.container_index(self.target) if hasattr(self, 'container_index') else -1,
            "color_r": self.color.red(), "color_g": self.color.green(),
            "color_b": self.color.blue(), "color_a": self.color.alpha()
        }
    def load(self, data):
        self.color = QColor(data.get("color_r", 255), data.get("color_g", 0),
                            data.get("color_b", 0), data.get("color_a", 255))

# Группа (Composite)
class Group(Shape):
    def __init__(self, position=None, color=None):
        if position is None: position = QPointF(0,0)
        super().__init__(position, color if color else QColor(0,255,0))
        self.shapes = []
        self._bounds_cache = None
    def add(self, shape): self.shapes.append(shape); self._update_bounds_cache()
    def remove(self, shape):
        if shape in self.shapes: self.shapes.remove(shape); self._update_bounds_cache()
    def get_children(self): return self.shapes
    def _update_bounds_cache(self):
        if not self.shapes:
            self._bounds_cache = QRectF(self.position.x(), self.position.y(), 0, 0)
            return
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        for s in self.shapes:
            r = s.get_bounding_rect()
            if r is None: continue
            min_x = min(min_x, r.left())
            min_y = min(min_y, r.top())
            max_x = max(max_x, r.right())
            max_y = max(max_y, r.bottom())
        self._bounds_cache = QRectF(min_x, min_y, max_x-min_x, max_y-min_y)
        self.position = QPointF(self._bounds_cache.center().x(), self._bounds_cache.center().y())
    def get_bounding_rect(self):
        if not self.shapes: return QRectF(self.position.x(), self.position.y(), 0, 0)
        if self._bounds_cache is None: self._update_bounds_cache()
        return self._bounds_cache
    def draw(self, painter):
        for s in self.shapes: s.draw(painter)
        if self.selected:
            painter.setPen(QPen(Qt.red, 2, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.get_bounding_rect())
    def contains(self, point):
        for s in self.shapes:
            if s.contains(point): return True
        return False
    def move(self, dx, dy):
        for s in self.shapes: s.move(dx, dy)
        self._update_bounds_cache()
        return self.check_bounds()
    def resize(self, dw, dh):
        old_rect = self.get_bounding_rect()
        if old_rect.width() <= 0 or old_rect.height() <= 0: return False
        scale_x = (old_rect.width() + dw) / old_rect.width()
        scale_y = (old_rect.height() + dh) / old_rect.height()
        if scale_x <= 0 or scale_y <= 0: return False
        for s in self.shapes:
            rect = s.get_bounding_rect()
            rel_x = (rect.center().x() - old_rect.center().x()) / old_rect.width()
            rel_y = (rect.center().y() - old_rect.center().y()) / old_rect.height()
            new_cx = old_rect.center().x() + rel_x * (old_rect.width() + dw)
            new_cy = old_rect.center().y() + rel_y * (old_rect.height() + dh)
            s.position = QPointF(new_cx, new_cy)
            s.resize(dw * rel_x, dh * rel_y)
        self._update_bounds_cache()
        return self.check_bounds()
    def check_bounds(self, new_pos=None):
        if self.bounds is None: return True
        r = self.get_bounding_rect()
        if r is None: return False
        return (r.left() >= self.bounds.left() and r.top() >= self.bounds.top() and
                r.right() <= self.bounds.right() and r.bottom() <= self.bounds.bottom())
    def set_selected(self, selected):
        self.selected = selected
        for s in self.shapes: s.set_selected(selected)
    def get_size_params(self): return {"count": len(self.shapes)}
    def set_size_params(self, params): pass
    def save(self):
        return {
            "type": "Group",
            "x": self.position.x(), "y": self.position.y(),
            "color_r": self.color.red(), "color_g": self.color.green(),
            "color_b": self.color.blue(), "color_a": self.color.alpha(),
            "children": [ch.save() for ch in self.shapes]
        }
    def load(self, data):
        self.position = QPointF(data.get("x",0), data.get("y",0))
        self.color = QColor(data.get("color_r",0), data.get("color_g",0),
                            data.get("color_b",255), data.get("color_a",255))

# Фабрика
class ShapeFactory:
    _shapes = {
        "Circle": Circle, "Square": Square, "Rectangle": Rectangle,
        "Ellipse": Ellipse, "Triangle": Triangle, "Line": Line, "Group": Group
    }
    @classmethod
    def create_shape(cls, data):
        t = data.get("type")
        if t == "Group":
            group = Group()
            for child_data in data.get("children", []):
                group.add(cls.create_shape(child_data))
            group.load(data)
            return group
        if t == "Line":
            start = QPointF(data.get("start_x",0), data.get("start_y",0))
            end   = QPointF(data.get("end_x",0), data.get("end_y",0))
            line = Line(start, end)
            line.load(data)
            return line
        shape_class = cls._shapes[t]
        shape = shape_class(QPointF(0,0))
        shape.load(data)
        return shape

# КОНТЕЙНЕР С ПОДДЕРЖКОЙ НАБЛЮДАТЕЛЕЙ (OBSERVER)
class ShapeContainer(QObject):
    changed = pyqtSignal()
    selection_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.shapes = []
        self.selected_indices = set()
        self.arrows = []

    def add(self, shape):
        self.shapes.append(shape)
        self.changed.emit()
        return len(self.shapes)-1

    def add_arrow(self, arrow):
        self.arrows.append(arrow)
        self.changed.emit()

    def remove(self, idx):
        if 0 <= idx < len(self.shapes):
            if idx in self.selected_indices:
                self.selected_indices.remove(idx)
            new_sel = set()
            for i in self.selected_indices:
                if i > idx: new_sel.add(i-1)
                elif i < idx: new_sel.add(i)
            self.selected_indices = new_sel
            removed = self.shapes.pop(idx)
            # Удаляем стрелки, связанные с удалённым объектом
            self.arrows = [a for a in self.arrows if a.source != removed and a.target != removed]
            self.changed.emit()

    def remove_arrow(self, arrow):
        if arrow in self.arrows:
            self.arrows.remove(arrow)
            self.changed.emit()

    def get(self, idx): return self.shapes[idx] if 0<=idx<len(self.shapes) else None
    def get_all(self): return self.shapes
    def get_all_arrows(self): return self.arrows

    def clear_selection(self):
        for i in self.selected_indices:
            self.shapes[i].set_selected(False)
        for a in self.arrows:
            a.set_selected(False)
        self.selected_indices.clear()
        self.selection_changed.emit()

    def select_one(self, idx, add=False, add_to_selection=None):
        if add_to_selection is not None:
            add = add_to_selection
        if add:
            if idx in self.selected_indices:
                self.shapes[idx].set_selected(False)
                self.selected_indices.remove(idx)
            else:
                self.shapes[idx].set_selected(True)
                self.selected_indices.add(idx)
        else:
            self.clear_selection()
            if 0 <= idx < len(self.shapes):
                self.shapes[idx].set_selected(True)
                self.selected_indices.add(idx)
        self.selection_changed.emit()

    def select_shape(self, shape, add=False):
        if shape in self.shapes:
            idx = self.shapes.index(shape)
            self.select_one(idx, add)
        elif shape in self.arrows:
            self.clear_selection()
            shape.set_selected(True)
            self.selection_changed.emit()

    def get_selected(self):
        selected = [self.shapes[i] for i in self.selected_indices]
        for a in self.arrows:
            if a.selected:
                selected.append(a)
        return selected

    def is_selected(self, shape):
        if shape in self.shapes:
            return self.shapes.index(shape) in self.selected_indices
        return shape.selected

    def move_selected(self, dx, dy):
        moved_shapes = []
        for i in self.selected_indices:
            self.shapes[i].move(dx, dy)
            moved_shapes.append(self.shapes[i])
        # Для стрелок: при перемещении источника, перемещаем цель
        for arrow in self.arrows:
            if arrow.source in moved_shapes:
                if arrow.target and arrow.target in self.shapes:
                    arrow.target.move(dx, dy)
        self.changed.emit()

    def resize_selected(self, dw, dh):
        for i in self.selected_indices:
            self.shapes[i].resize(dw, dh)
        self.changed.emit()

    def set_color_to_selected(self, color):
        for i in self.selected_indices:
            self.shapes[i].set_color(color)
        for a in self.arrows:
            if a.selected:
                a.set_color(color)
        self.changed.emit()

    def delete_selected(self):
        indices = sorted(self.selected_indices, reverse=True)
        for idx in indices:
            self.remove(idx)
        to_remove = [a for a in self.arrows if a.selected]
        for a in to_remove:
            self.arrows.remove(a)
        self.selected_indices.clear()
        self.changed.emit()

    def group_selected(self):
        sel = self.get_selected()
        sel_shapes = [s for s in sel if not isinstance(s, Arrow)]
        if len(sel_shapes) < 2:
            QMessageBox.information(None, "Информация", "Выделите минимум 2 объекта")
            return
        g = Group()
        for s in sel_shapes:
            g.add(s)
        indices_to_remove = [i for i, s in enumerate(self.shapes) if s in sel_shapes]
        for idx in sorted(indices_to_remove, reverse=True):
            self.remove(idx)
        self.add(g)
        self.clear_selection()
        self.select_one(len(self.shapes)-1)

    def ungroup_selected(self):
        sel = self.get_selected()
        groups = [s for s in sel if isinstance(s, Group)]
        if len(groups) != 1:
            QMessageBox.information(None, "Информация", "Выделите одну группу")
            return
        grp = groups[0]
        idx = None
        for i, s in enumerate(self.shapes):
            if s is grp:
                idx = i
                break
        if idx is None:
            return
        children = grp.get_children()
        self.remove(idx)
        for ch in children:
            ch.set_selected(False)
            self.add(ch)
        self.clear_selection()

    def can_add_arrow(self, source, target):
        if source == target:
            return False
        # Проверка на цикл
        visited = set()
        def depends(a, b):
            if a == b:
                return True
            for arrow in self.arrows:
                if arrow.source == a and arrow.target == b:
                    return True
                if arrow.source == a and depends(arrow.target, b):
                    return True
            return False
        return not depends(target, source)

    def create_arrow(self, source, target):
        if not self.can_add_arrow(source, target):
            QMessageBox.warning(None, "Ошибка", "Нельзя создать стрелку: возникнет цикл")
            return None
        arrow = Arrow(source, target)
        self.add_arrow(arrow)
        return arrow

    def save_to_file(self, filename):
        shape_to_idx = {id(s): i for i, s in enumerate(self.shapes)}
        arrow_data = []
        for a in self.arrows:
            arrow_data.append({
                "type": "Arrow",
                "source_idx": shape_to_idx.get(id(a.source), -1),
                "target_idx": shape_to_idx.get(id(a.target), -1),
                "color_r": a.color.red(), "color_g": a.color.green(),
                "color_b": a.color.blue(), "color_a": a.color.alpha()
            })
        data = {"version": 1,
                "objects": [s.save() for s in self.shapes],
                "arrows": arrow_data}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.shapes = []
        self.selected_indices.clear()
        self.arrows = []
        for obj_data in data.get("objects", []):
            self.shapes.append(ShapeFactory.create_shape(obj_data))
        for arr_data in data.get("arrows", []):
            src_idx = arr_data.get("source_idx", -1)
            tgt_idx = arr_data.get("target_idx", -1)
            if 0 <= src_idx < len(self.shapes) and 0 <= tgt_idx < len(self.shapes):
                arrow = Arrow(self.shapes[src_idx], self.shapes[tgt_idx])
                arrow.color = QColor(arr_data.get("color_r",255), arr_data.get("color_g",0),
                                     arr_data.get("color_b",0), arr_data.get("color_a",255))
                self.arrows.append(arrow)
        self.changed.emit()

# ДЕРЕВО ОБЪЕКТОВ (TreeView) – НАБЛЮДАТЕЛЬ
class ObjectTreeWidget(QTreeWidget):
    def __init__(self, container, parent=None):
        super().__init__(parent)
        self.container = container
        self.setHeaderLabel("Объекты сцены")
        self.itemClicked.connect(self.on_item_clicked)
        self.container.changed.connect(self.rebuild_tree)
        self.container.selection_changed.connect(self.on_selection_changed)
        self.rebuild_tree()

    def rebuild_tree(self):
        self.clear()
        for shape in self.container.get_all():
            self._add_shape_to_tree(None, shape)
        for arrow in self.container.get_all_arrows():
            item = QTreeWidgetItem([f"Стрелка: {self._get_obj_name(arrow.source)} → {self._get_obj_name(arrow.target)}"])
            item.setData(0, Qt.UserRole, arrow)
            self.addTopLevelItem(item)

    def _add_shape_to_tree(self, parent_item, shape):
        name = self._get_obj_name(shape)
        if parent_item is None:
            item = QTreeWidgetItem([name])
            item.setData(0, Qt.UserRole, shape)
            self.addTopLevelItem(item)
        else:
            item = QTreeWidgetItem(parent_item, [name])
            item.setData(0, Qt.UserRole, shape)
            parent_item.addChild(item)
        if isinstance(shape, Group):
            for child in shape.get_children():
                self._add_shape_to_tree(item, child)

    def _get_obj_name(self, obj):
        if isinstance(obj, Circle): return f"Круг {id(obj)%1000}"
        if isinstance(obj, Square): return f"Квадрат {id(obj)%1000}"
        if isinstance(obj, Rectangle): return f"Прямоугольник {id(obj)%1000}"
        if isinstance(obj, Ellipse): return f"Эллипс {id(obj)%1000}"
        if isinstance(obj, Triangle): return f"Треугольник {id(obj)%1000}"
        if isinstance(obj, Line): return f"Линия {id(obj)%1000}"
        if isinstance(obj, Group): return f"Группа {id(obj)%1000}"
        return "Объект"

    def on_item_clicked(self, item, column):
        obj = item.data(0, Qt.UserRole)
        if obj:
            self.container.select_shape(obj, add=False)

    def on_selection_changed(self):
        self._update_tree_selection()

    def _update_tree_selection(self):
        def recurse(item):
            obj = item.data(0, Qt.UserRole)
            if obj and self.container.is_selected(obj):
                self.setCurrentItem(item)
                return True
            for i in range(item.childCount()):
                if recurse(item.child(i)):
                    return True
            return False
        for i in range(self.topLevelItemCount()):
            recurse(self.topLevelItem(i))

# Диалог изменения размера
class ResizeDialog(QDialog):
    def __init__(self, shape, parent=None):
        super().__init__(parent)
        self.shape = shape
        self.setWindowTitle("Изменение размера")
        layout = QVBoxLayout()
        self.params = shape.get_size_params()
        self.inputs = {}
        for key, val in self.params.items():
            if key == "count": continue
            layout.addWidget(QLabel(self._name(key)))
            e = QLineEdit(str(int(val) if val==int(val) else val))
            layout.addWidget(e)
            self.inputs[key] = e
        btn_ok = QPushButton("OK"); btn_ok.clicked.connect(self.accept); layout.addWidget(btn_ok)
        btn_cancel = QPushButton("Отмена"); btn_cancel.clicked.connect(self.reject); layout.addWidget(btn_cancel)
        self.setLayout(layout)
    def _name(self, key):
        d = {"radius":"Радиус","side":"Сторона","width":"Ширина","height":"Высота",
             "base":"Основание","length":"Длина","angle":"Угол"}
        return d.get(key, key)
    def get_new_params(self):
        res = {}
        for key, ed in self.inputs.items():
            try:
                v = float(ed.text())
                if key != "angle" and v < 2:
                    QMessageBox.warning(self, "Ошибка", f"{self._name(key)} >= 2")
                    return None
                res[key] = v
            except:
                QMessageBox.warning(self, "Ошибка", "Введите число")
                return None
        return res

# Диалог создания стрелки
class AddArrowDialog(QDialog):
    def __init__(self, container, parent=None):
        super().__init__(parent)
        self.container = container
        self.setWindowTitle("Добавить стрелку")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Выберите исходный объект:"))
        self.source_combo = QComboBox()
        layout.addWidget(self.source_combo)
        layout.addWidget(QLabel("Выберите целевой объект:"))
        self.target_combo = QComboBox()
        layout.addWidget(self.target_combo)
        self._fill_combos()
        btn_ok = QPushButton("OK"); btn_ok.clicked.connect(self.accept); layout.addWidget(btn_ok)
        btn_cancel = QPushButton("Отмена"); btn_cancel.clicked.connect(self.reject); layout.addWidget(btn_cancel)
        self.setLayout(layout)
    def _fill_combos(self):
        self.source_combo.clear()
        self.target_combo.clear()
        for shape in self.container.get_all():
            name = f"{shape.__class__.__name__} {id(shape)%1000}"
            self.source_combo.addItem(name, shape)
            self.target_combo.addItem(name, shape)
    def get_arrow(self):
        src = self.source_combo.currentData()
        tgt = self.target_combo.currentData()
        return src, tgt

# Область рисования
class SceneWidget(QWidget):
    def __init__(self, container, parent=None):
        super().__init__(parent)
        self.container = container
        self.current_tool = 'circle'
        self.temp_line_start = None
        self.setMinimumSize(400,300)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.dragging = False
        self.drag_start = None
        self.dragged_indices = set()
    def set_tool(self, t):
        self.current_tool = t
        if t != 'line':
            self.temp_line_start = None
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), Qt.white)
        p.setPen(Qt.gray); p.drawRect(self.rect().adjusted(0,0,-1,-1))
        bounds = QRectF(0,0,self.width(),self.height())
        for s in self.container.get_all():
            s.set_bounds(bounds)
            s.draw(p)
        for a in self.container.get_all_arrows():
            a.set_bounds(bounds)
            a.draw(p)
    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton: return
        pos = e.pos()
        # Проверяем сначала стрелки
        for a in self.container.get_all_arrows():
            if a.contains(pos):
                self.container.clear_selection()
                a.set_selected(True)
                self.dragging = True
                self.drag_start = pos
                self.dragged_indices = set()
                self.update()
                return
        shapes = self.container.get_all()
        idx = -1
        for i in range(len(shapes)-1, -1, -1):
            if shapes[i].contains(pos):
                idx = i
                break
        if idx != -1:
            if e.modifiers() & Qt.ControlModifier:
                self.container.select_one(idx, add=True)
            else:
                self.container.select_one(idx, add=False)
            self.update()
            self.dragging = True
            self.drag_start = pos
            self.dragged_indices = set(self.container.selected_indices)
        else:
            self.container.clear_selection()
            self.update()
            bounds = QRectF(0,0,self.width(),self.height())
            if self.current_tool == 'line':
                if self.temp_line_start is None:
                    self.temp_line_start = pos
                else:
                    line = Line(self.temp_line_start, pos, QColor(0,0,255))
                    line.set_bounds(bounds)
                    if not line.check_bounds():
                        end = line.end_point
                        end.setX(max(0, min(end.x(), bounds.right())))
                        end.setY(max(0, min(end.y(), bounds.bottom())))
                        line.end_point = end
                    self.container.add(line)
                    self.temp_line_start = None
                    self.update()
            else:
                shape = None
                if self.current_tool == 'circle': shape = Circle(pos,20,QColor(0,0,255))
                elif self.current_tool == 'square': shape = Square(pos,40,QColor(0,0,255))
                elif self.current_tool == 'rectangle': shape = Rectangle(pos,40,30,QColor(0,0,255))
                elif self.current_tool == 'ellipse': shape = Ellipse(pos,40,30,QColor(0,0,255))
                elif self.current_tool == 'triangle': shape = Triangle(pos,40,40,QColor(0,0,255))
                if shape:
                    shape.set_bounds(bounds)
                    if not shape.check_bounds():
                        rect = shape.get_bounding_rect()
                        dx = dy = 0
                        if rect.left() < 0: dx = -rect.left()
                        if rect.top() < 0: dy = -rect.top()
                        if rect.right() > bounds.right(): dx = bounds.right() - rect.right()
                        if rect.bottom() > bounds.bottom(): dy = bounds.bottom() - rect.bottom()
                        shape.move(dx, dy)
                    self.container.add(shape)
                    self.update()
    def mouseMoveEvent(self, e):
        if self.dragging and self.drag_start is not None:
            delta = e.pos() - self.drag_start
            if delta.x() != 0 or delta.y() != 0:
                self.container.move_selected(delta.x(), delta.y())
                self.drag_start = e.pos()
                self.update()
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = False
            self.drag_start = None
            self.dragged_indices.clear()
    def mouseDoubleClickEvent(self, e):
        pos = e.pos()
        shapes = self.container.get_all()
        for i in range(len(shapes)-1, -1, -1):
            if shapes[i].contains(pos):
                if not shapes[i].selected:
                    self.container.select_one(i, add=False)
                    self.update()
                sel = self.container.get_selected()
                if len(sel) == 1:
                    dlg = ResizeDialog(sel[0], self)
                    if dlg.exec_() == QDialog.Accepted:
                        newp = dlg.get_new_params()
                        if newp and sel[0].set_size_params(newp):
                            self.update()
                break
    def keyPressEvent(self, e):
        key = e.key()
        mod = e.modifiers()
        if key == Qt.Key_G and (mod & Qt.ControlModifier) and (mod & Qt.ShiftModifier):
            self.container.ungroup_selected(); self.update(); return
        if key == Qt.Key_G and (mod & Qt.ControlModifier):
            self.container.group_selected(); self.update(); return
        if key == Qt.Key_A and (mod & Qt.ControlModifier):
            dlg = AddArrowDialog(self.container, self)
            if dlg.exec_() == QDialog.Accepted:
                src, tgt = dlg.get_arrow()
                if src and tgt:
                    self.container.create_arrow(src, tgt)
                    self.update()
            return
        selected = self.container.get_selected()
        if not selected: return
        step = 5
        if mod & Qt.ControlModifier:
            if key == Qt.Key_Left: self.container.resize_selected(-step,0)
            elif key == Qt.Key_Right: self.container.resize_selected(step,0)
            elif key == Qt.Key_Up: self.container.resize_selected(0,-step)
            elif key == Qt.Key_Down: self.container.resize_selected(0,step)
        else:
            if key == Qt.Key_Left: self.container.move_selected(-step,0)
            elif key == Qt.Key_Right: self.container.move_selected(step,0)
            elif key == Qt.Key_Up: self.container.move_selected(0,-step)
            elif key == Qt.Key_Down: self.container.move_selected(0,step)
            elif key in (Qt.Key_Delete, Qt.Key_Backspace): self.container.delete_selected()
            elif key == Qt.Key_C:
                col = QColorDialog.getColor(selected[0].get_color(), self, "Выберите цвет")
                if col.isValid(): self.container.set_color_to_selected(col)
        self.update()
    def resizeEvent(self, e):
        bounds = QRectF(0,0,self.width(),self.height())
        for s in self.container.get_all():
            s.set_bounds(bounds)
            self._set_bounds_recursive(s, bounds)
        for a in self.container.get_all_arrows():
            a.set_bounds(bounds)
        self.update()
    def _set_bounds_recursive(self, shape, bounds):
        shape.set_bounds(bounds)
        if isinstance(shape, Group):
            for ch in shape.get_children():
                self._set_bounds_recursive(ch, bounds)

# Главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Векторный редактор - Лабораторная 7 (дерево, стрелки)")
        self.setGeometry(100,100,1000,700)
        self.container = ShapeContainer()
        splitter = QSplitter(Qt.Horizontal)
        self.tree = ObjectTreeWidget(self.container)
        splitter.addWidget(self.tree)
        self.scene = SceneWidget(self.container)
        splitter.addWidget(self.scene)
        splitter.setSizes([250, 750])
        self.setCentralWidget(splitter)
        self.create_toolbar()
        self.create_menu()
        self.statusBar().showMessage("Готов")
    def create_toolbar(self):
        tb = self.addToolBar("Инструменты")
        tb.setMovable(False)
        tools = {"Круг":"circle","Квадрат":"square","Прямоугольник":"rectangle",
                 "Эллипс":"ellipse","Треугольник":"triangle","Линия":"line"}
        for name, tool in tools.items():
            a = QAction(name, self)
            a.triggered.connect(lambda ch, t=tool: self.scene.set_tool(t))
            tb.addAction(a)
        tb.addSeparator()
        a = QAction("Изменить цвет", self); a.triggered.connect(self.change_color); tb.addAction(a)
        a = QAction("Удалить", self); a.triggered.connect(self.delete_selected); tb.addAction(a)
        tb.addSeparator()
        a = QAction("Увеличить размер", self); a.triggered.connect(lambda: self.resize_sel(5,5)); tb.addAction(a)
        a = QAction("Уменьшить размер", self); a.triggered.connect(lambda: self.resize_sel(-5,-5)); tb.addAction(a)
        tb.addSeparator()
        a = QAction("Группировать (Ctrl+G)", self); a.triggered.connect(self.group); tb.addAction(a)
        a = QAction("Разгруппировать (Ctrl+Shift+G)", self); a.triggered.connect(self.ungroup); tb.addAction(a)
        a = QAction("Добавить стрелку (Ctrl+A)", self); a.triggered.connect(self.add_arrow); tb.addAction(a)
    def create_menu(self):
        mb = self.menuBar()
        fm = mb.addMenu("Файл")
        a = QAction("Сохранить...", self); a.triggered.connect(self.save); fm.addAction(a)
        a = QAction("Загрузить...", self); a.triggered.connect(self.load); fm.addAction(a)
        fm.addSeparator(); a = QAction("Выход", self); a.triggered.connect(self.close); fm.addAction(a)
        em = mb.addMenu("Правка")
        a = QAction("Изменить цвет", self); a.triggered.connect(self.change_color); em.addAction(a)
        a = QAction("Удалить", self); a.triggered.connect(self.delete_selected); em.addAction(a)
        em.addSeparator(); a = QAction("Группировать", self); a.triggered.connect(self.group); em.addAction(a)
        a = QAction("Разгруппировать", self); a.triggered.connect(self.ungroup); em.addAction(a)
        a = QAction("Добавить стрелку", self); a.triggered.connect(self.add_arrow); em.addAction(a)
        hm = mb.addMenu("Справка")
        a = QAction("Истории пользователей", self); a.triggered.connect(self.show_stories); hm.addAction(a)
    def change_color(self):
        sel = self.container.get_selected()
        if sel:
            col = QColorDialog.getColor(sel[0].get_color(), self, "Выберите цвет")
            if col.isValid(): self.container.set_color_to_selected(col); self.scene.update()
    def delete_selected(self): self.container.delete_selected(); self.scene.update()
    def resize_sel(self, dw, dh): self.container.resize_selected(dw, dh); self.scene.update()
    def group(self): self.container.group_selected(); self.scene.update()
    def ungroup(self): self.container.ungroup_selected(); self.scene.update()
    def add_arrow(self):
        dlg = AddArrowDialog(self.container, self)
        if dlg.exec_() == QDialog.Accepted:
            src, tgt = dlg.get_arrow()
            if src and tgt:
                self.container.create_arrow(src, tgt)
                self.scene.update()
    def save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить проект", "", "JSON (*.json)")
        if path:
            try:
                self.container.save_to_file(path)
                QMessageBox.information(self, "Успех", "Проект сохранён")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {str(e)}")
    def load(self):
        path, _ = QFileDialog.getOpenFileName(self, "Загрузить проект", "", "JSON (*.json)")
        if path:
            try:
                self.container.load_from_file(path)
                bounds = QRectF(0, 0, self.scene.width(), self.scene.height())
                for shape in self.container.get_all():
                    self.scene._set_bounds_recursive(shape, bounds)
                self.scene.update()
                QMessageBox.information(self, "Успех", "Проект загружен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить: {str(e)}")
    def show_stories(self):
        txt = """
        <h3>5 пользовательских историй</h3>
        <b>1. Создать круг и квадрат → сгруппировать → добавить стрелку от группы к кругу</b><br>
        <b>2. Создать две группы и стрелку между ними → переместить исходную группу → целевая движется</b><br>
        <b>3. Создать стрелку А→Б, затем стрелку Б→В → проверить отсутствие цикла</b><br>
        <b>4. Сохранить проект со стрелками, загрузить → проверить работоспособность</b><br>
        <b>5. Выделить объект в дереве → он выделяется на сцене, и наоборот</b>
        """
        QMessageBox.information(self, "Истории пользователей", txt)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())