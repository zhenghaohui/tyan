import argparse
import os
from idlelib.debugger_r import restart_subprocess_debugger
from math import remainder
from types import new_class
from typing import List
from enum import Enum
import re

PARAM_CHAR_SET = {
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', '.', '[', ']'
}

def check_condition_define(line: str) -> bool:
    return (
            line.startswith("#ifdef")
            or line.startswith("#ifndef")
            or line.startswith("#else")
            or line.startswith("#elseif")
            or line.startswith("#endif"))

class CodeItemType(Enum):
    CXX_SOURCE = "<cxx_source>"
    INCLUDE = "<include>"
    DEFINE = "<define>"
    COMMENT_LINE = "<comment>"
    DECLARE_CLASS = "<declare_class>"
    FUNCTION = "<function>"
    IF = "<if>"
    WHILE = "<WHILE>"
    FOR = "<for>"
    SINGLE_SENTENCE = "<single-sentence>"
    NAMESPACE = "<namespace>"
    EXTERN = "<extern>"
    VAR_SET = "<var_set>"
    STRUCT = "<struct>"
    CLASS = "<class>"
    SWITCH = "<switch>"
    VAR_ADD_SELF = "<var_add_self>"
    VAR_SUB_SELF = "<var_sub_self>"
    ASSERT = "<assert>"
    RETURN  = "<return>"
    BREAK  = "<break>"
    CONTINUE  = "<continue>"
    PURE_DOMAIN = "<pure_domain>"
    ELSE = "<else>"

    UNKNOWN = "<unknown>"


def go_through_head_and_body(from_line: int, to_line: int, raw_content: List[str],
                             left_bracket: chr = '{', right_bracket: chr = '}') -> (int, int, int):
    line = raw_content[from_line]
    remain_depth = line.count(left_bracket) - line.count(right_bracket)
    remain_depth_par = line.count("(") - line.count(")")
    # go through function header
    while remain_depth == 0 or remain_depth_par != 0:
        if remain_depth_par == 0 and line.count(left_bracket):
            break
        if line[-1] == ";" and not remain_depth_par:
            break
        line = raw_content[to_line]
        to_line += 1
        remain_depth += line.count(left_bracket) - line.count(right_bracket)
        remain_depth_par += line.count("(") - line.count(")")
    head_end_line = to_line

    if line.count(left_bracket):
        # go through function body
        while remain_depth > 0:
            line = raw_content[to_line]
            to_line += 1
            remain_depth += line.count(left_bracket) - line.count(right_bracket)

    return from_line, head_end_line, to_line


def go_through_single_sentence(from_line: int, raw_content: List[str]) -> (int, int):
    to_line = from_line
    remain_bra_1 = 0  # (
    remain_bra_2 = 0  # {
    while to_line < len(raw_content):
        line = raw_content[to_line]
        remain_bra_1 += line.count("(") - line.count(")")
        remain_bra_2 += line.count("{") - line.count("}")
        to_line += 1
        if line.endswith(';') and not remain_bra_1 and not remain_bra_2:
            break
        special_macro = line.replace(" ", "")
        if special_macro.startswith("#"):
            break
        if special_macro in ["public:", "private:", "procted:"]:
            break
        if special_macro.startswith("case"):
            break
        if special_macro.startswith("default:"):
            break
        if special_macro.startswith("template<"):
            break
    return from_line, to_line

def extract_skeleton(line: str) -> str:
    result = ""
    for chr in line:
        if chr == '#' or chr == "'" or chr == '(' or chr == "{":
            break
        result += chr
    result += " "
    return result

def found_op(line: str, op: str) -> bool:
    seems_str_pos = line.find('\"')
    if seems_str_pos != -1:
        if seems_str_pos < line.find(op):
            return False
    line = extract_skeleton(line)
    if len(line) <= len(op) + 2:
        return False
    for idx in range(0, len(line)):
        if idx + 1 + len(op) + 1 > len(line):
            break
        if line[idx] in "+-=":
            continue
        if line[idx + 1:idx + 1 + len(op)] != op:
            continue
        if line[idx + 1 + len(op)] in "+-=":
            continue
        return True
    return False

def short_head_content(content: List[str]) -> List[str] :
    updated_content = []
    for idx, line in enumerate(content):
        is_condition_define = check_condition_define(line)
        if (len(updated_content) == 0
                or updated_content[-1].count("//")
                or updated_content[-1].count("/*")
                or is_condition_define):
            if is_condition_define:
                line = f"\n{line}\n"
            updated_content.append(line)
            continue
        if line.startswith("."):
            updated_content[-1] += line
        else:
            updated_content[-1] += " " + line
    return updated_content


