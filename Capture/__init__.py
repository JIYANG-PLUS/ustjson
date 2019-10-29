"""Various tools to handle Catalog.
"""
# 本模块返回的正文和阅读指引部分，并不是规整的数据，后期用到的时候，需要进行再次清洗。
# Use of this source code is governed by the MIT license.
__license__ = "MIT"

__all__ = [
    'Capturer', # 捕捉器
]

_Capturer_Info = [
    'test_catalog_exist', # 仅用来测试目录是否存在，并未用于整体功能中。
    'capture_catalog_and_body', # 从初步清洗后的文本中提炼目录、正文、阅读指引
    'convert_catalog_to_pair_format', # 用于处理capture_catalog_and_body输出的目录文本。
    'get_search_route', # 用于从标题编号中提取搜索路径。
    'get_current_node' # 获取当前标题编号下的末端节点。
] # 方便后期进行检查和改进，不喜误删。

from ..CleanTools._Judge import *
from ..Constant import *
from ..CleanTools import Cleaner
from typing import List,Tuple,Dict
import pprint

try:
    from functools import reduce
except: pass

class CatalogNotFound(IndexError): pass
class RouteGenerateError(Exception): pass
class RouteFoundError(Exception): pass

class Capturer():
    def __init__(self, *args, **kwargs): pass

    @classmethod
    def test_catalog_exist(cls, content: List[str]) ->Tuple[bool,int]:
        """用于检测文档是否存在目录。
        
        content: 以行为标准拆分的文本列表。
        return: 二元组，是否存在目录、目录的索引下标。
        """
        return get_catalogue_begin_index(content,
                catalog_flag_len=CATALOG_FLAG_LEN,
                catalog_words=CATALOG_WORDS)
    
    @classmethod
    def capture_catalog_and_body_text(cls,content: List[str],other_punctuation=OTHER_PUNCTUATION,
            replace_char=REPLACE_CHAR,other_flag=OTHER_FLAG,
            insert_char=INSERT_CHAR,standard_flag: str=STANDARD_FLAG,
            standard_flag_wosc: str=STANDARD_FLAG_WOSC,id_split_char: str=ID_SPLIT_CHAR,
            ) ->Tuple[List[str]]:
        """获取目录部分的全部内容。
        
        content: 全部的文本内容列表。
        index: 目录内容的起始位置。
        return: 目录内容列表。
        """

        # 提取目录前的初步清洗
        clean_data = Cleaner.before_capture_catalog_clean(content,
                    other_punctuation,replace_char,
                    other_flag,insert_char,
                    standard_flag,standard_flag_wosc)
        # 拿出目录
        catalog, index = cls.test_catalog_exist(clean_data)
        if catalog == False: raise CatalogNotFound('解析文档不存在目录。')

        len_clean_data = len(clean_data)
        i = index + 1 # 从第index+1行开始，解读标题
        exist_number = []
        while i < len_clean_data:
            t_clean_data = clean_data[i].split(insert_char)
            if not judge_catalog_end( t_clean_data[0], exist_number ): # 拿每一行分解出的第一个元素，和历史记录比较，如有重复即停止目录的提取
                exist_number.extend( t_clean_data )
                i += 1
            else:
                break
        return (Cleaner.clean_catalog_again(clean_data[index+1:i],insert_char,other_flag,id_split_char,standard_flag),
                clean_data[i:], clean_data[:index]) # 目录、正文、其余信息。

    @classmethod
    def convert_catalog_to_pair_format(cls, catalog: List[str], insert_char: str=INSERT_CHAR, 
        other_flag: str=OTHER_FLAG, id_split_char: str=ID_SPLIT_CHAR, 
        standard_flag: str=STANDARD_FLAG) ->List[Tuple[str,str]]:
        """将提取后的目录文本转换为：（标题编号+标题） 形式的列表"""
        list_catalog = []
        for line in catalog:
            split_line = line.split(insert_char)
            if len(split_line)%2 == 1:
                split_line.append('NULL') # 必须是偶数个，如果不是，添加一个空值，强制变为偶数个。
            for i in range(0,len(split_line),2):
                list_catalog.append((split_line[i],split_line[i+1]))
        # 再次确认标题编号格式的正确性，不符合格式的进行删除。一般情况下均符合。
        for i in range(len(list_catalog))[::-1]:
            if judge_id(list_catalog[i][0], other_flag, id_split_char, standard_flag)==False:
                list_catalog.pop(i)
        # 按照标题编号排序后返回
        return list(sorted(list_catalog,key=lambda x:x[0],reverse=False))

    @classmethod
    def get_search_route(cls, ids: ID, id_split_char: str=ID_SPLIT_CHAR) ->Tuple[str,List[ID]]:
        """根据标题编号获取完整搜索路径"""
        t_id = [s for s in ids.split(id_split_char) if bool(s)]
        if len(t_id) == 0: raise RouteGenerateError('路径为空，无法创建合法路径。')
        # 分解结果为单的，表示根节点，为双的表示有父节点，开始生成搜索路径
        if len(t_id) == 1: return ROOT, t_id
        results = [t_id[0]] # 组合
        for item in t_id[1:]:
            results.append( id_split_char.join([results[-1],item]) )
        return CHILDREN, results

    @classmethod
    def get_current_node(cls, root: TREE_TYPE, ids: ID, 
                id_split_char: str=ID_SPLIT_CHAR, other_flag: str=OTHER_FLAG, 
                standard_flag: str=STANDARD_FLAG, initials: str=None) ->TREE_TYPE:
        """获取当前标题编号下的节点。因为本功能是由查找父节点触发的，所以不存在编号正确而找不到路径的情况。"""
        # 补充ids异常，并抛出，待补充。。。不补充对整体运行暂无影响。
        if not judge_id(ids, other_flag, id_split_char, standard_flag, initials):
            raise RouteFoundError('标题编号不存在，路径不存在。无法定位节点位置。')
        routes = cls.get_search_route(ids,id_split_char)
        for _id in routes[1]:
            if root.get(_id) == None: # 如果父路径不存在，尝试修补为完整路径，缺失的部分用NULL代替。
                root[_id] = {}
                root[_id][HEAD] = 'NULL' # 后期填充内容时，尝试修复缺失值。
            root = root[_id]
        return root

    @classmethod
    def get_last_node(cls, root: TREE_TYPE, ids: ID, 
                id_split_char: str=ID_SPLIT_CHAR, other_flag: str=OTHER_FLAG, 
                standard_flag: str=STANDARD_FLAG) ->TREE_TYPE:
        """获取当前编号下的上一个节点"""
        if not judge_id(ids, other_flag, id_split_char, standard_flag):
            raise RouteFoundError('标题编号不存在，路径不存在。无法定位节点位置。')
        routes = cls.get_search_route(ids,id_split_char)
        for _id in routes[1][:-1]:
            if root.get(_id) == None: # 如果父路径不存在，尝试修补为完整路径，缺失的部分用NULL代替。
                root[_id] = {}
                root[_id][HEAD] = 'NULL' # 后期填充内容时，尝试修复缺失值。
            root = root[_id]
        return root
