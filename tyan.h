#pragma once
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <stdint-gcc.h>

namespace tyan {
    template<typename T>
    std::string to_string(T* num) {
        return "<ptr>";
    }

    template<>
    inline std::string to_string<int>(int* num) {
        return std::to_string(*num);
    }

    class ThreadContext {
        uint32_t depth_ = 0;
    public:

        uint32_t depth() { return depth_; }

        void push() {
            depth_ += 1;
        }

        void pop() {
            depth_ -= 1;
        }


        static ThreadContext &get() {
            thread_local ThreadContext txn;
            return txn;
        }
    };

    class Painter {
    public:
        std::map<std::string, std::string> var_map;

        template<typename T>
        void catch_var(const std::string &name, T *new_val) {
            this->var_map[name] = ::tyan::to_string(new_val);
        }

        template<typename T>
        void log_value(T &new_val) {
            std::cout << ::tyan::to_string(new_val);
        }

        void log_value(const std::string &value_str) {
            std::cout << value_str;
        }

        void log_var(const std::string &name) {
            if (this->var_map.count(name)) {
                std::cout << name << ":" << this->var_map[name];
            } else {
                std::cout << name;
            }
        }

        void log_line(const std::string &line) {
            static std::set VAR_CHARSET = {
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_'
            };
            std::string tmp;
            std::cout << std::string(ThreadContext::get().depth() << 1, ' ');
            for (const char c: line) {
                if (VAR_CHARSET.find(c) == VAR_CHARSET.end()) {
                    this->log_var(tmp);
                    tmp.clear();
                    std::cout << c;
                    continue;
                }
                tmp += c;
            }
            if (!tmp.empty()) {
                this->log_var(tmp);
            }
            std::cout << std::endl;
        }

        ~Painter() {
            // std::cout << os.str() << std::endl;
        }
    };

    class PainterDomainGuard {
    public:
        explicit PainterDomainGuard(){
            ThreadContext::get().push();
        }

        ~PainterDomainGuard() {
            ThreadContext::get().pop();
        }
    };

}

#define TyanMethod()    tyan::Painter tyan_painter
#define TyanGuard(id)   tyan::PainterDomainGuard tyan_domain_guard_ ## id;
#define TyanCatch(var)  tyan_painter.catch_var(#var, &var)
#define LogLine(line)   tyan_painter.log_line(line)