class CodeItem:
    def __init__(self, item_type: CodeItemType, head_content: List[str], body_content: List[str]):
        self.item_type: CodeItemType = item_type
        self.head_content: List[str] = short_head_content(head_content)
        self.body_content: List[str] = body_content
        self.parts: List[CodeItem] = []
        self.parent: "CodeItem" = None
        self.is_under_function = False # pls use self.get_is_under_function(), some class might overload this
        self.need_domain_guard = False
        self.depth = 0

    def get_is_under_function(self):
        return self.is_under_function

    def append_part(self, new_item: "CodeItem"):
        new_item.parent = self
        new_item.is_under_function = self.get_is_under_function() or isinstance(new_item, CodeItemFunction)
        new_item.depth = self.depth + 1
        self.parts.append(new_item)

    def parse_head(self):
        pass

    def parse_body(self):
        to_line = 0
        while to_line < len(self.body_content):  # has next part
            from_line = to_line
            to_line = from_line + 1

            line = self.body_content[from_line]

            # schema1: include
            if line.startswith("#include"):
                self.append_part(CodeItemInclude(self.body_content[from_line:to_line]))
                continue

            # schema2: define
            if line.startswith("#define"):
                self.append_part(CodeItemDefine(self.body_content[from_line:to_line]))
                continue

            # schema3: comment line
            if line.startswith("//"):
                self.append_part(CodeItemCommentLine(self.body_content[from_line:to_line]))
                continue

            # schema: namespace
            if line.startswith("namespace"):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemNamespace(self.body_content[from_line:head_end_line],
                                                   self.body_content[head_end_line:to_line]))
                continue

            # schema: namespace
            if line.startswith("extern "):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemExtern(self.body_content[from_line:head_end_line],
                                                self.body_content[head_end_line:to_line]))
                continue

            # schema: struct
            if line.startswith("struct "):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemStruct(self.body_content[from_line:head_end_line],
                                                self.body_content[head_end_line:to_line]))
                continue

            # schema: class
            if line.startswith("class "):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemClass(self.body_content[from_line:head_end_line],
                                                self.body_content[head_end_line:to_line]))
                continue

            if line.startswith("switch "):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemSwitch(self.body_content[from_line:head_end_line],
                                                self.body_content[head_end_line:to_line]))
                continue

            if line.startswith("if (") or line.startswith("if("):
                # todo: simple if without bracket
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemIf(self.body_content[from_line:head_end_line],
                                            self.body_content[head_end_line:to_line]))
                continue

            # schema6: declare class
            if line.startswith("class ") and line.find(";") != -1:
                self.append_part(CodeItemDeclareClass(self.body_content[from_line:to_line]))
                continue

            # schema7: right bracket
            if line.startswith("}"):
                # just ignore
                continue

            # schema4: function
            hit_function = False
            for try_multi_line in range(1, 3):
                temp_line = " ".join(self.body_content[from_line:from_line + try_multi_line])
                if not self.get_is_under_function() and temp_line.find("(") != -1 and temp_line.find(";") == -1:
                    from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                    head_content = self.body_content[from_line:head_end_line]
                    if head_content[-1][-1] == ';':
                        to_line = head_end_line
                        self.append_part(CodeItemSingleSentence(head_content))
                    else:
                        self.append_part(CodeItemFunction(self.body_content[from_line:head_end_line],
                                                          self.body_content[head_end_line:to_line]))
                    hit_function = True
                    break
            if hit_function:
                continue

            # schema11: for
            if line[:10].replace(' ', '').startswith("for("):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemFor(self.body_content[from_line:head_end_line],
                                             self.body_content[head_end_line:to_line]))
                continue

            # schema11: while
            if line[:10].replace(' ', '').startswith("while("):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemWhile(self.body_content[from_line:head_end_line],
                                             self.body_content[head_end_line:to_line]))
                continue

            # schema: pure domain
            if line == "{":
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemPureDomain(self.body_content[from_line:head_end_line],
                                                    self.body_content[head_end_line:to_line]))
                continue

            # schema: else
            if line.startswith("else"):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemElse(self.body_content[from_line:head_end_line],
                                              self.body_content[head_end_line:to_line]))
                continue

            # schema: single line
            from_line, to_line = go_through_single_sentence(from_line, self.body_content)
            line = "".join(self.body_content[from_line:to_line])

            if self.get_is_under_function(): # prevent global namespace var
                # schema: assert
                if line.startswith("assert("):
                    self.append_part(CodeItemAssert(self.body_content[from_line:to_line]))
                    continue

                # schema: return
                if line.startswith("return ") or line.startswith("return;") or line.startswith("return{"):
                    self.append_part(CodeItemReturn(self.body_content[from_line:to_line]))
                    continue

                # schema: break;
                if line.startswith("break;"):
                    self.append_part(CodeItemBreak(self.body_content[from_line:to_line]))
                    continue

                # schema: continue;
                if line.startswith("continue;"):
                    self.append_part(CodeItemContinue(self.body_content[from_line:to_line]))
                    continue

                # schema: =
                if found_op(line, "=") and not line.startswith("using "):
                    self.append_part(CodeItemVarSet(self.body_content[from_line:to_line]))
                    continue

                # schema: +=
                if found_op(line, "+="):
                    self.append_part(CodeItemVarAddSelf(self.body_content[from_line:to_line]))
                    continue

                # schema10: -=
                if found_op(line, "-="):
                    self.append_part(CodeItemVarSubSelf(self.body_content[from_line:to_line]))
                    continue

            self.append_part(CodeItemSingleSentence(self.body_content[from_line:to_line]))


            # assert False
        for part in self.parts:
            part.parse()

    def parse(self):
        self.parse_head()
        self.parse_body()

    def log_line(self, depth: int) -> str:
        result = ""
        line_prefix = line_prefix_depth(depth)
        guard_uuid = get_painter_guard_uuid()
        log_line = "".join(self.head_content).strip("\n ")
        log_line = log_line.replace('"', '\\"')
        log_line = log_line.replace('\n', '')
        log_line = re.sub(r'#ifdef.*', '', log_line)
        log_line = re.sub(r'#ifndef.*', '', log_line)
        log_line = re.sub(r'#elseif.*', '', log_line)
        log_line = re.sub(r'#else.*', '', log_line)
        log_line = re.sub(r'#endif.*', '', log_line)
        if self.get_is_under_function() and len(log_line):
            result += f"{line_prefix}LogLine(\"{log_line}\");"
        if self.need_domain_guard:
            result += f"{line_prefix}TyanGuard({guard_uuid});"
        return result

    def print_head(self, add_tyan_code=False) -> str:
        result = ""
        line_prefix = line_prefix_depth(self.depth)
        for line in self.head_content:
            result += f"{line_prefix}{line}"
        if add_tyan_code:
            result += f" /* {self.item_type.value} */"
        return result

    def print(self, add_tyan_code=False) -> str:
        result = self.print_head(add_tyan_code)
        for part in self.parts:
            result += part.print(add_tyan_code)
        return result
