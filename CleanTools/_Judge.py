# Use of this source code is governed by the MIT license.
__license__ = "MIT"

from typing import List,Tuple,Any,NoReturn
from ..Constant import *

try:
    from functools import reduce
except: pass

__all__ = [
    'get_catalogue_begin_index',
    'judge_catalog_end',
    'judge_id',
    'check_routes_complete_and_fill' # 判断路径的完整性，并用指定值填充标题名称。
]

class RouteGenerateError(Exception): pass

def get_catalogue_begin_index(content: List[str],
    catalog_flag_len: int=CATALOG_FLAG_LEN,
    catalog_words: Tuple[str]=CATALOG_WORDS) ->Tuple[bool,int]:
    """判断该文档有没有目录，并返回目录开始的下标。
    
    content: 按行拆分的文本列表。
    catalog_flag_len: 目录其实标志的长度阈值。
    catalog_words: 有可能的目录特征的值组成的元组。
    return: 一个二元组，第一个值为有没有目录，第二个值为目录开始的索引。
    """
    for index, item in enumerate(content):
        if len(item)<catalog_flag_len and reduce(lambda a,b: a or b,((x in item) for x in catalog_words)):
            return True, index
    return False, -1

def judge_catalog_end(next_number: str, exist_numbers: List[IDENTIFIER], 
    id_split_char: str=ID_SPLIT_CHAR) ->bool:
    '''判断是否是目录截取的终点。
    
    next_number: 本次要判断的编号。
    exist_numbers: 程序已经认识的编号。
    return: 本次编号所在的行是否标志着目录提取的截止。
    '''
    for item in exist_numbers:
        if next_number.strip(id_split_char) == item.strip(id_split_char): return True
    return False

def judge_id(_id: str, other_flag: str=OTHER_FLAG, 
    id_split_char: str=ID_SPLIT_CHAR, standard_flag: str=STANDARD_FLAG, 
    initials: str=None) ->bool:
    """判断是否符合已有的标题特征。
    
    _id: 参与判断的标题编号。
    other_flag: 其它标题特征，默认为全局变量。
    initials: 限制首字母。
    return: 布尔值真假。
    """
    strip_id = _id.strip(id_split_char)
    if bool(strip_id) == False: return False # 全为标题编号分隔符的，不符合标题编号的特征。

    for i in strip_id: # 将编号逐个拆解并判断。
        if i not in standard_flag+other_flag: return False
    
    if initials == None:
        return True
    else:
        return (_id[0] == initials) # 用于首字母的标题编号的限制。

def _get_search_route(ids: ID, id_split_char: str=ID_SPLIT_CHAR) ->Tuple[str,List[ID]]:
    """根据标题编号获取完整搜索路径"""
    t_id = [s for s in ids.split(id_split_char) if bool(s)]
    if len(t_id) == 0: raise RouteGenerateError('路径为空，无法创建合法路径。')
    # 分解结果为单的，表示根节点，为双的表示有父节点，开始生成搜索路径
    if len(t_id) == 1: return ROOT, t_id
    results = [t_id[0]] # 组合
    for item in t_id[1:]:
        results.append( id_split_char.join([results[-1],item]) )
    return CHILDREN, results

def check_routes_complete_and_fill(tree: TREE_TYPE, _id: str, 
    missing_value: str='NULL', id_split_char: str=ID_SPLIT_CHAR) ->NoReturn:
    """判断路径是否完整，若不完整则补全，并用missing_value补全标题，默认为NULL"""
    routes = _get_search_route(_id, id_split_char)[1] # 不管是不是根节点
    for r in routes:
        if r not in tree:
            tree[r] = {}
            tree[r][HEAD] = missing_value
        tree = tree[r]
