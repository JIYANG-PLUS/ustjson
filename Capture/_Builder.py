# Use of this source code is governed by the MIT license.
__license__ = "MIT"

__all__ = [
    'build_tree', # 用于从二元目录列表中，构建文本目录树。
    'insert_allText_to_eachNode', # 想每个节点添加对应的所属于本节点的数据域temp。
    'build_data_and_sub_tree', # 细化操作填充分散各个节点及其内容。
    'build_table', # 创建表数据节点。
]

from ..Constant import *
from ..CleanTools import Cleaner
from ..CleanTools._Judge import *
from ..CleanTools._Split import *
from ..CleanTools._Combine import *
from typing import List,Tuple,Dict,NoReturn,Callable,Any
from . import Capturer
from itertools import takewhile
import pprint

class TempGetError(IndexError): pass
class TableDataError(TypeError): pass
class AppointIdError(TypeError): pass
class FuncNotCallableError(Exception): pass

def build_tree(catalog: List[Tuple[ID,TITLE]], id_split_char: str=ID_SPLIT_CHAR) ->TREE_TYPE:
    """构建目录树
    
    catalog: 为二元数据目录列表。必须是从函数Capturer.convert_catalog_to_pair_format()清洗过来的数据。
    return: 字典类型的目录树。
    """
    text_tree = {} # 正文部分的子树。
    for _id, _title in catalog:
        route = Capturer.get_search_route(_id,id_split_char) # route[0]是性质，route[1]是路径。
        if route[0] == ROOT: # 根节点的情况。
            text_tree[route[1][0]] = {}
            text_tree[route[1][0]][HEAD] = _title
            continue
        # 沿路径搜索末端节点。
        t_tree = text_tree
        for r in route[1][:-1]: # 最后一个标题编号为需要创建的，所以只要取到前一个。
            if t_tree.get(r) == None: # 如果父路径不存在，尝试修补为完整路径，缺失的部分用NULL代替。
                t_tree[r] = {}
                t_tree[r][HEAD] = 'NULL' # 后期填充内容时，尝试修复缺失值。
            t_tree = t_tree[r]
        t_tree[route[1][-1]] = {} # 创建标题对应下的子节点。
        t_tree[route[1][-1]][PRIOR] = route[1][-2] # 双向指针，指向父节点，方便返回父节点。
        t_tree[route[1][-1]][HEAD] = _title # 当前节点的标题。
    return text_tree

def insert_allText_to_eachNode(tree: TREE_TYPE, text: List[str],
    id_split_char: str=ID_SPLIT_CHAR, other_flag: str=OTHER_FLAG, 
    insert_char: str=INSERT_CHAR, standard_flag: str=STANDARD_FLAG, 
    standard_flag_wosc: str=STANDARD_FLAG_WOSC, initials: str=None, text_end=TEXT_END) ->List[ID]:
    """本函数会对正文再次进行清洗，所以可以直接传入本程序抓取后的正文。本函数目的是为了最大化降低解析误差。"""
    # 先对正文进行再清洗
    clean_text = Cleaner.clean_text_again(text,id_split_char,other_flag,insert_char,standard_flag,standard_flag_wosc)
    clean_text.append(text_end) # 添加文本结束标志
    flag = False # False 表示还没有集中一个标题编号下的所有内容
    index, left = 0, (0,'NULL') # 默认第一行是标题编号，实际上，根据现实文本内容实现。
    temp_ids = []
    while index < len(clean_text):
        split_t_text = clean_text[index].split(INSERT_CHAR) # 拆分，经过清洗后不存在空行。
        _id = split_t_text[0]
        if judge_id(_id,other_flag,id_split_char,standard_flag,initials): # 如果符合标题特征，便等待下一个标题特征。
            # 对本路径的合法性作检测，并用文本内容修复对应编号下的标题。修复缺失值。
            if len(split_t_text) > 1: check_routes_complete_and_fill(tree,_id,split_t_text[1],id_split_char) # 用第二个元素充当标题
            else: check_routes_complete_and_fill(tree,_id,'NULL',id_split_char) # 一般是自动填补一个缺失标题，除非一个路径上全部是缺失的节点，这种情况下会共用一个标题。
            if flag==False:
                left = index,_id # 找到了起点
                flag = True # 表明已经找到了某个标题编号的起点
            else:
                if judge_id(_id,other_flag,id_split_char,standard_flag,initials): # 一个标题编号获取结束。
                    now_node = Capturer.get_current_node(tree,left[1],id_split_char,other_flag,standard_flag)
                    temp_ids.append(left[1]) # 存储处理过的id数据
                    now_node[TEMP] = clean_text[left[0]:index]
                    flag = False # 表示本次编号下的内容提取完成。
                    index -= 1 # 下次从本次开始
        index += 1 # 最后一个标题编号会出现问题，但已通过结束标志解决。
    return temp_ids

