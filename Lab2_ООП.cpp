#include <iostream>
#include <io.h>
#include <fcntl.h>

using namespace std;

class Point {
protected:
    int x, y;

public:
    // Конструктор без параметров
    Point() : x(0), y(0) {
        wcout << L"Point(): конструктор\n";
    }

    // Конструктор с параметрами
    Point(int x, int y) : x(x), y(y) {
        wcout << L"Point(int, int): конструктор\n";
    }

    // Конструктор копирования
    Point(const Point& other) : x(other.x), y(other.y) {
        wcout << L"Point: конструктор копирования\n";
    }

    // виртуальный деструктор
    virtual ~Point() {
        wcout << L"~Point(): деструктор\n";
    }

    // НЕ виртуальный метод
    void print() {
        wcout << L"Point: (" << x << L", " << y << L")\n";
    }

    // ВИРТУАЛЬНЫЙ метод
    virtual void show() {
        wcout << L"Point show(): (" << x << L", " << y << L")\n";
    }
};

class Circle : public Point {
private:
    int radius;

public:
    Circle() : Point(), radius(0) {
        wcout << L"Circle(): конструктор\n";
    }

    Circle(int x, int y, int r) : Point(x, y), radius(r) {
        wcout << L"Circle(int,int,int): конструктор\n";
    }

    ~Circle() {
        wcout << L"~Circle(): деструктор\n";
    }

    // Переопределение без virtual
    void print() {
        wcout << L"Circle print(): radius = " << radius << endl;
        Point::print();
    }

    // Переопределение виртуального метода
    void show() override {
        wcout << L"Circle show(): radius = " << radius << endl;
    }
};

// Через объект
class Line {
private:
    Point start;
    Point end;

public:
    Line(): start(0, 0), end(1, 1) {
        wcout << L"Line():  конструктор\n";
    }
    ~Line() {
        wcout << L"~Line():  деструктор\n";

    }
    void print() {
        wcout << L"Line():\n";
        start.print();
        end.print();

    }
};

// Через указатель
class ShapeWithPointer {
private:
    Point* p;

public:
    ShapeWithPointer() {
        p = new Point(9, 9);
        wcout << L"ShapeWithPointer(): конструктор\n";
    }

    ~ShapeWithPointer() {
        delete p;
        wcout << L"~ShapeWithPointer(): деструктор\n";
    }

    void print() {
        p->print();
    }
};

int main() {
    // Включаем Unicode для консоли
    _setmode(_fileno(stdout), _O_U16TEXT);

    wcout << L"=== 1. НЕ виртуальные методы ===\n";

    Point* p1 = new Circle(1, 2, 10);

    wcout << L"Вызов print():\n";
    p1->print();  // вызовется Point::print()

    delete p1;

    wcout << L"\n=============================\n";

    wcout << L"=== 2. ВИРТУАЛЬНЫЕ методы ===\n";

    Point* p2 = new Circle(3, 4, 20);

    wcout << L"Вызов show():\n";
    p2->show();  // вызовется Circle::show()

    delete p2;

    wcout << L"\n=============================\n";

    wcout << L"=== 3. Прямой вызов ===\n";

    Circle c(5, 6, 30);
    c.print();
    c.show();


    wcout << L"\n=============================\n";
    wcout << L"=== 4. Композиция (объект) ===\n";

    Line l;
    l.print();

    wcout << L"\n=============================\n";
    wcout << L"=== 5. Композиция (указатель) ===\n";

    ShapeWithPointer sp;
    sp.print();

    wcout << L"\n=== Конец программы ===\n";
    return 0;
}