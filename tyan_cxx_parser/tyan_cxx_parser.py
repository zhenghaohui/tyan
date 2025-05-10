import argparse
from math import remainder
from typing import List
from enum import Enum


class CodeItemType(Enum):
    CXX_SOURCE = "<cxx_source>"
    INCLUDE = "<include>"
    DEFINE = "<define>"
    COMMENT_LINE = "<comment>"
    DECLARE_CLASS = "<declare_class>"
    FUNCTION = "<function>"
    IF = "<if>"
    NAMESPACE = "<namespace>"
    VAR_SET = "<var_set>"
    VAR_ADD_SELF = "<var_add_self>"
    VAR_SUB_SELF = "<var_sub_self>"
    UNKNOWN = "<unknown>"


def go_through_head_and_body(from_line: int, to_line: int, raw_content: List[str],
                             left_bracket: chr = '{', right_bracket: chr = '}') -> (int, int, int):
    line = raw_content[from_line]
    remain_depth = line.count(left_bracket) - line.count(right_bracket)
    # go through function header
    while remain_depth == 0:
        line = raw_content[to_line]
        to_line += 1
        remain_depth += line.count(left_bracket) - line.count(right_bracket)
    head_end_line = to_line
    # go through function body
    while remain_depth > 0:
        line = raw_content[to_line]
        to_line += 1
        remain_depth += line.count(left_bracket) - line.count(right_bracket)
    return from_line, head_end_line, to_line

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

class CodeItem:
    def __init__(self, item_type: CodeItemType, head_content: List[str], body_content: List[str]):
        self.item_type: CodeItemType = item_type
        self.head_content: List[str] = head_content
        self.body_content: List[str] = body_content
        self.parts: List[CodeItem] = []

    def append_part(self, new_item: "CodeItem"):
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
            if line.find("(") != -1 and line.find(";") == -1:
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemFunction(self.body_content[from_line:head_end_line],
                                                  self.body_content[head_end_line:to_line]))
                print(f"{from_line}, {head_end_line}, {to_line}")
                continue

            # schema5: namespace
            if line.startswith("namespace "):
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemFunction(self.body_content[from_line:head_end_line],
                                                  self.body_content[head_end_line:to_line]))
                print(f"{from_line}, {head_end_line}, {to_line}")
                continue

            if line.startswith("if (") != -1:
                # todo: simple if without bracket
                from_line, head_end_line, to_line = go_through_head_and_body(from_line, to_line, self.body_content)
                self.append_part(CodeItemIf(self.body_content[from_line:head_end_line],
                                                  self.body_content[head_end_line:to_line]))
                print(f"{from_line}, {head_end_line}, {to_line}")
                continue


            # schema6: declare class
            if line.startswith("class ") and line.find(";") != -1:
                self.append_part(CodeItemDeclareClass(self.body_content[from_line:to_line]))
                continue

            # schema7: right bracket
            if line.startswith("}"):
                # just ignore
                continue

            # schema8: =
            if found_op(line, "="):
                self.append_part(CodeItemVarSet(self.body_content[from_line:to_line]))
                continue

            # schema9: +=
            if found_op(line, "+="):
                self.append_part(CodeItemVarAddSelf(self.body_content[from_line:to_line]))
                continue

            # schema10: -=
            if found_op(line, "-="):
                self.append_part(CodeItemVarSubSelf(self.body_content[from_line:to_line]))
                continue

            # print(line)

            # assert False
        for part in self.parts:
            part.parse()

    def parse(self):
        self.parse_body()

    def print_struct(self) -> str:
        result = f"{self.item_type.value}\n"
        for part in self.parts:
            result += part.print_struct()
        return result

    def print(self) -> str:
        result = "\n".join(self.head_content)
        for part in self.parts:
            result += "\n"
            result += part.print()
        return result


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


class CodeItemIf(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.IF, head_content, body_content)


class CodeItemNamespace(CodeItem):
    def __init__(self, head_content: List[str], body_content: List[str]):
        super().__init__(CodeItemType.NAMESPACE, head_content, body_content)


class CodeItemSourceCode(CodeItem):
    def __init__(self, body_content: List[str]):
        super().__init__(CodeItemType.CXX_SOURCE, [], body_content)

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


def main():
    parser = argparse.ArgumentParser(description='translate cxx src code into cxx-tyan src code')
    parser.add_argument('src_path', help='cxx源码输入文件路径')
    parser.add_argument('dst_path', help='cxx-tyan源码输出文件路径')
    args = parser.parse_args()
    print(f"Parsing {args.src_path} > {args.dst_path} ...")

    with open(args.src_path, "r", encoding="utf-8") as src_file:
        src_code = src_file.read()

    src_code: str = src_code.replace("{", "{\n")
    src_code: str = src_code.replace("}", "\n}")
    src_code: str = src_code.replace("if(", "if (")
    raw_content: List[str] = [line.strip() for line in src_code.split("\n") if len(line.strip()) > 0]

    code_tree = CodeItemSourceCode(raw_content)
    code_tree.parse()

    with open(args.dst_path, "w", encoding="utf-8") as dst_file:
        dst_file.write(code_tree.print())


if __name__ == '__main__':
    main()
