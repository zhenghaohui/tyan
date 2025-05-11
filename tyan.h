#pragma once
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <stdint-gcc.h>

namespace tyan {
    inline std::string to_string(const int num) {
        return std::to_string(num);
    }

    class Painter {
        uint32_t depth_ = 0;
    public:
        std::map<std::string, std::string> var_map;

        void push() {
            depth_ += 1;
        }

        void pop() {
            depth_ -= 1;
        }


        static Painter &get() {
            thread_local Painter painter;
            return painter;
        }

        template<typename T>
        T &catch_var(const std::string &name, T &new_val) {
            this->var_map[name] = ::tyan::to_string(new_val);
            return new_val;
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
            std::string tmp;
            std::cout << std::string(depth_ << 1, ' ');
            for (const char c: line) {
                if (c == ' ' || c == ')' || c == '(' || c == ',' || c == ';') {
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
        Painter* painter_;
    public:
        explicit PainterDomainGuard(Painter* painter): painter_((painter)) {
            painter->push();
        }

        ~PainterDomainGuard() {
            painter_->pop();
        }
    };

}


#define TyanCatch(var) tyan_painter.catch_var(#var, var)
#define LogLine(line) tyan_painter.log_line(line)
