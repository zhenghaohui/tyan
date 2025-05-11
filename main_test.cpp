
#include "tyan.h" /* <cxx_source> */
  #include <iostream> /* <include> */
  #include <vector> /* <include> */
  #include <map> /* <include> */
  #include <algorithm> /* <include> */
  #include <string> /* <include> */
  #include <memory> /* <include> */
  // 定义一个简单的结构体 /* <comment> */
  struct Point{ /* <struct> */
    int x, y; /* <single-sentence> */
    // 构造函数 /* <comment> */
    Point(int x = 0, int y = 0) : x(x), y(y){ /* <function> */
      /* params: x, y */
      TyanMethod();
      TyanCatch(x);
      TyanCatch(y);
      LogLine("Point(int x = 0, int y = 0) : x(x), y(y){");
      TyanGuard(2);
    }
    // 重载输出运算符 /* <comment> */
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
  // 定义一个模板函数 /* <comment> */
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
  // 定义一个类 /* <comment> */
  class MyClass{ /* <class> */
    private: /* <single-sentence> */
    std::string name; /* <single-sentence> */
    int value; /* <single-sentence> */
    public: /* <single-sentence> */
    // 构造函数 /* <comment> */
    MyClass(const std::string &name, int value) : name(name), value(value){ /* <function> */
      /* params: name, value */
      TyanMethod();
      TyanCatch(name);
      TyanCatch(value);
      LogLine("MyClass(const std::string &name, int value) : name(name), value(value){");
      TyanGuard(14);
    }
    // 成员函数 /* <comment> */
    void display() const{ /* <function> */
      /* params:  */
      TyanMethod();
      LogLine("void display() const{");
      TyanGuard(15);
      std::cout << "Name: " << name << ", Value: " << value << std::endl; /* <single-sentence> */
      LogLine("std::cout << \"Name: \" << name << \", Value: \" << value << std::endl;");
    }
    // 静态成员函数 /* <comment> */
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
  // 使用命名空间 /* <comment> */
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
  // 主函数 /* <comment> */
  int main(){ /* <function> */
    /* params:  */
    TyanMethod();
    LogLine("int main(){");
    TyanGuard(22);
    // 测试基础数据类型 /* <comment> */
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
    // 测试结构体 /* <comment> */
    Point p1(1, 2), p2(3, 4); /* <single-sentence> */
    LogLine("Point p1(1, 2), p2(3, 4);");
    // 测试类 /* <comment> */
    MyClass obj("TestObject", 42); /* <single-sentence> */
    LogLine("MyClass obj(\"TestObject\", 42);");
    obj.display(); /* <single-sentence> */
    LogLine("obj.display();");
    MyClass::staticMethod(); /* <single-sentence> */
    LogLine("MyClass::staticMethod();");
    // 测试 STL 容器 /* <comment> */
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
    // 测试智能指针 /* <comment> */
    std::shared_ptr<MyClass> ptr = std::make_shared<MyClass>("SmartPointer", 100); /* <var_set> */
    LogLine("std::shared_ptr<MyClass> ptr = std::make_shared<MyClass>(\"SmartPointer\", 100);");
    TyanCatch(ptr);
    ptr->display(); /* <single-sentence> */
    LogLine("ptr->display();");
    // 测试命名空间 /* <comment> */
    MyNamespace::printMessage("Hello from MyNamespace!"); /* <single-sentence> */
    LogLine("MyNamespace::printMessage(\"Hello from MyNamespace!\");");
    // 测试 tyan.h 中的功能 /* <comment> */
    int x = 42; /* <var_set> */
    LogLine("int x = 42;");
    TyanCatch(x);
    LogLine("return 0;");
    return 0; /* <return> */
  }