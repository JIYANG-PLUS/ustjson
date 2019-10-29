"""Test json's Result.
"""

# Use of this source code is governed by the MIT license.
__license__ = "MIT"

__all__ = ['Test']

from ..Constant import *
from ..Capture import Capturer
from typing import Dict,List,Tuple
import json

class TreeTypeError(TypeError): pass
class FileRouteError(TypeError): pass
class AttrsTooMuch(Exception): pass

class Test():
    def __init__(self, t_tree: TREE_TYPE=None, json_file: str=None):
        if t_tree!=None and json_file==None:
            if isinstance(t_tree, Dict):
                self.tree = tree
            else: raise TreeTypeError('测试的树结构类型错误。')
        elif t_tree==None and json_file!=None:
            if isinstance(json_file, str):
                with open(json_file,'r',encoding='utf-8') as file:
                    self.tree = json.load(file) # 直接从文件中读。
            else: raise FileRouteError('json文件路径错误。')
        else: raise AttrsTooMuch('传递参数过多，只需传入其中一个。')

    def get_data(self, _id: str, initials: str=None, 
        standard_flag: str=STANDARD_FLAG):
        """获取当前节点下的DATA域。
        
        注意：本函数不处理异常，因此会抛出异常。注意处理异常。
        """
        return Capturer.get_current_node(self.tree,_id,
            initials=initials,standard_flag=standard_flag).get(DATA)

    def get_head(self, _id: ID, initials: str=None, standard_flag: str=STANDARD_FLAG) ->str:
        """获取当前节点下的标题。
        
        注意：本方法会抛出异常，请自行处理。
        """
        return Capturer.get_current_node(self.tree,_id,
            initials=initials,standard_flag=standard_flag).get(HEAD)

    def get_create_time(self) ->str:
        """获取json文件创建的时间。"""
        return self.tree.get(TIME)
    
    def get_file_name(self) ->str:
        """获取文件名"""
        return self.tree.get(TITLE)

    def get_node(self, _id: ID, initials: str=None, 
        standard_flag: str=STANDARD_FLAG) ->TREE_TYPE:
        """获取当前的节点
        
        注意：本函数会抛异常。
        """
        return Capturer.get_current_node(self.tree,_id,
            initials=initials,standard_flag=standard_flag)
    
    def get_brother_node_id(self, _id: ID, initials: str=None, 
        standard_flag: str=STANDARD_FLAG) ->List[ID]:
        """获取当前标题编号下的所有孩子节点的标题编号。
        
        注意：本函数会抛异常。
        """
        return [x for x in Capturer.get_current_node(self.tree,_id,
            initials=initials,standard_flag=standard_flag).keys()
            if x not in [TIME,TITLE,TEXT,HEAD,DATA,TABLE,PRIOR,TEMP]]

    def get_head_and_data(self, _id: ID, initials: str=None, 
        standard_flag: str=STANDARD_FLAG) ->Tuple[str,str]:
        """同时获取标题和内容。
        
        注意：本函数会抛出异常。
        """
        now_node = Capturer.get_current_node(self.tree,_id,
            initials=initials,standard_flag=standard_flag)
        return now_node.get(HEAD), now_node.get(DATA)

    def get_table(self, _id: ID, initials: str=None, standard_flag: str=STANDARD_FLAG):
        """获取当前节点下的表格。
        
        注意：本函数会抛异常。
        """
        return Capturer.get_current_node(self.tree,_id,
            initials=initials,standard_flag=standard_flag).get(TABLE)

    def get_temp(self, _id: ID, initials: str=None, standard_flag: str=STANDARD_FLAG):
        """获取当前节点下的TEMP域。
        
        注意：本方法会抛异常。
        """
        return Capturer.get_current_node(self.tree,_id,
            initials=initials,standard_flag=standard_flag).get(TEMP)