def build_data_and_sub_tree(tree: TREE_TYPE, temp_ids: List[ID], NPL_judge_func: Callable[[str],bool]=None,
    id_split_char: str=ID_SPLIT_CHAR, other_flag: str=OTHER_FLAG, 
    insert_char: str=INSERT_CHAR, standard_flag: str=STANDARD_FLAG, 
    line_end_char: str=LINE_END_CHAR, recognize_table: str= RECOGNIZE_TABLE) ->NoReturn:
    """填充每个节点的data域。并且自动生成相应的子节点。"""
    for _id in temp_ids:
        registry = _init_registry(recognize_table) # 初始化子节点注册表

        node_id = Capturer.get_current_node(tree,_id,id_split_char,other_flag,standard_flag) # 拿出当前节点
        if node_id.get(TEMP) == None:
            continue # 继续往后
            # raise TempGetError('Temp节点获取错误。')
        temp = node_id[TEMP][:] # 拿出临时数据，进行再整理。为了不影响原来的数据，传入副本。
        # 最后一行不是以句号等符号结尾的进行清洗。
        for i in range(len(temp))[::-1]:
            if temp[i][-1] not in line_end_char:
                temp.pop(-1) # 不符合结束标志的行，进行删除。效率至上。
            else: break
        
        if len(temp) == 0:
            continue # 如果清洗结束后，没有内容了，则继续下一个节点的处理。

        # 第一行因为是符合框架的大标题编号，所以单独处理。
        split_first_line = temp[0].split(insert_char) # 空格分割
        if len(split_first_line) > 2: # 表示除了标题编号和标题外还有其余内容。
            data = ''.join(split_first_line[2:])
        else: data = '' # 此处的data用于DATA域的填充。正文编号的DATA域以列表形式存储。

        feature_result = [] # 存储所有的判断信息。
        # 自动向下延伸判断是否有分区节点拆分行。
        connect_str = ''
        left_str = []
        for i, v in enumerate(temp[1:]): # 从第二行开始判断
            split_next_line = v.split(insert_char)
            connect_str += split_next_line[0]
            if len(split_next_line) > 1:
                left_str.append(''.join(split_next_line[1:]))
            if len(split_first_line)>1 and (node_id[HEAD]==split_first_line[1]+connect_str):
                break
        else:
            i = -1 # 表示分区节点标题没有分行。
            left_str = [] # 说明分区节点的标题没有分行。
        except_first_line_temp = left_str+temp[2+i:]

        # 接下来的每一行都要进行标题特征的检查
        for l_temp in except_first_line_temp:
            feature_result.append(_judge_and_return_subNode(
                l_temp,recognize_table,insert_char,line_end_char)) # 获取判断结果

        # 拿出最开始连续为False的元素，将其合并到正文编号下的Data域里面。
        last_false_index = len(list(takewhile(lambda x:x[0]==False, feature_result))) # 截取到开始连续的最后一个False
        data += ''.join(except_first_line_temp[:last_false_index]) # 合并为正文处理
        data = [data]

        # 剩下的将做延伸子节点用
        leftover_temp = except_first_line_temp[last_false_index:]
        feature_result = feature_result[last_false_index:]
        # pprint.pprint(feature_result)
        # 因为上一步已经将前面为False的值全部获取并排除了，所以理论上下面的功能是完全成立的。
        i, len_leftover_temp = 0, len(leftover_temp)
        while i < len_leftover_temp:
            # 获取连续为True的长度
            this_True_len = len(list(takewhile(lambda x:x[0]==True,feature_result[i:]))) # 从当前往后获取
            if this_True_len == 0: break # 如果没有子标题，那么直接退出。
            # 获取连续为False的长度
            this_False_len = len(list(takewhile(lambda x:x[0]==False,feature_result[i+this_True_len:])))

            flag_other_sample_id = None # 用于存放不是最后一个样式的样式的节点
            _head, _data = '', ''
            if this_True_len > 1: # 说明可能是子标题分行了或者是多个子标题比较密集，这时候可能需要合并，这里也是自然语言处理功能的插入点！但本版本并未实现。
                temp_feature_result = feature_result[i:i+this_True_len]
                for item in temp_feature_result:
                    if item[1]!=len(recognize_table)-1 and item!=temp_feature_result[-1]:
                        if _head!='' or _data!='': # 写入数据
                            insert_id = _update_registry_and_return_now_id(registry,len(recognize_table)-1,_id,id_split_char)
                            last_node = Capturer.get_last_node(tree,insert_id,id_split_char,other_flag,standard_flag)
                            last_node[insert_id] = {} # 新增节点
                            last_node[insert_id][HEAD] = _head
                            last_node[insert_id][DATA] = _data
                            last_node[insert_id][PRIOR] = id_split_char.join(insert_id.split(id_split_char)[:-1])
                            _head, _data = '', ''

                        # 不属于最后一个样式，且不是最后一个，那么单独出来成为一个节点
                        # 获取当前节点的标题编号
                        insert_id = _update_registry_and_return_now_id(registry,item[1],_id,id_split_char)
                        # 先获取当前节点的上一个节点，然后插入
                        last_node = Capturer.get_last_node(tree,insert_id,id_split_char,other_flag,standard_flag)
                        last_node[insert_id] = {} # 新增节点
                        last_node[insert_id][HEAD] = item[2] # 插入标题
                        last_node[insert_id][DATA] = item[3] # 插入数据域
                        last_node[insert_id][PRIOR] = id_split_char.join(insert_id.split(id_split_char)[:-1]) # 插入前指针域

                    elif item[1]!=len(recognize_table)-1 and item==temp_feature_result[-1]:
                        if _head!='' or _data!='': # 写入数据，将上面的内容写入最后一个样式并清空
                            insert_id = _update_registry_and_return_now_id(registry,len(recognize_table)-1,_id,id_split_char)
                            last_node = Capturer.get_last_node(tree,insert_id,id_split_char,other_flag,standard_flag)
                            last_node[insert_id] = {} # 新增节点
                            last_node[insert_id][HEAD] = _head
                            last_node[insert_id][DATA] = _data
                            last_node[insert_id][PRIOR] = id_split_char.join(insert_id.split(id_split_char)[:-1])
                            _head, _data = '', ''
                        # 不属于最后一个样式，且位于最后一个，那么可能会继续往后读False的内容。
                        insert_id = _update_registry_and_return_now_id(registry,item[1],_id,id_split_char)
                        _head += item[2]
                        _data += item[3]
                        flag_other_sample_id = insert_id # 存储到外部，方便定位。
                    else: # 其他情况就是符合最后一个标题的情况
                        # 不用写入数据，暂时存储。
                        _head += item[2]
                        _data += item[3]
                        if len(_data)>0 and (_data[-1] in line_end_char): # 检测是不是属于单独的子节点样式。
                            insert_id = _update_registry_and_return_now_id(registry,len(recognize_table)-1,_id,id_split_char)
                            last_node = Capturer.get_last_node(tree,insert_id,id_split_char,other_flag,standard_flag)
                            last_node[insert_id] = {} # 新增节点
                            last_node[insert_id][HEAD] = _head
                            last_node[insert_id][DATA] = _data
                            last_node[insert_id][PRIOR] = id_split_char.join(insert_id.split(id_split_char)[:-1])
                            _head, _data = '', ''
            else: # 否则就是只有一个True的情况
                item = feature_result[i] # 下面同样要区分是不是最后一个子标题样式。
                if item[1] == len(recognize_table)-1: # 符合最后一个样式
                    _head += item[2]
                    _data += item[3]
                else:
                    insert_id = _update_registry_and_return_now_id(registry,item[1],_id,id_split_char)
                    _head += item[2]
                    _data += item[3]
                    flag_other_sample_id = insert_id

            # 处理False的情况。
            temp_leftover_temp = leftover_temp[i+this_True_len: i+this_True_len+this_False_len] # 获取所有的False行。
            temp_data = ''.join(temp_leftover_temp)
            if flag_other_sample_id == None: # 说明符合最后一个标题样式
                insert_id = _update_registry_and_return_now_id(registry,len(recognize_table)-1,_id,id_split_char)
                last_node = Capturer.get_last_node(tree,insert_id,id_split_char,other_flag,standard_flag)
                last_node[insert_id] = {} # 新增节点
                last_node[insert_id][HEAD] = _head
                last_node[insert_id][PRIOR] = id_split_char.join(insert_id.split(id_split_char)[:-1])
                if len(_data)>0  and (_data[-1] in line_end_char): # 此处需要改进，用NLP辅助处理。
                    last_node[insert_id][DATA] = _data
                else:
                    last_node[insert_id][DATA] = _data + temp_data
                    temp_data = ''
            else:
                last_node = Capturer.get_last_node(tree,flag_other_sample_id,id_split_char,other_flag,standard_flag)
                last_node[flag_other_sample_id] = {} # 新增节点
                last_node[flag_other_sample_id][HEAD] = _head
                last_node[flag_other_sample_id][PRIOR] = id_split_char.join(flag_other_sample_id.split(id_split_char)[:-1])
                if len(_data)>0  and (_data[-1] in line_end_char):
                    last_node[flag_other_sample_id][DATA] = _data
                else:
                    last_node[flag_other_sample_id][DATA] = _data + temp_data
                    temp_data = ''
            # 主节点新增data域
            data.append(temp_data)
            i += this_True_len + this_False_len # 前进
        node_id[DATA] = [x for x in data if bool(x)]

