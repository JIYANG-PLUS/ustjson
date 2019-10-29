# Use of this source code is governed by the MIT license.
__license__ = "MIT"

__all__ = [
    'split_contents_flag_after',
    'split_contents_flag_before'
]

from ..Constant import *

class ContentsFlagError(Exception): pass

def split_contents_flag_after(t_str: str, other_flag: str=OTHER_FLAG, 
    insert_char: str=INSERT_CHAR, standard_flag: str=STANDARD_FLAG, 
    standard_flag_wosc: str=STANDARD_FLAG_WOSC) ->str:
    '''将正文中的标记和内容前后分隔开，方便提取标题，主要是针对数字型编号。后式插入分割字符。
    
    other_flag: 其余的目录编号形式。
    insert_char: 选择何种字符作为分隔符，默认是空格，不建议修改该参数。
    return: 分离后的文本。
    '''

    if not isinstance(other_flag, str):
        raise ContentsFlagError('传入的目录标记不是字符串类型。')

    result_str = list( t_str )
    len_str = len( t_str )
    if len(result_str)>0 and result_str[0] in standard_flag_wosc+other_flag:
        i = 0
        while i < len_str-1:
            if result_str[i] in standard_flag+other_flag:
                if result_str[i+1] not in standard_flag+' '+other_flag: # 这里的空格字符是保证解析后正确性的关键
                    result_str.insert(i+1, insert_char)
                    len_str += 1
                    i += 1 # 跳过空格
            i += 1
    return ''.join( result_str )

def split_contents_flag_before(t_str: str, other_flag: str=OTHER_FLAG, 
    insert_char: str=INSERT_CHAR, standard_flag: str=STANDARD_FLAG, 
    standard_flag_wosc: str=STANDARD_FLAG_WOSC) ->str:
    '''将正文中的标记和内容前后分隔开，方便提取标题，主要是针对数字型编号。前式插入分割字符。
    
    特殊说明：本函数功能主要用于对提取后的目录的清洗操作。解析正文用不到本功能。
    other_flag: 其余的目录编号形式。
    insert_char: 选择何种字符作为分隔符，默认是空格，不建议修改该参数。
    return: 分离后的文本。
    '''
    if not isinstance(other_flag, str):
        raise ContentsFlagError('传入的字符标记不是字符串类型。')

    result_str = list( t_str )
    len_str = len( t_str )
    if len(result_str)>0 and result_str[0] in standard_flag_wosc+other_flag: # 只有具有标题编号开头的行才需要处理。
        i = 0
        while i < len_str-1:
            if result_str[i] not in standard_flag+' '+other_flag: # 这里的空格字符是保证解析后正确性的关键
                if result_str[i+1] in standard_flag+other_flag:
                    result_str.insert(i+1, insert_char)
                    len_str += 1
                    i += 1 # 跳过空格
            i += 1
    return ''.join( result_str )