# Use of this source code is governed by the MIT license.
__license__ = "MIT"

from typing import Tuple,List,Any,NoReturn
import pdfplumber
from pdfminer.pdfdocument import PDFEncryptionError
from itertools import chain
from .Constant import *
from .CleanTools import Cleaner
import os
import pprint

# 表格数据
TITLE, CONTENTS = str, List[Any]
ONEROW = Tuple[TITLE, CONTENTS]
EXCEL = List[ONEROW]

class ReadPdfError(Exception): pass
class AbspathError(Exception): pass

def read_pdf(path: str, other_punctuation=OTHER_PUNCTUATION,
    replace_char=REPLACE_CHAR,other_flag=OTHER_FLAG,
    insert_char=INSERT_CHAR,standard_flag=STANDARD_FLAG,
    standard_flag_wosc=STANDARD_FLAG_WOSC) ->Tuple[str, EXCEL]:
    '''用于从pdf中读取数据，并提取其中的表格。

    path: 文件的绝对路径。
    return: 读取的所有文本内容和表格，用元组返回。
    '''

    # 判断是不是绝对路径
    if not os.path.isabs(path):
        raise AbspathError('此路径不是绝对路径。')

    try:
        COUNT = 0 # 表格计数，编号从0开始
        total_contents = []
        total_excel = []
        with pdfplumber.open( path ) as pdf:
            total_contents = list()
            for page in pdf.pages:
                if bool(page.extract_text()):
                    contents = page.extract_text().splitlines()
                    total_contents.extend( Cleaner.before_capture_catalog_clean(
                        contents[:-1],other_punctuation,
                        replace_char,other_flag,
                        insert_char,standard_flag,standard_flag_wosc) ) # 剔除pdfminer自带的页码元素
                excel_text = page.extract_tables() # 提取表格数据
                if bool(_screen_excel(excel_text)):
                    total_excel.extend(excel_text)
                    """
                    # 如果表格检测通过，就在本页面最后一行插入标识行，用于锁定位置，方便后续提取
                    for i in range(len(excel_text)):
                        total_contents.append(f'{EXCELFLAG}{COUNT}') # 插入标记
                        COUNT += 1 # 编号连续递增，用连续表示一个页面有多个表格
                    pprint.pprint(excel_text)
                    """
    except PDFEncryptionError:
        raise ReadPdfError('此文档编码无法解析。')
    else:
        return total_contents,total_excel

def _screen_excel(first_excel: List[Any]) ->List[Any]:
    '''用阈值筛选可能的表格数据'''
    combine = list(chain.from_iterable(first_excel))
    if len(combine) < EXCELSCREENVALUE:
        return []
    else:
        return combine