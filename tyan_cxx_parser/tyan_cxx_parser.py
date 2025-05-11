import argparse
from math import remainder
from types import new_class
from typing import List
from enum import Enum
import re


class CodeItemType(Enum):
    CXX_SOURCE = "<cxx_source>"
    INCLUDE = "<include>"
    DEFINE = "<define>"
    COMMENT_LINE = "<comment>"
    DECLARE_CLASS = "<declare_class>"
    FUNCTION = "<function>"
    IF = "<if>"
    FOR = "<for>"
    SINGLE_SENTENCE = "<single-sentence>"
    NAMESPACE = "<namespace>"
    VAR_SET = "<var_set>"
    VAR_ADD_SELF = "<var_add_self>"
    VAR_SUB_SELF = "<var_sub_self>"
    ASSERT = "<assert>"
    PURE_DOMAIN = "<pure_domain>"
    ELSE = "<else>"
    UNKNOWN = "<unknown>"


def go_through_head_and_body(from_line: int, to_line: int, raw_content: List[str],
                             left_bracket: chr = '{', right_bracket: chr = '}') -> (int, int, int):
    line = raw_content[from_line]
    remain_depth = line.count(left_bracket) - line.count(right_bracket)
    remain_depth_par = line.count("(") - line.count(")")
    # go through function header
    while remain_depth == 0:
        if line.count(left_bracket):
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
    while to_line < len(raw_content):
        line = raw_content[to_line]
        to_line += 1
        if line.find(';') != -1:
            break
    return from_line, to_line

def found_op(line: str, op: str) -> bool:
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
        if len(updated_content) == 0 or updated_content[-1].count("// ") or updated_content[-1].count("/*"):
            updated_content.append(line)
            continue
        updated_content[-1] += line
    return updated_content


