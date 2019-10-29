# Use of this source code is governed by the MIT license.
__license__ = "MIT"

__all__ = [
    'delete_head_tail_space', # 删除首尾泛空字符，这通常是程序处理的第一步。
    'common_clean_repeat_word' # 清楚重复字符。如：'我我我爱爱爱爱中国' 会清洗成 '我爱中国'。
]

import re
import warnings
from typing import List

class PunctuationError(Exception): pass

def delete_head_tail_space(content: str, other_punctuation: str='') ->List[str]:
    """删除首尾泛空字符。
    
    content: 要处理的字符串列表。
    other_punctuation: 其余非正规的泛空字符。
    return: 处理后的字符串列表。
    """
    delete_chars = ' 　 \t\n\r\f\v' + other_punctuation
    return [x.strip(delete_chars) for x in content if bool(x.strip(delete_chars))]

def clean_series_space(t_str: str, other_punctuation: str='', replace_char: str=' ') ->str:
    """将分割符统一化，连续的泛空将删减至单一空格，方便后面数据的分解与整合。
    
    不严谨说明：这里的泛空字符可以不严格地理解为一切想缩减删除替换的特殊字符。
    other_punctuation: 其他的泛空字符。
    replace_char: 替换字符默认是空格，可自定义替换符。对全文进行替换的时候不建议更改默认值。
    但可利用此接口实现部分特殊需求，如：替换连续重复单一值为一个值。
    return: 清洗后的紧凑字符串。
    """
    warn_info = """\
    本函数和combine_series_single配合使用时，建议用clean_and_combine_series_single一个函数替代.\
    """.strip(' ')
    warnings.warn(warn_info, DeprecationWarning)

    if not isinstance(other_punctuation, str):
        raise PunctuationError('传入标点符号格式错误。')

    flag = ' 　 \t\n\r\f\v'+other_punctuation
    t_str = t_str.strip(flag)
    t_str_len, result_str = len( t_str ), list( t_str )
    i = 0
    while i < t_str_len-1:
        if result_str[i] in flag and result_str[i+1] in flag:
            result_str[i] = replace_char
            result_str.pop( i+1 )
            t_str_len -= 1
            i -= 1
        i += 1

    return ''.join( result_str )

def _re_clean_repeat_word(t_str: str) ->str:
    """正则清理连续重复的字，效率不高。功能暂定，未使用。
    
    t_str: 要清理的字符串。
    return: 清理重复值之后的字符串。
    """
    patt = r'(?P<repeat>\w)\1'
    result_str, counts = re.subn(patt, repl=lambda x:x['repeat'], string=t_str)
    while counts:
        result_str, counts = re.subn(patt, repl=lambda x:x['repeat'], string=result_str)
    return result_str

def common_clean_repeat_word(t_str: str) ->str:
    """常规清理连续重复的字。功能暂定，未使用。
    
    t_str: 要清理的字符串。
    return: 清理重复值之后的字符串。
    """
    list_t_str = list(t_str)
    for i in range(1,len(list_t_str))[::-1]:
        if list_t_str[i] == list_t_str[i-1]:
            list_t_str.pop(i)
    return ''.join(list_t_str)

def delete_puredigit(lines: List[str]):
    """删除纯数字字符的行。

    包括删除一行中只有数字和标点的行。（只有数字和标点的行极有可能是页码）
    """