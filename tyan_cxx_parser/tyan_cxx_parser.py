import argparse
from math import remainder
from typing import List
from enum import Enum


class CodeItemType(Enum):
    CXX_SOURCE = "<cxx_source>"
    INCLUDE = "<include>"
    DEFINE = "<define>"
    COMMENT_LINE = "<comment_line>"
    FUNCTION = "<function>"
    NAMESPACE = "<namespace>"
    UNKNOWN = "<unknown>"


class CodeItem:
    def __init__(self, item_type: CodeItemType, raw_content: List[str]):
        self.item_type: CodeItemType = item_type
        self.raw_content: List[str] = raw_content
        self.parts: List[CodeItem] = []

    def append_part(self, new_item: "CodeItem"):
        self.parts.append(new_item)

    def parse(self):
        pass

    def print_struct(self) -> str:
        result = f"{self.item_type.value}\n"
        for part in self.parts:
            result += part.print_struct()
        return result

class CodeItemInclude(CodeItem):
    def __init__(self, raw_content: List[str]):
        super().__init__(CodeItemType.INCLUDE, raw_content)

    def parse(self):
        pass


class CodeItemDefine(CodeItem):
    def __init__(self, raw_content: List[str]):
        super().__init__(CodeItemType.DEFINE, raw_content)

    def parse(self):
        pass


class CodeItemCommentLine(CodeItem):
    def __init__(self, raw_content: List[str]):
        super().__init__(CodeItemType.COMMENT_LINE, raw_content)

    def parse(self):
        pass


class CodeItemFunction(CodeItem):
    def __init__(self, raw_content: List[str]):
        super().__init__(CodeItemType.FUNCTION, raw_content)

    def parse(self):
        pass

class CodeItemNamespace(CodeItem):
    def __init__(self, raw_content: List[str]):
        super().__init__(CodeItemType.NAMESPACE, raw_content)

    def parse(self):
        pass


def go_through_bracket(from_line: int, to_line: int, raw_content: List[str]) -> (int, int):
    line = raw_content[from_line]
    remain_depth = line.count("{") - line.count("}")
    # go through function header
    while remain_depth == 0:
        line = raw_content[to_line]
        to_line += 1
        remain_depth += line.count("{") - line.count("}")
        # go through function body
    while remain_depth > 0:
        line = raw_content[to_line]
        to_line += 1
        remain_depth += line.count("{") - line.count("}")
    return from_line, to_line


class CodeItemSourceCode(CodeItem):
    def __init__(self, raw_content: List[str]):
        super().__init__(CodeItemType.CXX_SOURCE, raw_content)

    def parse(self):
        to_line = 0
        while to_line < len(self.raw_content):  # has next part
            from_line = to_line
            to_line = from_line + 1

            line = self.raw_content[from_line]

            # schema1: include
            if line.startswith("#include"):
                self.append_part(CodeItemInclude(self.raw_content[from_line:to_line]))
                continue

            # schema2: define
            if line.startswith("#define"):
                self.append_part(CodeItemDefine(self.raw_content[from_line:to_line]))
                continue

            # schema3: comment line
            if line.startswith("//"):
                self.append_part(CodeItemCommentLine(self.raw_content[from_line:to_line]))
                continue

            # schema4: function
            if line.find("(") != -1 and line.find(";") == -1:
                from_line, to_line = go_through_bracket(from_line, to_line, self.raw_content)
                self.append_part(CodeItemFunction(self.raw_content[from_line:to_line]))
                continue

            # schema5: namespace
            if line.startswith("namespace "):
                from_line, to_line = go_through_bracket(from_line, to_line, self.raw_content)
                self.append_part(CodeItemNamespace(self.raw_content[from_line:to_line]))
                continue

            assert False
        for part in self.parts:
            part.parse()

def main():
    parser = argparse.ArgumentParser(description='translate cxx src code into cxx-tyan src code')
    parser.add_argument('src_path', help='cxx源码输入文件路径')
    parser.add_argument('dst_path', help='cxx-tyan源码输出文件路径')
    args = parser.parse_args()
    print(f"Parsing {args.src_path} > {args.dst_path} ...")

    with open(args.src_path, "r", encoding="utf-8") as src_file:
        src_code = src_file.read()

    src_code: str = src_code.replace("{", "{\n")
    raw_content: List[str] = [line for line in src_code.split("\n") if len(line) > 0]

    code_tree = CodeItemSourceCode(raw_content)
    code_tree.parse()

    with open(args.dst_path, "w", encoding="utf-8") as dst_file:
        dst_file.write(code_tree.print_struct())


if __name__ == '__main__':
    main()