# todo: return Status::NotSupported("CompactionFilter::IgnoreSnapshots() = false is not supported ""anymore."); /* <var_set> */

class CodeItemInclude(CodeItem):
    def __init__(self, head_content: List[str]):
        super().__init__(CodeItemType.INCLUDE, head_content, [], )


class CodeItemDefine(CodeItem):
    def __init__(self, head_content: List[str]):
        super().__init__(CodeItemType.DEFINE, head_content, [])


class CodeItemCommentLine(CodeItem):
    def __init__(self, head_content: List[str]):
        super().__init__(CodeItemType.COMMENT_LINE, head_content, [])

def line_prefix_depth(depth: int) -> str:
    return "\n" + "  " * depth

class PainterGuard:
    painter_guard_uuid = 0


def get_painter_guard_uuid() -> int:
    PainterGuard.painter_guard_uuid += 1
    return PainterGuard.painter_guard_uuid

def format_tyan_catch(line_prefix: str, param: str) -> str:
    # give up catch
    if param.count("[") != param.count("]"):
        return ""
    if param.count("(") != param.count(")"):
        return ""
    if param.count("("):
        return ""
    if param in ["std", "int", "double", "void"]:
        return ""
    if param.endswith("[]"):
        return ""
    return f"{line_prefix}TyanCatch({param});"

