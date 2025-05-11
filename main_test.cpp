
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
    TyanMethod();
    TyanCatch(a);
    TyanCatch(b);
    LogLine("int add(int a, int b){");
    TyanGuard(1);
    LogLine("return a + b;");
    return a + b; /* <return> */
  }
  int fibonacci(int n){ /* <function> */
    /* params: n */
    TyanMethod();
    TyanCatch(n);
    LogLine("int fibonacci(int n){");
    TyanGuard(3);
    if (n <= 1){ /* <if> */
      LogLine("if (n <= 1){");
      TyanGuard(4);
      LogLine("return n;");
      return n; /* <return> */
    }
    LogLine("return fibonacci(n - 1) + fibonacci(n - 2);");
    return fibonacci(n - 1) + fibonacci(n - 2); /* <return> */
  }
  int main(){ /* <function> */
    /* params:  */
    TyanMethod();
    LogLine("int main(){");
    TyanGuard(7);
    assert(add(10, 20) == 30); /* <assert> */
    LogLine("assert(add(10, 20) == 30);");
    int n = 1; /* <var_set> */
    LogLine("int n = 1;");
    TyanCatch(n);
    n++; /* <single-sentence> */
    LogLine("n++;");
    n += 1; /* <var_add_self> */
    LogLine("n += 1;");
    TyanCatch(n);
    int result = fibonacci(n); /* <var_set> */
    LogLine("int result = fibonacci(n);");
    TyanCatch(result);
    std::cout << "The 10th Fibonacci number is: " << result << std::endl; /* <single-sentence> */
    LogLine("std::cout << \"The 10th Fibonacci number is: \" << result << std::endl;");
    LogLine("return 0;");
    return 0; /* <return> */
  }