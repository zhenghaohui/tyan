import argparse


class CxxParser:
    def __init__(self, src_path: str, dst_path: str):
        self.src_file = open(src_path, "r", encoding="utf-8")
        self.dst_file = open(dst_path, "w", encoding="utf-8")

    def parse(self):
        print("/* <tyan> */", file=self.dst_file)
        for line in self.src_file:
            print(line, file=self.dst_file, end="")
        print("/* </tyan> */", file=self.dst_file)


def main():
    parser = argparse.ArgumentParser(description='translate cxx src code into cxx-tyan src code')
    parser.add_argument('src_path', help='cxx源码输入文件路径')
    parser.add_argument('dst_path', help='cxx-tyan源码输出文件路径')
    args = parser.parse_args()
    print(f"Parsing {args.src_path} > {args.dst_path} ...")

    parser = CxxParser(args.src_path, args.dst_path)
    parser.parse()


if __name__ == '__main__':
    main()
