
#include "tyan.h" /* <cxx_source> */
  #include <iostream> /* <include> */
  #include <vector> /* <include> */
  #include <map> /* <include> */
  #include <algorithm> /* <include> */
  #include <string> /* <include> */
  #include <memory> /* <include> */
  struct Point{ /* <struct> */
    int x, y; /* <single-sentence> */
    Point(int x = 0, int y = 0) : x(x), y(y){ /* <function> */
      /* params: x, y */
      TyanMethod();
      TyanCatch(x);
      TyanCatch(y);
      LogLine("Point(int x = 0, int y = 0) : x(x), y(y){");
      TyanGuard(2);
    }
    friend std::ostream &operator<<(std::ostream &os, const Point &p){ /* <function> */
      /* params: os, p */
      TyanMethod();
      TyanCatch(os);
      TyanCatch(p);
      LogLine("friend std::ostream &operator<<(std::ostream &os, const Point &p){");
      TyanGuard(3);
      os << "(" << p.x << ", " << p.y << ")"; /* <single-sentence> */
      LogLine("os << \"(\" << p.x << \", \" << p.y << \")\";");
      LogLine("return os;");
      return os; /* <return> */
    }
  }
  ; /* <single-sentence> */
  template<typename T> /* <single-sentence> */
  T add(T a, T b){ /* <function> */
    /* params: a, b */
    TyanMethod();
    TyanCatch(a);
    TyanCatch(b);
    LogLine("T add(T a, T b){");
    TyanGuard(8);
    LogLine("return a + b;");
    return a + b; /* <return> */
  }
  class MyClass{ /* <class> */
    private: /* <single-sentence> */
    std::string name; /* <single-sentence> */
    int value; /* <single-sentence> */
    public: /* <single-sentence> */
    MyClass(const std::string &name, int value) : name(name), value(value){ /* <function> */
      /* params: name, value */
      TyanMethod();
      TyanCatch(name);
      TyanCatch(value);
      LogLine("MyClass(const std::string &name, int value) : name(name), value(value){");
      TyanGuard(14);
    }
    void display() const{ /* <function> */
      /* params:  */
      TyanMethod();
      LogLine("void display() const{");
      TyanGuard(15);
      std::cout << "Name: " << name << ", Value: " << value << std::endl; /* <single-sentence> */
      LogLine("std::cout << \"Name: \" << name << \", Value: \" << value << std::endl;");
    }
    static void staticMethod(){ /* <function> */
      /* params:  */
      TyanMethod();
      LogLine("static void staticMethod(){");
      TyanGuard(17);
      std::cout << "This is a static method." << std::endl; /* <single-sentence> */
      LogLine("std::cout << \"This is a static method.\" << std::endl;");
    }
  }
  ; /* <single-sentence> */
  namespace MyNamespace{ /* <namespace> */
    void printMessage(const std::string &message){ /* <function> */
      /* params: message */
      TyanMethod();
      TyanCatch(message);
      LogLine("void printMessage(const std::string &message){");
      TyanGuard(20);
      std::cout << "Message: " << message << std::endl; /* <single-sentence> */
      LogLine("std::cout << \"Message: \" << message << std::endl;");
    }
  }
  int main(){ /* <function> */
    /* params:  */
    TyanMethod();
    LogLine("int main(){");
    TyanGuard(22);
    int a = 10, b = 20; /* <var_set> */
    LogLine("int a = 10, b = 20;");
    TyanCatch(a);
    double c = 3.14, d = 2.71; /* <var_set> */
    LogLine("double c = 3.14, d = 2.71;");
    TyanCatch(c);
    int a_plus_b = add(a, b); /* <var_set> */
    LogLine("int a_plus_b = add(a, b);");
    TyanCatch(a_plus_b);
    int c_plus_d = add(c, d); /* <var_set> */
    LogLine("int c_plus_d = add(c, d);");
    TyanCatch(c_plus_d);
    Point p1(1, 2), p2(3, 4); /* <single-sentence> */
    LogLine("Point p1(1, 2), p2(3, 4);");
    MyClass obj("TestObject", 42); /* <single-sentence> */
    LogLine("MyClass obj(\"TestObject\", 42);");
    obj.display(); /* <single-sentence> */
    LogLine("obj.display();");
    MyClass::staticMethod(); /* <single-sentence> */
    LogLine("MyClass::staticMethod();");
    std::vector<int> vec ={1, 2, 3, 4, 5}; /* <var_set> */
    LogLine("std::vector<int> vec ={1, 2, 3, 4, 5};");
    TyanCatch(vec);
    for (const auto &elem : vec){ /* <for> */
      elem; /* <single-sentence> */
      LogLine("elem;");
    }
    std::cout << std::endl; /* <single-sentence> */
    LogLine("std::cout << std::endl;");
    std::map<std::string, int> myMap ={{"apple", 1},{"banana", 2},{"cherry", 3}}; /* <var_set> */
    LogLine("std::map<std::string, int> myMap ={{\"apple\", 1},{\"banana\", 2},{\"cherry\", 3}};");
    TyanCatch(myMap);
    for (const auto &[key, value] : myMap){ /* <for> */
      key; /* <single-sentence> */
      LogLine("key;");
      value; /* <single-sentence> */
      LogLine("value;");
    }
    std::shared_ptr<MyClass> ptr = std::make_shared<MyClass>("SmartPointer", 100); /* <var_set> */
    LogLine("std::shared_ptr<MyClass> ptr = std::make_shared<MyClass>(\"SmartPointer\", 100);");
    TyanCatch(ptr);
    ptr->display(); /* <single-sentence> */
    LogLine("ptr->display();");
    MyNamespace::printMessage("Hello from MyNamespace!"); /* <single-sentence> */
    LogLine("MyNamespace::printMessage(\"Hello from MyNamespace!\");");
    int x = 42; /* <var_set> */
    LogLine("int x = 42;");
    TyanCatch(x);
    LogLine("return 0;");
    return 0; /* <return> */
  }