def build_table(tree: TREE_TYPE, appoint: List[str]=None, table_data: List[Any]=None, temp_ids: List[ID]=None, 
        id_split_char: str=ID_SPLIT_CHAR, other_flag: str=OTHER_FLAG, 
        standard_flag: str=STANDARD_FLAG, recognize_table: str= RECOGNIZE_TABLE, 
        insert_char: str=INSERT_CHAR, line_end_char: str=LINE_END_CHAR) ->List[ID]:
    """构建表格。
    
    内建多个隐藏参数。
    appoint: List[str]：指定在哪几个标题编号下面。
    table_data: List[TABLE]：手动输入的表格数据。
    如果appoint的长度和table_data的长度不一致，将以最小长度截取，这将导致数据的丢失。
    return: 插入表格失败的节点编号。
    """
    if temp_ids == None:
        temp_ids = []
    if appoint!=None and table_data!=None: # 只有同时指定这两个参数的时候才合理。
        if not isinstance(appoint, List):
            raise AppointIdError('指定要插入表格的节点类型错误。需要是List[str]类型。')
        if not isinstance(table_data, List):
            raise TableDataError('表格数据类型不正确。需要是List[str]类型。')
        len_appoint = len(appoint)
        len_table_data = len(table_data)
        min_len = min(len_appoint, len_table_data)
        # 截取
        appoint, table_data = appoint[:min_len], table_data[:min_len]
        return _build_table_by_attrs(tree,appoint,table_data,id_split_char,other_flag,standard_flag)
    if appoint==None and table_data==None: # 允许同时为空，这时候程序将自动运行填充，这种方式错误率较高，也不是很准确。
        _auto_build_table(tree,temp_ids,id_split_char,
            recognize_table,insert_char,line_end_char,other_flag,standard_flag)
        return []
    else: raise FuncNotCallableError('build_table函数无法工作。请同时指定appoint和table_data参数。')

