#pragma once
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <cstdint>
#include <iomanip>
#include <ctime>
#include <thread>

namespace tyan {
    template<typename T>
    std::string to_string(T *num) {
        return "...";
    }

    template<>
    inline std::string to_string<const int>(const int *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<int>(int *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<const bool>(const bool *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<bool>(bool *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<const double>(const double *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<double>(double *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<const int64_t>(const int64_t *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<int64_t>(int64_t *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<const uint64_t>(const uint64_t *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<uint64_t>(uint64_t *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<const uint32_t>(const uint32_t *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<uint32_t>(uint32_t *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<const uint16_t>(const uint16_t *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<uint16_t>(uint16_t *num) {
        return std::to_string(*num);
    }

    template<>
    inline std::string to_string<const std::string>(const std::string *str) {
        return *str;
    }
    template<>
    inline std::string to_string<std::string>(std::string *str) {
        return *str;
    }

    template<>
    inline std::string to_string<const char *>(const char * *str) {
        return *str;
    }

    template<>
    inline std::string to_string<char *>(char * *str) {
        return *str;
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
            // std::cout << "catch " << name << " -> " << this->var_map[name] << std::endl;
        }

        template<typename T>
        void log_value(T &new_val) {
            log(::tyan::to_string(new_val));
        }

        void log_value(const std::string &value_str) {
            log(value_str);
        }

        std::string get_var(const std::string &name) {
            if (this->var_map.count(name)) {
                return name + ":" + this->var_map[name];
            } else {
                return name;
            }
        }

        void log_line(const std::string &line) {
            static std::set<char> VAR_CHARSET = {
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', '.'
            };
            std::string tmp;
            std::ostringstream oss;
            oss << std::string(ThreadContext::get().depth() << 1, ' ');
            for (size_t i = 0; i < line.size(); i++) {
                char c = line[i];
                if (VAR_CHARSET.count(c)) {
                    tmp += c;
                    continue;
                }
                char c_next = i + 1 < line.size() ? line[i + 1] : ' ';
                if (c == '-' && c_next == '>') {
                    tmp += "->";
                    i++;
                    continue;
                }
                if (!tmp.empty()) {
                    oss << get_var(tmp);
                    tmp.clear();
                }
                oss << c;
            }
            if (!tmp.empty()) {
                oss << get_var(tmp);
            }
            log(oss.str());
        }

        ~Painter() {
            // std::cout << os.str() << std::endl;
        }

    private:
        void log(const std::string &message) {
            auto now = std::time(nullptr);
            auto local_time = *std::localtime(&now);
            std::ostringstream oss;
            oss << std::put_time(&local_time, "%H:%M:%S");
            std::cout << "[" << oss.str() << "][" << std::this_thread::get_id() << "] " << message << std::endl;
        }
    };

    class PainterDomainGuard {
    public:
        explicit PainterDomainGuard() {
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