class CodeItemFunction(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.FUNCTION, head_content, body_content)
        self.head_content = [" ".join([remove_comment(line) for line in self.head_content])]
        self.params = None
        self.need_domain_guard = True

    def print_head(self, add_tyan_code=False):
        result = super().print_head(add_tyan_code)
        line_prefix = line_prefix_depth(self.depth + 1)
        if add_tyan_code:
            result += f"{line_prefix}/* params: " + ", ".join(self.params) + " */"
            result += f"{line_prefix}TyanMethod();"
            for param in self.params:
                result += format_tyan_catch(line_prefix, param)
            result += self.log_line(self.depth + 1)
        return result

    def print(self, add_tyan_code=False) -> str:
        result = super().print(add_tyan_code)
        result += "\n"
        result += "  " * self.depth
        result += "}"
        return result

    def extract_params(self, content: str) -> List[str]:
        param_beg = content.find('(')
        param_end = param_beg + 1
        depth = 1
        while depth > 0:
            depth += (content[param_end] == '(') - (content[param_end] == ')')
            param_end += 1
        content = content[param_beg:param_end]

        parts = content.split(",")
        result = []
        for part in parts:
            pos = part.find('=') # drop right part
            if pos != -1:
                part = part[:pos]
            part = part[::-1].strip("{) ")
            if part.count(' ') == 0:
                continue
            if part.count('<'):
                continue
            if part.count('>'):
                continue
            name = ""
            for char in part:
                if char not in PARAM_CHAR_SET:
                    break
                name += char
            name = name[::-1]
            # print("!!! : " + name)
            if len(name) > 0 and name not in ["bool", "int", "double"]:
                result.append(name)
        return result

    def parse_head(self):
        self.params = self.extract_params("".join(self.head_content))

class CodeItemIf(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.IF, head_content, body_content)

        self.need_domain_guard = True

    def print_head(self, add_tyan_code=False) -> str:
        result = super().print_head(add_tyan_code)
        if add_tyan_code:
            result += self.log_line(self.depth + 1)
        return result

    def print(self, add_tyan_code=False) -> str:
        result = super().print(add_tyan_code)
        if any("{" in line for line in self.head_content):
            result += line_prefix_depth(self.depth) + "}"

        return result


class CodeItemElse(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.ELSE, head_content, body_content)
        self.need_domain_guard = True

    def print(self, add_tyan_code=False) -> str:
        result = super().print(add_tyan_code)
        if any("{" in line for line in self.head_content):
            result += line_prefix_depth(self.depth) + "}"

        return result


class CodeItemFor(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.FOR, head_content, body_content)
        self.need_domain_guard = True
        self.params_name = []

    def parse_body(self):
        # todo: better impl
        self.depth += 1
        super().parse_body()
        self.depth -= 1

    def parse_head(self):
        self.params_name = []
        content = "".join(self.head_content)
        candidate_prefix = content[:20].replace(" ", "")
        if candidate_prefix.startswith("for(auto") or candidate_prefix.startswith("for(constauto"):
            pos = content.find("auto ")
            pos_end = content.find(":", pos)
            if pos_end == -1:
                return
            candidate_str = content[pos+4:pos_end + 1]
            typing_param = ""
            for char in candidate_str:
                if char in PARAM_CHAR_SET:
                    typing_param += char
                    continue
                if len(typing_param) > 0:
                    self.params_name.append(typing_param)
                    typing_param = ""
                    break

    def print_head(self, add_tyan_code=False) -> str:
        result = super().print_head(add_tyan_code)
        if add_tyan_code:
            line_prefix = line_prefix_depth(self.depth)
            log_line = "".join(self.head_content)
            log_line = log_line.replace('"', '\\"')
            result = f"{line_prefix}LogLine(\"{log_line}\");" + result

            if len(self.body_content) == 0:
                return result

            for param in self.params_name:
                result += format_tyan_catch(line_prefix_depth(self.depth + 1), param)

            line_prefix = line_prefix_depth(self.depth + 1)
            guard_uuid = get_painter_guard_uuid()
            result += f"{line_prefix}TyanGuard({guard_uuid});"

            params = ", ".join(self.params_name)
            result += line_prefix_depth(self.depth + 1) + f"LogLine(\"[loop-round] {params} -> \");"



        return result

    def print(self, add_tyan_code=False) -> str:
        result = self.print_head(add_tyan_code)

        line_prefix = line_prefix_depth(self.depth + 1)

        if add_tyan_code and len(self.parts) > 0:
            result += f"{line_prefix}{{"
            guard_uuid = get_painter_guard_uuid()
            result += f"{line_prefix}TyanGuard({guard_uuid});"


        for part in self.parts:
            result += part.print(add_tyan_code)

        if add_tyan_code and len(self.parts) > 0:
            result += f"{line_prefix}}}"

        if any("{" in line for line in self.head_content):
            result += line_prefix_depth(self.depth) + "}"

        return result