def _build_table_by_attrs(tree: TREE_TYPE, appoint: List[str], table_data: List[Any], 
    id_split_char: str=ID_SPLIT_CHAR, other_flag: str=OTHER_FLAG, 
    standard_flag: str=STANDARD_FLAG) ->List[ID]:
    """根据传入的数据进行填充。
    
    return: 插入失败的节点
    """
    failure_node_insert = []
    now_node, now_data = [], []
    for i, _id in enumerate(appoint):
        try: # 先进行节点存在性检查。
            now_node.append(Capturer.get_current_node(tree,_id,id_split_char,other_flag,standard_flag))
            now_data.append(table_data[i]) # 对应存储。
        except: failure_node_insert.append(_id) # 存储处理失败的id。
        else:
            for i, node in enumerate(now_node):
                node[TABLE] = now_data[i]
    return failure_node_insert

def _auto_build_table(tree: TREE_TYPE, temp_ids: List[ID], id_split_char: str=ID_SPLIT_CHAR, 
    recognize_table: str= RECOGNIZE_TABLE, 
    insert_char: str=INSERT_CHAR, line_end_char: str=LINE_END_CHAR,
    other_flag: str=OTHER_FLAG, standard_flag: str=STANDARD_FLAG) ->NoReturn:
    """自动填充表格内容。"""
    for i in temp_ids:
        now_node = Capturer.get_current_node(tree,i,id_split_char,other_flag,standard_flag)
        temp_data = now_node[TEMP] # 拿出temp域
        # 查找有没有表格数据
        for i,d in enumerate(temp_data):
            if d[-1]=='表' or (len(d)>1 and d[-2]=='表'): # 用特征值定位表格，这通常会有很大的误差。
                for j, v in enumerate(temp_data[i+1:]):
                    if _judge_and_return_subNode(v,recognize_table,insert_char,line_end_char,id_split_char)[0]:
                        break
                now_node[TABLE] = {}
                now_node[TABLE][HEAD] = temp_data[i] # 自动填充表格数据会多出一个标题
                now_node[TABLE][DATA] = temp_data[i+1:j]
                break

