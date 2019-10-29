# Use of this source code is governed by the MIT license.
__license__ = "MIT"

from ._Show import *
from typing import List,Any

class ShowError(IndexError): pass

def show(head: str, data: List[Any]):
    try:
        if head[0] == '$': # 约定的表格标题样式，必须是这样！！！
            data.insert(0, [str(x) for x in data.pop(0)])
            show_table(head, data)
        else: raise ShowError('表格内容不符合约定，无法显示。')
    except: raise ShowError('表格内容不符合约定，无法显示。')