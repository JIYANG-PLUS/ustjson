"""Special texts transformed into json.

ustjson is a tool to transfrom Unstructured terms text into JSON.
"""

__author__ = "Huge Yellow Dog (jiyangj@foxmail.com)"
__version__ = "1.1.0"
__copyright__ = "Copyright (c) 2019-2019 Huge Yellow Dog"
# Use of this source code is governed by the MIT license.
__license__ = "MIT"
name = "ustjson"

__all__ = [
    'SpecialText',
    'TreeBuilder',
    'read_txt',
    'replace_id_feature'
]

from .Constant import *
from .Capture import Capturer
from .Capture._Builder import *
from typing import List,Tuple,Dict,NoReturn,Callable,Any
import os, re
import json, pprint

class LimitError(Exception): pass
class ReplaceError(IndexError): pass

class SpecialText():
    def __init__(self, tree, *args, **kwargs):
        self.tree = tree

    def to_json(self, path=os.getcwd(), file_name='test.json', *, skipkeys=False, 
        ensure_ascii=False, check_circular=True, allow_nan=True, cls=None, indent=4, 
        separators=(',', ':'), default=None, sort_keys=True, **kw) ->NoReturn:
        """保存为json文件。
        
        有关参数的解释参考python官方解释文档。
        """
        print('json文件保存到：'+os.path.join(path, file_name))
        with open(os.path.join(path,file_name),'w',encoding='utf-8') as json_file:
            json.dump(self.tree,json_file,skipkeys=skipkeys, ensure_ascii=ensure_ascii, 
                check_circular=check_circular, allow_nan=allow_nan, cls=cls, indent=indent, 
                separators=separators, default=default, sort_keys=sort_keys)

    def to_pickle(self): pass # 预备功能，可能在未来版本中实现。

    def perfect_tree(self, now_time, title):
        """完善树结构信息"""
        self.tree[TIME] = now_time
        self.tree[TITLE] = title

class TreeBuilder():
    def __init__(self, *, insert_char: str=INSERT_CHAR, 
        other_flag: str=OTHER_FLAG, id_split_char: str=ID_SPLIT_CHAR, 
        standard_flag: str=STANDARD_FLAG, **kwargs):
        if bool(kwargs) and 'catalog' in kwargs: # 支持构造函数直接初始化树结构。
            self.tree = build_tree(Capturer.convert_catalog_to_pair_format(
                kwargs['catalog'],insert_char,other_flag,id_split_char,standard_flag),id_split_char)
        else: self.tree = {}

    def begin_bulid_by_catalog(self, catalog: List[Tuple[ID,TITLE]], insert_char: str=INSERT_CHAR, 
        other_flag: str=OTHER_FLAG, id_split_char: str=ID_SPLIT_CHAR, 
        standard_flag: str=STANDARD_FLAG) ->TREE_TYPE:
        """整体结构的初步构建与准备。"""
        self.tree = build_tree(Capturer.convert_catalog_to_pair_format(
            catalog,insert_char,other_flag,id_split_char,standard_flag),id_split_char)

    def allocate_text_for_eachNode(self, text: List[str], 
        id_split_char: str=ID_SPLIT_CHAR, other_flag: str=OTHER_FLAG, 
        insert_char: str=INSERT_CHAR, standard_flag: str=STANDARD_FLAG, 
        standard_flag_wosc: str=STANDARD_FLAG_WOSC, initials: str=None, 
        text_end=TEXT_END) ->NoReturn:
        """先分配各个节点的数据。最大限度避免解析失误。"""
        return insert_allText_to_eachNode(self.tree,text,id_split_char,other_flag,
            insert_char,standard_flag,standard_flag_wosc,initials,text_end)

    def build_data_and_sub_tree_node(self, temp_ids: List[ID], 
        NPL_judge_func: Callable[[str],bool] = None,
        id_split_char: str=ID_SPLIT_CHAR, other_flag: str=OTHER_FLAG, 
        insert_char: str=INSERT_CHAR, standard_flag: str=STANDARD_FLAG, 
        line_end_char: str=LINE_END_CHAR, recognize_table: str= RECOGNIZE_TABLE) ->NoReturn:
        """子节点的扩张与DATA域的填充。
        
        tree: 正文结构树。
        temp_ids: 填充过TEMP域的正文节点。
        """
        build_data_and_sub_tree(self.tree, temp_ids, NPL_judge_func, id_split_char, other_flag, 
            insert_char, standard_flag, line_end_char, recognize_table)

    def build_table_auto_or_manual(self, appoint: List[str]=None, table_data: List[Any]=None, 
        temp_ids: List[ID]=None, id_split_char: str=ID_SPLIT_CHAR, 
        other_flag: str=OTHER_FLAG, standard_flag: str=STANDARD_FLAG, recognize_table: str= RECOGNIZE_TABLE, 
        insert_char: str=INSERT_CHAR, line_end_char: str=LINE_END_CHAR) ->List[ID]:
        """填充表格数据。"""
        return build_table(self.tree, appoint=appoint, table_data=table_data, temp_ids=temp_ids, id_split_char=id_split_char, 
            other_flag=other_flag, standard_flag=standard_flag, recognize_table=recognize_table, 
            insert_char=insert_char, line_end_char=line_end_char)

def read_txt(path: str, limit_lines: int=None) ->str:
    '''用于从txt文档中读取数据，默认忽略空行。

    path: 文件的绝对路径或相对路径。
    limit_lines: 限制读取的行数，空行不在计数之中。
    内容编码为 utf-8。
    return: 由每一行数据组成的列表，不包含换行符。
    '''
    with open(path, 'r', encoding='utf-8') as txt:
        if txt.readable():
            content = [x for x in txt.read().splitlines() if bool(x)]
    if limit_lines == None:
        return content
    else:
        if limit_lines <= 0:
            raise LimitError('限制读取的行数必须大于0.')
        else:
            return content[:limit_lines]

def _rename(initials: str, cut_char: str, table_type: str, 
    replace_table: Dict[str,Dict[str,str]]=REPLACE_TABLE) ->str:
    """通过REPALCE_TABLE对照表进行重命名。
    
    替换类型：一、二、三、、、
    目前功能局限于替换：一 ~ 九十九。
    """
    replace_table = replace_table[table_type]
    try:
        if cut_char in replace_table:
            return initials+replace_table[cut_char]
        elif len(cut_char) == 3:
            s_cut_char = cut_char.split('十')
            return initials+str(int(replace_table[s_cut_char[0]])*10+int(replace_table[s_cut_char[1]]))
        else:
            i = cut_char.index('十')
            if i == 0:
                return initials+str(10+int(replace_table[cut_char[1]]))
            else:
                return initials+str(int(replace_table[cut_char[0]])*10)
    except: raise ReplaceError('替换失败。')

def replace_id_feature(content: List[str], patt, table_type: str, 
    initials: str, replace_table: Dict[str,Dict[str,str]]=REPLACE_TABLE) ->List[str]:
    """替换标题编号，以让程序更容易理解层次关系！
    content: 正文内容列表。
    patt: 正则表达式对象。
    replace_table: 标题字符替换表。
    initials: 替换后的标志性首字符。
    return: 替换后的正文内容列表。
    """
    replace_content = []
    for c in content:
        try:
            cut_char = patt.match(c).group(1)
            f_char = _rename(initials, cut_char, table_type, replace_table)
            replace_content.append(patt.sub(f_char, c))
        except:
            replace_content.append(c)

    return replace_content

if __name__ == "__main__":
    import sys
    params = sys.argv
    print(params)