def _judge_and_return_subNode(test_str: str, recognize_table: str= RECOGNIZE_TABLE, 
    insert_char: str=INSERT_CHAR, line_end_char: str=LINE_END_CHAR, 
    id_split_char: str=ID_SPLIT_CHAR) ->Tuple[bool,int,str,str]:
    """用于判断是否具有子节点特征，并返回特征所在对照表中的下标。末尾是句子结尾特征的标点符号不算作子节点。
    
    test_str: 为初始数据，也是并未拆分过的数据。
    return: 是否具有特征、特征所在的对照表的下标、标题、内容
    """
    for i in recognize_table[:-1]: # 最后一个子节点特征单独考虑
        # 需要根据每个标题特征作针对性清洗操作。
        clean_str = split_contents_flag_after(test_str,'',insert_char,i,i)
        clean_str = split_contents_flag_before(clean_str,'',insert_char,i,i) # 分离
        clean_str = combine_split_ids(clean_str,insert_char,'',i) # 合并
        first_clean_char = clean_str.split(insert_char)[0] # 分解获取第一个值
        if judge_id(first_clean_char,'','',i) and first_clean_char[-1]==i[-1]: # 最后一个字符判断以区分不同的标题编号类型
            return True, recognize_table.index(i), first_clean_char, ''.join(clean_str.split(insert_char)[1:])

    # 最后一个特征值单独拿出来考虑，本特征必须放在最后考虑，注意！！！是必须！！！不可商量！！！
    first_clean_char = test_str.split(insert_char)[0]
    len_limit = int(recognize_table[-1][1:]) # 拿出标准阈值
    if 0<len(first_clean_char)<len_limit and (first_clean_char[-1] not in line_end_char):
        return True, len(recognize_table)-1, first_clean_char, ''.join(test_str.split(insert_char)[1:])

    return False, -1, '', '' # 全部不匹配的情况

