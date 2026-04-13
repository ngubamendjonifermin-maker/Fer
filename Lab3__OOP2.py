import sys, json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout,
    QLabel, QLineEdit, QSpinBox, QSlider
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from datetime import datetime

ФАЙЛ = Path.home() / ".lab3_mvc.json"

class ABCModel(QObject):
    changed = pyqtSignal()

    МИН, МАКС = 0, 100

    def __init__(self):
        super().__init__()
        self._a = 0
        self._b = 0
        self._c = 100
        self._last_saved = "Нет сохранённых данных"
        self._load()

    @property
    def a(self): return self._a
    @property
    def b(self): return self._b
    @property
    def c(self): return self._c
    @property
    def min_val(self): return self.МИН
    @property
    def max_val(self): return self.МАКС
    @property
    def last_saved(self): return self._last_saved

    def notify(self):
        self.changed.emit()

    def set_a(self, value: int):
        value = max(self.МИН, min(self.МАКС, value))
        new_a = value
        new_b = max(self._b, new_a)
        new_c = max(self._c, new_b)
        self._apply(new_a, new_b, new_c)

    def set_b(self, value: int):
        value = max(self.МИН, min(self.МАКС, value))
        clamped = max(self._a, min(self._c, value))
        self._apply(self._a, clamped, self._c)

    def set_c(self, value: int):
        value = max(self.МИН, min(self.МАКС, value))
        new_c = value
        new_b = min(self._b, new_c)
        new_a = min(self._a, new_b)
        self._apply(new_a, new_b, new_c)

    def _apply(self, a: int, b: int, c: int):
        if a == self._a and b == self._b and c == self._c:
            return
        self._a, self._b, self._c = a, b, c
        self._save()
        self.changed.emit()

    def _save(self):
        """Guarda solo a y c (b no se persiste)."""
        try:
            ФАЙЛ.write_text(
                json.dumps({"a": self._a, "c": self._c})
            )
            hora = datetime.now().strftime("%H:%M:%S")
            self._last_saved = (
                f"Сохранено в {hora}:  "
                f"A={self._a},    C={self._c}"
            )
        except OSError:
            self._last_saved = "Ошибка сохранения"

    def _load(self):
        try:
            data = json.loads(ФАЙЛ.read_text())

            a = int(data.get("a", 0))
            c = int(data.get("c", 100))

            # игнорируем b даже если он есть
            b = a

            self._a, self._b, self._c = a, b, c

        except Exception:
            self._last_saved = "Нет сохранённых данных"


class MainWindow(QMainWindow):
    def __init__(self, model: ABCModel):
        super().__init__()
        self._model = model
        self._updating = False
        self.setWindowTitle("Лаб. 3 – Часть 2: MVC")
        self._build_ui()
        model.changed.connect(self._refresh)
        model.notify()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        grid = QGridLayout(central)
        grid.setSpacing(12)
        grid.setContentsMargins(20, 20, 20, 20)

        grid.addWidget(QLabel("<b>Переменная</b>"), 0, 0)
        grid.addWidget(QLabel("<b>Текст</b>"),       0, 1)
        grid.addWidget(QLabel("<b>Счётчик</b>"),     0, 2)
        grid.addWidget(QLabel("<b>Ползунок</b>"),    0, 3)

        self._rows = {}
        for row, (name, setter) in enumerate([
            ("A", self._model.set_a),
            ("B", self._model.set_b),
            ("C", self._model.set_c),
        ], start=1):
            txt    = QLineEdit()
            spin   = QSpinBox()
            slider = QSlider(Qt.Horizontal)

            for widget in (spin, slider):
                widget.setMinimum(self._model.min_val)
                widget.setMaximum(self._model.max_val)

            grid.addWidget(QLabel(name), row, 0)
            grid.addWidget(txt,          row, 1)
            grid.addWidget(spin,         row, 2)
            grid.addWidget(slider,       row, 3)

            self._rows[name] = (txt, spin, slider)

            txt.editingFinished.connect(
                lambda s=setter, t=txt: self._on_text(s, t))
            spin.valueChanged.connect(
                lambda v, s=setter: self._on_value(s, v))
            slider.valueChanged.connect(
                lambda v, s=setter: self._on_value(s, v))

        self._update_count = 0
        self._count_lbl = QLabel("Количество обновлений: 0")
        grid.addWidget(self._count_lbl, 4, 0, 1, 4)

        self._save_lbl = QLabel("")
        self._save_lbl.setStyleSheet("color: green; font-style: italic;")
        grid.addWidget(self._save_lbl, 5, 0, 1, 4)

    def _on_text(self, setter, txt_widget: QLineEdit):
        try:
            setter(int(txt_widget.text()))
        except ValueError:
            self._refresh()

    def _on_value(self, setter, value: int):
        if not self._updating:
            setter(value)

    def _refresh(self):
        self._update_count += 1
        self._count_lbl.setText(
            f"Количество обновлений: {self._update_count}")
        self._save_lbl.setText(self._model.last_saved)

        self._updating = True
        try:
            values = {"A": self._model.a, "B": self._model.b, "C": self._model.c}
            for name, (txt, spin, slider) in self._rows.items():
                v = values[name]

                # 👇 ВАЖНО: при первом запуске скрываем B
                if name == "B" and self._update_count == 1:
                   txt.setText("")
                   spin.setEnabled(False)
                   slider.setEnabled(False)
                else:
                    txt.setText(str(v))
                    spin.setValue(v)
                    slider.setValue(v)
                    spin.setEnabled(True)
                    slider.setEnabled(True)

        finally:
            self._updating = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = ABCModel()
    win = MainWindow(model)
    win.resize(600, 260)
    win.show()
    sys.exit(app.exec_())