class CodeItemWhile(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.WHILE, head_content, body_content)
        self.need_domain_guard = True

    def print(self, add_tyan_code=False) -> str:
        result = super().print(add_tyan_code)
        if any("{" in line for line in self.head_content):
            result += line_prefix_depth(self.depth) + "}"

        return result


class CodeItemSingleSentence(CodeItem):
    def __init__(self, head_content: List[str]):
        super().__init__(CodeItemType.SINGLE_SENTENCE, head_content, [])
        self.params = []

    def print_head(self, add_tyan_code=False) -> str:
        result = super().print_head(add_tyan_code)

        if add_tyan_code:
            for param in self.params:
                result += format_tyan_catch(line_prefix_depth(self.depth), param)
            if self.item_type not in [CodeItemType.BREAK, CodeItemType.CONTINUE]: # not add LogLine(xxx)
                if self.item_type != CodeItemType.RETURN:
                    result += self.log_line(self.depth)
                else:
                    result = self.log_line(self.depth) + result
        return result

class CodeItemNamespace(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.NAMESPACE, head_content, body_content)

    def print(self, add_tyan_code=False) -> str:
        result = super().print(add_tyan_code)
        result += "\n" + "  " * self.depth + "}"
        return result

class CodeItemExtern(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.EXTERN, head_content, body_content)

    def print(self, add_tyan_code=False) -> str:
        result = super().print(add_tyan_code)
        result += "\n" + "  " * self.depth + "}"
        return result

class CodeItemStruct(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.STRUCT, head_content, body_content)
        self.is_under_function = False

    def get_is_under_function(self):
        # Function > struct > Function is allow
        return False

    def print(self, add_tyan_code=False) -> str:
        result = super().print(add_tyan_code)
        result += "\n" + "  " * self.depth + "}"
        return result

class CodeItemClass(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.CLASS, head_content, body_content)

    def print(self, add_tyan_code=False) -> str:
        result = super().print(add_tyan_code)
        if any("{" in line for line in self.head_content):
            result += line_prefix_depth(self.depth) + "}"
        return result

class CodeItemSwitch(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.SWITCH, head_content, body_content)

    def print(self, add_tyan_code=False) -> str:
        result = super().print(add_tyan_code)
        if any("{" in line for line in self.head_content):
            result += line_prefix_depth(self.depth) + "}"
        return result

class CodeItemSourceCode(CodeItem):
    def __init__(self, body_content: List[str]):
        super().__init__(CodeItemType.CXX_SOURCE, [], body_content)

    def print(self, add_tyan_code=False) -> str:
        result = ""
        if add_tyan_code:
            result += "\n" + "  " * self.depth
            result += '#include "tyan.h"'
        result += super().print(add_tyan_code)
        return result


class CodeItemDeclareClass(CodeItem):
    def __init__(self, head_content: List[str]):
        super().__init__(CodeItemType.DECLARE_CLASS, head_content, [])

class CodeItemPureDomain(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.PURE_DOMAIN, head_content, body_content)

    def print(self, add_tyan_code=False) -> str:
        result = super().print(add_tyan_code)
        result += "\n"
        result += "  " * self.depth
        result += "}"
        return result

class CodeItemAssert(CodeItemSingleSentence):
    def __init__(self, head_content: List[str]):
        super().__init__(head_content)
        self.item_type = CodeItemType.ASSERT


class CodeItemVarModify(CodeItemSingleSentence): # pure
    def __init__(self, head_content: List[str]):
        super().__init__(head_content)

    def _extract_param_from_line(self, line: str) -> str:
        line = line[:line.find("=")] # left part
        line = line[::-1] # reverse
        line += ' '
        cur = 0
        while cur + 1 < len(line) and line[cur] not in PARAM_CHAR_SET: # drop others
            cur += 1
            continue
        result = ""
        while cur + 1 < len(line):
            if line[cur] in PARAM_CHAR_SET: # collect
                result += line[cur]
                cur += 1
                continue
            if line[cur:cur+2] == '>-':  # due to reversed
                result += line[cur:cur+2]
                cur += 2
                continue
            break
        result = result[::-1] # reverse back
        return result

    def parse_head(self):
        self.params = [self._extract_param_from_line("".join(self.head_content))]