def _init_registry(recognize_table: str= RECOGNIZE_TABLE) ->REGISTRY:
    """初始化子节点注册表"""
    registry = {}
    common_attr = {
        'isalive': 0, # 默认子节点处于未激活状态
        'grade': 0, # 用于区分有多个子节点特征时的主次关系
        'id': '' # 下一次检测到子节点特征时的替代标题编号
    } # 子节点注册表的共有特征
    # 以子节点特征对照表的顺序为顺序，方便后面的使用。
    for i,v in enumerate(recognize_table):
        registry.setdefault(i,{}).update(common_attr) # 注册表的键和对照表的下标是一一对应的关系，以此来辨识区分。
    return registry

def _update_registry_and_return_now_id(registry: REGISTRY, sample_index: int, _id: ID, 
    id_split_char: str=ID_SPLIT_CHAR) ->ID:
    """更新子节点注册表。默认以1、2、3......进行子标题的扩充。
    
    registry: 已经初始化过的注册表。
    sample_index: 在样式表下的样式下标。
    _id: 父节点标题。
    id_split_char: 标题编号间的连字符。
    return: 当前子节点的自定义标题。
    """
    if  registry[sample_index]['isalive'] == 0:
        # 如果此样式没有在确认表中出现过，那么将继承其最邻近的上一个节点的特征，即grade最大的那个
        now_max_grade, now_max_grade_id = _search_regestry_largest_grade_id(registry)
        registry[sample_index]['isalive'] = 1 # 激活
        registry[sample_index]['grade'] = now_max_grade+1 # 等级+1
        if now_max_grade_id == '':
            registry[sample_index]['id'] = id_split_char.join([_id,'2'])
            return id_split_char.join([_id,'1'])
        else:
            # 根据子节点注册表的执行原理，这里的路径应该先后退一步
            ttt = now_max_grade_id.split(id_split_char)
            true_tail_id_v = str(int(ttt[-1])-1) # 理论值减一
            now_max_grade_id = id_split_char.join(ttt[:-1]+[true_tail_id_v]) # 回到上一级
            registry[sample_index]['id'] = id_split_char.join([now_max_grade_id,'2'])
            return id_split_char.join([now_max_grade_id,'1'])
    else:
        # 先将大于本样式等级的所有样式删除清空。
        _grade, _id = registry[sample_index]['grade'], registry[sample_index]['id']
        _delete_greater_than_now_grade(registry,_grade)
        split_id = _id.split(id_split_char)
        left, right = id_split_char.join(split_id[:-1]), str(int(split_id[-1])+1)
        # 更新新的子标题编号
        registry[sample_index]['id'] = id_split_char.join([left,right])
        return _id

def _search_regestry_largest_grade_id(registry: REGISTRY) ->Tuple[int, ID]:
    """获取当前注册表下级数最大的信息。
    
    return: 当前最大级数，最大级数下对应的当前id。
    """
    max_grade, max_grade_id = 0, '' # 0表示当前没有子标题注册过
    for registry_sample in registry.values():
        if registry_sample['isalive'] == 1:
            now_grade, now_id = registry_sample['grade'], registry_sample['id']
            if now_grade > max_grade:
                max_grade = now_grade
                max_grade_id = now_id
    return max_grade, max_grade_id

def _delete_greater_than_now_grade(registry: REGISTRY, now_sample_grade: int) ->NoReturn:
    """删除所有大于now_sample_grade的节点信息。"""
    for k, v in registry.items():
        if v['grade'] > now_sample_grade:
            registry[k]['isalive'] = 0
            registry[k]['grade'] = 0
            registry[k]['id'] = ''
