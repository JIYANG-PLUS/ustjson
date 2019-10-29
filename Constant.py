# Use of this source code is governed by the MIT license.
__license__ = "MIT"

from typing import *

# 关于下面这些参数，是程序很敏感的部分，因此不直接放在函数的参数中，以免使用者在一些环节考虑不周而出错。
__all__ = [
    'OTHER_PUNCTUATION',
    'REPLACE_CHAR',
    'STANDARD_FLAG',
    'STANDARD_FLAG_WOSC',
    'OTHER_FLAG',
    'INSERT_CHAR',
    'ID_SPLIT_CHAR',
    'LINE_END_CHAR',
    'CATALOG_FLAG_LEN',
    'CATALOG_WORDS',
    'IDENTIFIER',
    'ID',
    'REGISTRY',
    'ROOT',
    'TIME',
    'TITLE',
    'TREE_TYPE',
    'CHILDREN',
    'TEXT',
    'HEAD',
    'DATA',
    'TABLE',
    'PRIOR',
    'TEMP',
    'TEXT_END',
    'EXCELSCREENVALUE',
    'EXCELFLAG',
    'REPLACE_TABLE',
    'RECOGNIZE_TABLE'
]

OTHER_PUNCTUATION = '．.' # 泛空字符的非正式补充。
REPLACE_CHAR = ' ' # 连续泛空字符合并为空格，这也是程序的默认值，不建议更改。
INSERT_CHAR = ' ' # 目录清洗用的插入符，默认为空格，不建议更改。本参数和 REPLACE_CHAR 无差别，若要更改请一同更改为一样的字符。

STANDARD_FLAG = '0123456789.' # 预存的标题编号全部特征
STANDARD_FLAG_WOSC = '0123456789' # WOS表示 without split char
OTHER_FLAG = '' # 关于标题特征的补充，如：一、二等。默认为空。程序中的默认值为[0-9.]。补充的特征符号不能有连接符性质的符号。
ID_SPLIT_CHAR = '.' # 标题编号间的分隔符
LINE_END_CHAR = ['。','.'] # 默认句子是以中文句号结尾。或者可以是其它字符结尾，根据真实情况而定。主要用于清洗数据。

# 其它一些阈值设定
CATALOG_FLAG_LEN = 20 # 检测目录起始，设定长度阈值为9，实际最大为8。经实测阈值越大越好，但阈值越大越可能出现不可控的解析结果。
CATALOG_WORDS = ('条款目录', '目录') # 正常情况下目录起始的标志

# 编号节点类型的设定
IDENTIFIER = str

# 其他有关节点的alias
ID, TITLE = str, str # 标题编号和标题
TREE_TYPE = Dict[str,Dict] # 树节点特征
REGISTRY = Dict[str,Dict] # 注册表类型

# 节点的路径搜索用名
ROOT = 'root' # 标记是否是路径源
TIME = 'time' # 创建json文档的时间
TITLE = 'title' # 原文档名
CHILDREN = 'children' # 孩子节点搜索名
TEXT = 'text' # 正文的根节点搜索名，暂时没用到
HEAD = 'head' # 标题搜索名
DATA = 'data' # 节点的数据域
TABLE = 'table' # 表格节点
PRIOR = 'prior' # 前指针
TEMP = 'temp' # 临时数据存储域，可增强程序的容错性
TEXT_END = '99999 END' # 标志文本的结束

# 利用pdfminer提取表格的筛选阈值
EXCELSCREENVALUE = 3 # 去燥
EXCELFLAG = "表格 Here is a table Big tables 编号" # 提示信息

# 目录编号字符替换对照表，一般根据实际情况调用
REPLACE_TABLE = {
    '0': {
        '一': '1',
        '二': '2',
        '三': '3',
        '四': '4',
        '五': '5',
        '六': '6',
        '七': '7',
        '八': '8',
        '九': '9',
        '十': '10'
    }
}

# 用于深入辨识子节点的内置对照样式表
RECOGNIZE_TABLE = [
    '0123456789、', # 注意：所有用于区分不同标题的标点符号必须放在最后！！！程序识别中是以最后一个标点符号来区分不同编号的！！！
    '0123456789.',
    '(0123456789)', # 等价于：'0123456789)'
    '（0123456789）', # 等价于：'0123456789）'
    '（一二三四五六七八九十百）', # 等价于：'一二三四五六七八九十百）'
    '(一二三四五六七八九十百)', # 等价于：'一二三四五六七八九十百)'
    '一二三四五六七八九十百、',
    f'<{CATALOG_FLAG_LEN}' # 长度阈值判断必须是最后一个！！！必须是！！！修改本参数时需要特别注意！！！
]