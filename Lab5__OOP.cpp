#include <iostream>
#include <string>
#include <memory>
#include <typeinfo>

using namespace std;

// Верси1: базовые классы
// 1. БАЗОВЫЕ КЛАССЫ (ЖИЗНЕННЫЙ ЦИКЛ + ПОЛИМОРФИЗМ)
class Base {
public:
    Base() {
        cout << "Base::Base() конструктор\n";
        data = new int(0);
    }

    Base(Base* obj) {
        cout << "Base::Base(Base*) конструктор (НЕ стандартный)\n";
        data = new int(*obj->data);
    }
    // Версия 6:исправление конструкторов копирования
    // правильный конструктор копирования
    Base(const Base& obj) {
        cout << "Base::Base(const Base&) КОПИРУЮЩИЙ\n";
        data = new int(*obj.data);
    }

    // виртуальный деструктор
    virtual ~Base() {
        cout << "Base::~Base() ДЕСТРУКТОР\n";
        delete data;
    }

    // НЕВИРТУАЛЬНЫЙ
    void nonVirtualMethod() {
        cout << "\tBase::nonVirtualMethod()\n";
    }

    // ВИРТУАЛЬНЫЙ 
    virtual void virtualMethod() {
        cout << "\tBase::virtualMethod()\n";
    }

    // method1 вызывает method2
    void method1() {
        cout << "\tBase::method1() -> ";
        method2();
    }

    // Меняй virtual для эксперимента
    /*virtual*/ void method2() {
        cout << "Base::method2()\n";
    }

    // Проверка типа 
    virtual string classname() {
        return "Base";
    }

    virtual bool isA(const string& name) {
        return name == "Base";
    }

    int* data;
};



class Desc : public Base {
public:
    Desc() {
        cout << "Desc::Desc() конструктор\n";
        descData = new int(100);
    }

    Desc(Desc* obj) {
        cout << "Desc::Desc(Desc*) конструктор\n";
        descData = new int(*obj->descData);
    }

    Desc(const Desc& obj) : Base(obj) {
        cout << "Desc::Desc(const Desc&) КОПИРУЮЩИЙ\n";
        descData = new int(*obj.descData);
    }

    ~Desc() {
        cout << "Desc::~Desc() ДЕСТРУКТОР\n";
        delete descData;
    }

    // Версия 2: виртуальные и невиртуальные методы 
    void nonVirtualMethod() {
        cout << "\tDesc::nonVirtualMethod()\n";
    }

    void virtualMethod() override {
        cout << "\tDesc::virtualMethod()\n";
    }

    void method2() {
        cout << "\tDesc::method2()\n";
    }
    // Версия 3: приведение типов и RTTI 
    string classname() override {
        return "Desc";
    }

    bool isA(const string& name) override {
        return name == "Desc" || Base::isA(name);
    }

    void onlyForDesc() {
        cout << "\tМетод только Desc\n";
    }

    int* descData;
};

// Версия 4: передача и возврат объектов  
// 2. ПЕРЕДАЧА В ФУНКЦИИ
void func1(Base obj) {
    cout << "--- func1(Base obj) ---\n";
    cout << "Срезка объекта (object slicing!)\n";
}

void func2(Base* obj) {
    cout << "--- func2(Base* obj) ---\n";

    Desc* d = dynamic_cast<Desc*>(obj);
    if (d) {
        cout << "Приведение успешно\n";
        d->onlyForDesc();
    }
    else {
        cout << "Приведение НЕ удалось\n";
    }
}

void func3(Base& obj) {
    cout << "--- func3(Base& obj) ---\n";

    try {
        Desc& d = dynamic_cast<Desc&>(obj);
        cout << "Приведение успешно\n";
        d.onlyForDesc();
    }
    catch (bad_cast&) {
        cout << "bad_cast (не удалось привести)\n";
    }
}


// 3. ВОЗВРАТ ОБЪЕКТОВ
Base f1() {
    static Base b;
    cout << "f1: возврат копии\n";
    return b;
}

Base* f2() {
    static Base b;
    cout << "f2: возврат указателя\n";
    return &b;
}

Base& f3() {
    static Base b;
    cout << "f3: возврат ссылки\n";
    return b;
}

Base f4() {
    cout << "f4: утечка памяти!\n";
    Base* b = new Base();
    return *b;
}

Base* f5() {
    cout << "f5: new Base\n";
    return new Base();
}

Base& f6() {
    cout << "f6: плохая практика\n";
    Base* b = new Base();
    return *b;
}
// Версия 5: smart pointers 
// 4. УМНЫЕ УКАЗАТЕЛИ
class Smart {
public:
    Smart(int id) : id(id) {
        cout << "Smart " << id << " создан\n";
    }

    ~Smart() {
        cout << "Smart " << id << " уничтожен\n";
    }

    void hello() {
        cout << "Привет от " << id << endl;
    }

private:
    int id;
};

void takeUnique(unique_ptr<Smart> p) {
    cout << "unique_ptr передан\n";
    p->hello();
}

void takeShared(shared_ptr<Smart> p) {
    cout << "shared_ptr count = " << p.use_count() << endl;
}

shared_ptr<Smart> makeSharedObj() {
    return make_shared<Smart>(99);
}


// MAIN
int main() {

    cout << "\n--- ПЕРЕКРЫВАЕМЫЕ (НЕ ВИРТУАЛЬНЫЕ) МЕТОДЫ ---\n";
    {
        Desc d;
        Base* basePtr = &d;
        Desc* descPtr = &d;

        cout << "Вызов через Base*: ";
        basePtr->nonVirtualMethod(); // Base!!!

        cout << "Вызов через Desc*: ";
        descPtr->nonVirtualMethod(); // Desc!!!

        cout << "Вызов напрямую: ";
        d.nonVirtualMethod(); // Desc!!!
    }

    cout << "\n--- ВИРТУАЛЬНЫЕ МЕТОДЫ ---\n";
    {
        Desc d;
        Base* basePtr = &d;

        cout << "Вызов через Base*: ";
        basePtr->virtualMethod(); // Desc!!!
    }

    cout << "\n--- ДЕСТРУКТОР ---\n";
    {
        Base* obj = new Desc();
        delete obj;
    }

    cout << "\n--- method1 -> method2 ---\n";
    {
        Desc d;
        d.method1();
    }

    cout << "\n--- ПРОВЕРКА ТИПА ---\n";
    {
        Base* p = new Desc();
        cout << p->classname() << endl;
        cout << p->isA("Base") << endl;
        cout << p->isA("Desc") << endl;
        delete p;
    }

    cout << "\n--- dynamic_cast ---\n";
    {
        Base* p = new Desc();
        Desc* d = dynamic_cast<Desc*>(p);
        if (d) d->onlyForDesc();
        delete p;
    }

    cout << "\n--- ПЕРЕДАЧА ---\n";
    {
        Desc d;
        func1(d);
        func2(&d);
        func3(d);
    }

    cout << "\n--- ВОЗВРАТ ---\n";
    {
        Base b1 = f1();
        Base* b2 = f2();
        Base& b3 = f3();

        Base b4 = f4();
        Base* b5 = f5();
        delete b5;
    }

    cout << "\n--- UNIQUE_PTR ---\n";
    {
        auto u = make_unique<Smart>(1);
        takeUnique(move(u));
    }

    cout << "\n--- SHARED_PTR ---\n";
    {
        auto s1 = make_shared<Smart>(2);
        auto s2 = s1;
        cout << "count = " << s1.use_count() << endl;

        auto s3 = makeSharedObj();
    }

    cout << "\n=== КОНЕЦ ===\n";
}