from ustjson.Capture import Capturer
from ustjson import TreeBuilder,SpecialText,read_txt
import datetime
import pprint

text = read_txt('test.txt')

try:
    catalog, text, _ = Capturer.capture_catalog_and_body_text(text) # 抓取全文信息，并分类清理。
    pdf = TreeBuilder(catalog=catalog) # 初始化文档树结构。
except:
    pdf = TreeBuilder() # 初始化空树
temp_ids = pdf.allocate_text_for_eachNode(text) # 分配各个节点的TEMP域。使解析更准确。temp_ids为分配过TEMP域的节点。
pdf.build_data_and_sub_tree_node(temp_ids) # 扩张子节点，完善DATA域。

failure_insert_id = pdf.build_table_auto_or_manual(appoint=['2.3.1'], table_data=[ # '2.3.1节点必须存在。'
    [
        ['$参赛信息表'], # 此处为表名，必须用$符号打头。
        ['姓名', '性别', 'team', '带队老师', '赛站', '时间'],
        ['吉杨', '男', '金石为开', '谢芳', 'Sophon', '2019-10-07'],
        ['覃兰珍','女','金石为开', '谢芳', 'Sophon', '2019-10-07']
    ]
]) # 填充表格。
if failure_insert_id != []: # 显示插入表格失败的节点信息。
    print(f'插入失败的标题编号有：{failure_insert_id}')

ST = SpecialText(pdf.tree) # 获取特殊文本对象进行完整性填充。
now = datetime.datetime.today() # 获取当前时间
file_name = 'test' # pdf的文件名
ST.perfect_tree(f'{now:%Y-%m-%d %H:%M:%S}', f'{file_name}.pdf') # 这里传入的参数，只用于修饰，不作其他用途。主要用来彰显时效性。
ST.to_json(path=os.getcwd(),file_name=f'{file_name}.json') # 保存为json文件，其他参数的使用参见官方的json文档。
