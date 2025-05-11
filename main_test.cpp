
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
      return a + b; /* <single-sentence> */
  }
int fibonacci(int n){ /* <function> */
      /* params: n */
      tyan::Painter& tyan_painter = tyan::Painter::get();
      TyanCatch(n);
      tyan::PainterDomainGuard tyan_domain_guard_2(&tyan_painter);
      LogLine("int fibonacci(int n){");
      if (n <= 1){ /* <if> */
          tyan::PainterDomainGuard tyan_domain_guard_3(&tyan_painter);
          LogLine("if (n <= 1){");
          return n; /* <single-sentence> */
      }
      return fibonacci(n - 1) + fibonacci(n - 2); /* <single-sentence> */
  }
int main(){ /* <function> */
      /* params:  */
      tyan::Painter& tyan_painter = tyan::Painter::get();
      tyan::PainterDomainGuard tyan_domain_guard_4(&tyan_painter);
      LogLine("int main(){");
      assert(add(10, 20) == 30); /* <assert> */
      int result = fibonacci(5); /* <var_set> */
      std::cout << "The 10th Fibonacci number is: " << result << std::endl; /* <single-sentence> */
      return 0; /* <single-sentence> */
  }