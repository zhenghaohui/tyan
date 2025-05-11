# tyan :)

## tyan_cxx_parser 使用文档

`tyan_cxx_parser` 是一个用于解析 C++ 源代码并提取关键信息的脚本工具。它可以帮助开发者快速分析代码结构和内容。

主要用于统一化的注入生成代码的简单场景，但又不想使用完全体的复杂如 clang 等进行完备的源码解析工具的场景。

### 基本用法

```bash
python tyan_cxx_parser.py [options] <input_file>
```

### 参数说明

- `<input_file>`: 指定需要解析的 C++ 源文件路径。
- `-o, --output`: 可选参数，指定输出结果保存的文件路径，默认为标准输出。
- `-v, --verbose`: 可选参数，启用详细模式以显示更多解析信息。

### 结果示例

在每个部件前增加对应的标签

```c++
...
/* <include> */
#include "util/stop_watch.h"
/* <namespace> */
namespace ROCKSDB_NAMESPACE
{
    /* <declare_class> */
    class TableFactory;
    /* <function> */
    void hello(int a)
    {
    }
    /* <function> */
    TableBuilder* NewTableBuilder(const TableBuilderOptions& tboptions,
    WritableFileWriter* file)
    {
        /* <assert> */
        assert((tboptions.column_family_id ==
        TablePropertiesCollectorFactory::Context::kUnknownColumnFamily) ==
        tboptions.column_family_name.empty());
        /* <if> */
        if (a==20) b=1;
        /* <else> */
        else b=2;
        /* <var_set> */
        int a = 1 < 2 ? 10 : 20;
        /* <if> */
        if (a==20) b=1;
        /* <else> */
        else if (a==30) b=2;
...
```