class CodeItemVarSet(CodeItemVarModify):
    def __init__(self, head_content: List[str]):
        super().__init__(head_content)
        self.item_type = CodeItemType.VAR_SET


class CodeItemVarAddSelf(CodeItemVarModify):
    def __init__(self, head_content: List[str]):
        super().__init__(head_content)
        self.item_type = CodeItemType.VAR_ADD_SELF

class CodeItemVarSubSelf(CodeItemVarModify):
    def __init__(self, head_content: List[str]):
        super().__init__(head_content)
        self.item_type = CodeItemType.VAR_SUB_SELF

class CodeItemReturn(CodeItemSingleSentence):
    def __init__(self, head_content: List[str]):
        super().__init__(head_content)
        self.item_type = CodeItemType.RETURN

class CodeItemBreak(CodeItemSingleSentence):
    def __init__(self, head_content: List[str]):
        super().__init__(head_content)
        self.item_type = CodeItemType.BREAK

class CodeItemContinue(CodeItemSingleSentence):
    def __init__(self, head_content: List[str]):
        super().__init__(head_content)
        self.item_type = CodeItemType.CONTINUE

def remove_comment(content: str) -> str:
    # Remove line comments
    content = re.sub(r'//.*', '', content)
    # Remove block comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    return content


def standard_code(content: str) -> str:
    content = remove_comment(content)
    # Remove all whitespace characters (spaces, tabs, newlines)
    content = ''.join(content.split())
    # Insert a newline character every 100 characters
    content = '\n'.join([content[i:i + 100] for i in range(0, len(content), 100)])
    return content

def run_one_file(src_path: str, dst_path: str, replace_mode: bool):
    if replace_mode:
        dst_path = src_path
        print(f"Parsing {src_path} (replace mode) ...")
    else:
        print(f"Parsing {src_path} > {dst_path} ...")

    # Read source code
    src_code = read_file(src_path)
    src_code = remove_comment(src_code)

    # Standardize and process the code
    # standardized_code = standard_code(src_code)
    # write_file(src_path + ".std", standardized_code)

    formatted_code = format_code(src_code)
    raw_content = [line.strip() for line in formatted_code.split("\n") if line.strip()]

    # Parse and generate output
    code_tree = CodeItemSourceCode(raw_content)
    code_tree.parse()

    write_file(dst_path, code_tree.print(True))
    # write_file(dst_path + ".std", standard_code(src_code))

    # Verify that the standardized source and output match
    # assert read_file(src_path + ".std") == read_file(dst_path + ".std"), "Standardized files do not match!"


def main():
    parser = argparse.ArgumentParser(description='translate cxx src code into cxx-tyan src code')

    # 添加位置参数
    parser.add_argument('src_path', help='cxx源码输入文件路径或目录路径（当使用 -d/--dir 时）')
    parser.add_argument('dst_path', help='cxx-tyan源码输出文件路径（仅在未使用 -r/--replace 时有效）')

    # 添加可选参数
    parser.add_argument('-r', '--replace', action='store_true', help="原地替换 src_path")
    parser.add_argument('-d', '--dir', action='store_true', help="将 src_path 视为目录路径，并递归处理所有文件")

    # 解析参数
    args = parser.parse_args()

    # 检查参数约束
    if args.dir and not args.replace:
        parser.error("-d/--dir 必须与 -r/--replace 一起使用")

    # 处理目录模式
    if args.dir:
        process_directory(args.src_path)
    else:
        # 单文件模式
        run_one_file(args.src_path, args.dst_path, args.replace)

def process_directory(directory_path):
    """递归处理目录中的所有文件"""
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith("test.cc"):
                continue
            if file_name.endswith("test.cpp"):
                continue
            if file_name.endswith(".cc") or file_name.endswith(".cpp"):
                src_file_path: str = os.path.join(root, file_name)
                run_one_file(src_file_path, src_file_path, True)

def read_file(file_path: str) -> str:
    """Reads and returns the content of a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def write_file(file_path: str, content: str):
    """Writes content to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def format_code(code: str) -> str:
    """Formats the C++ code for better readability."""
    code = code.replace("{", "\n{\n")
    code = code.replace("}", "\n}\n")
    code = code.replace("if(", "if (")
    code = code.replace("for(", "for (")
    code = code.replace(" else", "\nelse")
    code = code.replace(";else", ";\nelse")
    return code

if __name__ == '__main__':
    main()