class CodeItem:
    def __init__(self, item_type: CodeItemType, head_content: List[str], body_content: List[str]):
        self.item_type: CodeItemType = item_type
        self.head_content: List[str] = short_head_content(head_content)
        self.body_content: List[str] = body_content
        self.parts: List[CodeItem] = []
        self.parent: "CodeItem" = None
        self.is_under_function = False

    def append_part(self, new_item: "CodeItem"):
        new_item.parent = self
        new_item.is_under_function = self.is_under_function or isinstance(new_item, CodeItemFunction)
        self.parts.append(new_item)

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

            # schema4: function
            if not self.is_under_function and line.find("(") != -1 and line.find(";") == -1:
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemFunction(self.body_content[from_line:head_end_line],
                                                  self.body_content[head_end_line:to_line]))
                continue

            # schema5: namespace
            if line.startswith("namespace "):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemNamespace(self.body_content[from_line:head_end_line],
                                                   self.body_content[head_end_line:to_line]))
                continue

            # schema: assert
            if line.startswith("assert("):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content,
                                                                             '(', ')')
                self.append_part(CodeItemAssert(self.body_content[from_line:to_line], []))
                continue

            if line.startswith("if (") :
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

            # schema11: for
            if line.startswith("for ("):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemFor(self.body_content[from_line:head_end_line],
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

            # schema: =
            if found_op(line, "="):
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
        self.parse_body()

    def print(self, depth: int = -2, add_tyan_code=False) -> str:
        result = ""
        for line in self.head_content:
            result += "\n"
            result += "  " * depth
            result += line
        result += f" /* {self.item_type.value} */"
        for part in self.parts:
            result += part.print(depth + 2, add_tyan_code)
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


class CodeItemFunction(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.FUNCTION, head_content, body_content)

    def print(self, depth: int = -2, add_tyan_code=False) -> str:
        result = super().print(depth)
        result += "\n"
        result += "  " * depth
        result += "}"
        return result


class CodeItemIf(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.IF, head_content, body_content)

    def print(self, depth: int = -2, add_tyan_code=False) -> str:
        result = super().print(depth)
        if any("{" in line for line in self.head_content):
            result += "\n"
            result += "  " * depth
            result += "}"
        return result


class CodeItemElse(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.ELSE, head_content, body_content)

    def print(self, depth: int = -2, add_tyan_code=False) -> str:
        result = super().print(depth)
        if any("{" in line for line in self.head_content):
            result += "\n"
            result += "  " * depth
            result += "}"
        return result


class CodeItemFor(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.FOR, head_content, body_content)

    def print(self, depth: int = -2, add_tyan_code=False) -> str:
        result = super().print(depth)
        if any("{" in line for line in self.head_content):
            result += "\n"
            result += "  " * depth
            result += "}"
        return result


class CodeItemSingleSentence(CodeItem):
    def __init__(self, head_content: List[str]):
        super().__init__(CodeItemType.SINGLE_SENTENCE, head_content, [])

class CodeItemNamespace(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.NAMESPACE, head_content, body_content)

    def print(self, depth: int = -2, add_tyan_code=False) -> str:
        result = super().print(depth)
        result += "\n" + "  " * depth + "}"
        return result

class CodeItemAssert(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.ASSERT, head_content, body_content)


class CodeItemSourceCode(CodeItem):
    def __init__(self, body_content: List[str]):
        super().__init__(CodeItemType.CXX_SOURCE, [], body_content)

    def print(self, depth: int = -2, add_tyan_code=False) -> str:
        result = ""
        if add_tyan_code:
            result += "\n" + "  " * depth
            result += '#include "tyan.h"'
        result += super().print(depth, add_tyan_code)
        return result


class CodeItemDeclareClass(CodeItem):
    def __init__(self, head_content: List[str]):
        super().__init__(CodeItemType.DECLARE_CLASS, head_content, [])


class CodeItemVarSet(CodeItem):
    def __init__(self, head_content: List[str]):
        super().__init__(CodeItemType.VAR_SET, head_content, [])


class CodeItemVarAddSelf(CodeItem):
    def __init__(self, head_content: List[str]):
        super().__init__(CodeItemType.VAR_ADD_SELF, head_content, [])


class CodeItemVarSubSelf(CodeItem):
    def __init__(self, head_content: List[str]):
        super().__init__(CodeItemType.VAR_SUB_SELF, head_content, [])


class CodeItemPureDomain(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.PURE_DOMAIN, head_content, body_content)

    def print(self, depth: int = -2, add_tyan_code=False) -> str:
        result = super().print(depth)
        result += "\n"
        result += "  " * depth
        result += "}"
        return result


def standard_code(content: str) -> str:
    # Remove block comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove line comments
    content = re.sub(r'//.*', '', content)
    # Remove all whitespace characters (spaces, tabs, newlines)
    content = ''.join(content.split())

    # Insert a newline character every 100 characters
    content = '\n'.join([content[i:i + 100] for i in range(0, len(content), 100)])
    return content


def main():
    parser = argparse.ArgumentParser(description='translate cxx src code into cxx-tyan src code')
    parser.add_argument('src_path', help='cxx源码输入文件路径')
    parser.add_argument('dst_path', help='cxx-tyan源码输出文件路径')
    args = parser.parse_args()

    print(f"Parsing {args.src_path} > {args.dst_path} ...")

    # Read source code
    src_code = read_file(args.src_path)

    # Standardize and process the code
    standardized_code = standard_code(src_code)
    write_file(args.src_path + ".std", standardized_code)

    formatted_code = format_code(src_code)
    raw_content = [line.strip() for line in formatted_code.split("\n") if line.strip()]

    # Parse and generate output
    code_tree = CodeItemSourceCode(raw_content)
    code_tree.parse()

    write_file(args.dst_path, code_tree.print(-2, True))
    write_file(args.dst_path + ".std", standard_code(code_tree.print()))

    # Verify that the standardized source and output match
    assert read_file(args.src_path + ".std") == read_file(args.dst_path + ".std"), "Standardized files do not match!"


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
