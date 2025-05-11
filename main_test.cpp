
#include "tyan.h" /* <cxx_source> */
  #include "tyan.h" /* <include> */
  #include <cassert> /* <include> */
  #include <chrono> /* <include> */
  #include <iostream> /* <include> */
  #include <map> /* <include> */
  #include <sstream> /* <include> */
  #include <string> /* <include> */
  #include <utility> /* <include> */
  int add(int a, int b){ /* <function> */
    /* params: a, b */
    tyan::Painter& tyan_painter = tyan::Painter::get();
    TyanCatch(a);
    TyanCatch(b);
    tyan::PainterDomainGuard tyan_domain_guard_1(&tyan_painter);
    LogLine("int add(int a, int b){");
    tyan::PainterDomainGuard tyan_domain_guard_2(&tyan_painter);
    LogLine("return a + b;");
    return a + b; /* <return> */
  }
  int fibonacci(int n){ /* <function> */
    /* params: n */
    tyan::Painter& tyan_painter = tyan::Painter::get();
    TyanCatch(n);
    tyan::PainterDomainGuard tyan_domain_guard_3(&tyan_painter);
    LogLine("int fibonacci(int n){");
    if (n <= 1){ /* <if> */
      tyan::PainterDomainGuard tyan_domain_guard_4(&tyan_painter);
      LogLine("if (n <= 1){");
      tyan::PainterDomainGuard tyan_domain_guard_5(&tyan_painter);
      LogLine("return n;");
      return n; /* <return> */
    }
    tyan::PainterDomainGuard tyan_domain_guard_6(&tyan_painter);
    LogLine("return fibonacci(n - 1) + fibonacci(n - 2);");
    return fibonacci(n - 1) + fibonacci(n - 2); /* <return> */
  }
  int main(){ /* <function> */
    /* params:  */
    tyan::Painter& tyan_painter = tyan::Painter::get();
    tyan::PainterDomainGuard tyan_domain_guard_7(&tyan_painter);
    LogLine("int main(){");
    tyan::PainterDomainGuard tyan_domain_guard_8(&tyan_painter);
    LogLine("assert(add(10, 20) == 30);");
    assert(add(10, 20) == 30); /* <assert> */
    tyan::PainterDomainGuard tyan_domain_guard_9(&tyan_painter);
    LogLine("int result = fibonacci(5);");
    int result = fibonacci(5); /* <var_set> */
    tyan::PainterDomainGuard tyan_domain_guard_10(&tyan_painter);
    LogLine("std::cout << "The 10th Fibonacci number is: " << result << std::endl;");
    std::cout << "The 10th Fibonacci number is: " << result << std::endl; /* <single-sentence> */
    tyan::PainterDomainGuard tyan_domain_guard_11(&tyan_painter);
    LogLine("return 0;");
    return 0; /* <return> */
  }