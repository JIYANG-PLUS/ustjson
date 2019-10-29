"""Various tools to clean texts.
"""

# Use of this source code is governed by the MIT license.
__license__ = "MIT"

__all__ = [
    'Cleaner', # 清洗工具包
]

_Cleaner_Info = [
    'clean_content_first', # 测试功能
    'before_capture_catalog_clean', # 提取目录前的清洗，已在Capture中集成
    'clean_catalog_again', # 提取目录后的清洗，已在Capture中集成
    'clean_text_again' # 对正文的再次清洗，在_Builder中集成
]

from ._Delete import *
from ._Judge import *
from ._Combine import *
from ._Split import *
from typing import List,Tuple
from ..Constant import *
import warnings, pprint

try:
    from functools import reduce
except: pass

class Cleaner():
    def __init__(self, *args, **kwargs): pass
    
    @classmethod
    def before_capture_catalog_clean(cls,content: List[str],
        other_punctuation=OTHER_PUNCTUATION,
        replace_char=REPLACE_CHAR,other_flag=OTHER_FLAG,
        insert_char=INSERT_CHAR,standard_flag: str=STANDARD_FLAG,
        standard_flag_wosc: str=STANDARD_FLAG_WOSC) ->List[str]:
        """对目录提取之前的清洗。本次清洗不分正文和目录。指清洗全部。
        
        content: 要清洗的字符串。
        其余的为一些常量设置。
        return: 清洗后的字符串列表。
        """

        # 先对源数据进行初步清洗
        clean_data = [clean_and_combine_series_single(s,other_punctuation='', # 这里必须传入空值。
            replace_char=replace_char) for s in 
            delete_head_tail_space(content,other_punctuation=other_punctuation)]
        # 为方便目录的提取和判断，再次清洗，主要在于分离标题编号，以便让提取更准确。
        clean_data = [split_contents_flag_before(
            split_contents_flag_after(x,other_flag,insert_char,standard_flag,standard_flag_wosc),
            other_flag,insert_char,standard_flag,standard_flag_wosc) for x in clean_data] # 前后式分离
        # 将分散的标题编号进行整合
        clean_data = [combine_split_ids(x,insert_char,other_flag,standard_flag) for x in clean_data]
        return clean_data

    @classmethod
    def clean_catalog_again(cls, catalog: List[str],insert_char: str=INSERT_CHAR, 
        other_flag: str=OTHER_FLAG, id_split_char: str=ID_SPLIT_CHAR, 
        standard_flag: str=STANDARD_FLAG) ->List[str]:
        """对成功提取出来的目录再次清洗，本函数只针对原文本中有目录的情况。"""

        warn_info = """\
        如果原文中没有目录信息，且目录信息为后期合成的，那么本函数将不适用人工合成的目录清洗。\
        """.strip(' ')
        warnings.warn(warn_info, DeprecationWarning)

        # 一行只有单个数值的，删除
        catalog = [x for x in catalog if len(x)>1]

        i, len_catalog = 0, len(catalog)
        while i < len_catalog: # 深度清洗目录数据，降低分解误差，删除一些不必要的信息
            if not reduce(lambda a,b: a or b,[judge_id(x,other_flag,id_split_char,standard_flag) for x in catalog[i].split(insert_char)]):
                catalog.pop(i)
                len_catalog -= 1
            else: # 边界值和无关值进行删除。
                now_content = catalog[i]
                if now_content[0] not in standard_flag+other_flag:
                    j, len_now = 0, len(now_content)
                    while j < len_now:
                        if now_content[j] in standard_flag+other_flag:
                            break
                        j += 1
                    catalog[i] = catalog[i][j:]
                i += 1
        return [combine_between_two_ids_text(x,insert_char,other_flag,id_split_char,standard_flag) for x in catalog] # 离散标题合并
    
    @classmethod
    def clean_text_again(cls, text: List[str], id_split_char: str=ID_SPLIT_CHAR, 
        other_flag: str=OTHER_FLAG, insert_char: str=INSERT_CHAR, 
        standard_flag: str=STANDARD_FLAG, standard_flag_wosc: str=STANDARD_FLAG_WOSC) ->List[str]:
        """对成功提取出来的正文进行再次清洗。貌似该功能和初步清洗冲突了，实际上这一步在开始已经实现，后期会优化。"""
        return [combine_split_ids(y,insert_char,other_flag,standard_flag) for y in 
            [split_contents_flag_before(x,other_flag,insert_char,standard_flag,standard_flag_wosc) for x in
            [split_contents_flag_after(s,other_flag,insert_char,standard_flag,standard_flag_wosc) for s in text]]] # id标准化三步走