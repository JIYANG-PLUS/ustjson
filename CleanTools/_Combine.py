# Use of this source code is governed by the MIT license.
__license__ = "MIT"

__all__ = [
    'clean_and_combine_series_single', # 去除连续泛空字符+合并连续单一值。
    'combine_between_two_ids_text', # 通常为目录清洗的最后一步。
    'combine_split_ids' # 对离散的标题编号进行合并。通常和Split模块的两个标题编号分离函数搭配使用。
]

import re
import warnings
from typing import List
from ._Judge import *
from ..Constant import *

try:
    from functools import reduce
except: pass

class PunctuationError(Exception): pass

def _clear_series_single_list(split_str: List[str], join_str: str=' '):
    """以拆分后的列表形式进行合并离散单一值的清理，这是本模块其它函数的共用功能模块化实现。
    
    split_str: 以某种标准拆分后的字符串列表。
    join_str: 用于重新连接的字符。
    return: 处理后的字符串。
    """
    len_split_str = len( split_str )
    flag_single = [ len(x)==1 for x in split_str ] # 布尔值标记是否为单
    i = 0
    while i < len_split_str-1:
        if flag_single[i]:
            j = i
            if flag_single[i+1]:
                j -= 1 # 表示i现在的位置即这里的j依旧为单一值，配合后面的i+=1达到效果。
            split_str[i] = split_str[i]+split_str[i+1]
            split_str.pop( i+1 )
            flag_single.pop( i+1 )
            len_split_str -= 1
            i = j
        i += 1
    return join_str.join( split_str )

def combine_series_single(t_str: str, insert_char: str=INSERT_CHAR) ->str:
    """在整合连续空格clean_series_space的基础上，整合连续的离散的单一值，自动向后聚拢，向前不聚拢。
    
    特殊说明：本函数会删除所有的空格字符，换句话说，空格字符程序处理时会主动忽略剔除。
    其实本函数与clean_series_space的功能可以合二为一，详情见clean_and_combine_series_single函数。
    保留这个函数只是为了纪念一下自己过去的思路。
    t_str: 要整合的字符串。
    return: 整合后的字符串。
    """

    warn_info = """\
    本函数和clean_series_space配合使用时，建议用clean_and_combine_series_single一个函数替代.\
    """.strip(' ')
    warnings.warn(warn_info, DeprecationWarning)
    split_str = [x for x in t_str.split(insert_char) if bool(x)]
    return _clear_series_single_list(split_str[:])

def clean_and_combine_series_single(t_str: str,
    other_punctuation: str='', replace_char: str=REPLACE_CHAR) ->str:
    '''利用正则，将 删除连续重复泛空字符 和 整合连续离散值 功能合二为一。

    t_str: 要整合的字符串。
    other_punctuation: 其他的泛空字符。
    replace_char: 替换字符默认是空格，可自定义替换符。对全文进行替换的时候不建议更改默认值。
    return: 整合后的字符串。
    '''

    if not isinstance(other_punctuation, str):
        raise PunctuationError('传入标点符号格式错误。')

    patt = r'[ 　 \t\n\r\f\v' + repr(other_punctuation) + r']'
    split_str = [x for x in re.split(patt, t_str) if bool(x)]
    return _clear_series_single_list(split_str[:], replace_char)

def _judge_digit_point(obj: str, other_flag: str=OTHER_FLAG, standard_flag: str=STANDARD_FLAG) ->bool:
    """专属本模块的判断语句。
    """
    rule = standard_flag+other_flag
    for i in obj:
        if i not in rule: return False
    return True


def combine_split_ids(t_str: str, insert_char: str=INSERT_CHAR, 
    other_flag: str=OTHER_FLAG, standard_flag: str=STANDARD_FLAG) ->str:
    """将分散的不规整的标题编号进行合成。

    例：1 .2合并成1.2。注意这里的连字符.。类似1 . 2这样的可以不用考虑，这属于连续的单字符，已在前面处理过。
    但本程序中均会处理。
    t_str: 要处理的字符串。
    sp_con_char: 分隔符。
    return: 处理后的字符串。
    """
    l_str = [x for x in t_str.split(insert_char) if bool(x)]
    # 分散的标题编号有三种表现形式。1. 2和1 .2和1 . 2。
    flag_l_str = [_judge_digit_point(x, other_flag, standard_flag) for x in l_str] # 布尔标记是否均具有标题编号的特征

    i, len_flag_l_str = 0, len(flag_l_str)
    while i < len_flag_l_str-1: # 如果连续为True，则将其合并
        if flag_l_str[i] and flag_l_str[i+1]:
            l_str[i] = l_str[i]+l_str[i+1]
            l_str.pop(i+1)
            flag_l_str.pop(i+1)
            len_flag_l_str -= 1
            i -= 1
        i += 1
    return insert_char.join(l_str)

def combine_between_two_ids_text(t_str: str, sp_con_char: str=INSERT_CHAR, 
    other_flag: str=OTHER_FLAG, id_split_char: str=ID_SPLIT_CHAR, 
    standard_flag: str=STANDARD_FLAG) ->str:
    """将目录中两个标题编号间的文本进行合并，防止出现目录提取的错误。
    
    特殊说明：对于缺少标题的将用 NULL 作为缺失值。
    t_str: 要处理的字符串。
    sp_con_char: 分隔符。
    return: 合并后的新的字符串。
    """

    l_str = t_str.split(sp_con_char)
    search_id_index = []
    for index, item in enumerate(l_str):
        if judge_id(item,other_flag,id_split_char,standard_flag):
            search_id_index.append( index )
    for i in range( len(search_id_index)-1 ):
        i_0, i_1 = search_id_index[i], search_id_index[i+1]
        l_str[i_0+1] = reduce( lambda x, y : x+y, l_str[i_0+1:i_1] )
        if i_0+2<len(l_str) and not judge_id(l_str[i_0+2],other_flag,id_split_char,standard_flag):
            l_str[i_0+2] = ''
    # 整合每行最后一个id下标后面的值，防止分解出现键值的错误，并补充缺失值
    last_id_index = search_id_index[-1]
    if last_id_index+1 < len(l_str):
        l_str[last_id_index+1:] = [reduce( lambda x, y : x+y, l_str[last_id_index+1:] )]
    else:
        l_str.append('NULL') # 标记缺失值（即缺失的标题）
    return sp_con_char.join( list(filter(lambda x : bool(x), l_str)) )

def combine_digit_leftright_text(lines: List[str]) ->List[str]:
    """合并数字和点左右的文本。
    
    主要用于分区节点内部TEMP域的再清洗。
    lines: 分区数据组成的列表。
    """
    patt = re.compile(r' ([0123456789.]+?) ')
    new_lines = []
    for line in lines:
        try:
            new_lines.append(patt.sub(repl=lambda x:x.group(1), string=line))
        except:
            new_lines.append(line)
    return new_lines