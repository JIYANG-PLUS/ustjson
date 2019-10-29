from ustjson.Capture import Capturer
from ustjson import TreeBuilder,SpecialText,read_txt,replace_id_feature
from ustjson.read_pdf import read_pdf
import re,datetime,os,pprint
os.chdir('/Users/jiyang/Desktop/')
file_name = 'test.pdf'
flag = '0123456789$'
now_id_split_char = '.'
patt = re.compile(r'^第(.{1,5}?)条')
text, tables = read_txt('test.txt'), None
text = replace_id_feature(text,patt,'0','$') # 第一个替换表，使用$区分其它标题编号。

try:
    catalog, text, _ = Capturer.capture_catalog_and_body_text(text) # 抓取全文信息，并分类清理。
    pdf = TreeBuilder(catalog=catalog) # 初始化文档树结构。
except:
    pdf = TreeBuilder() # 初始化空树

text_end = '$99999 END'
temp_ids = pdf.allocate_text_for_eachNode(
    text,
    standard_flag=flag+now_id_split_char,
    standard_flag_wosc=flag,
    id_split_char = now_id_split_char,
    initials = '$',
    text_end=text_end
) # 分配各个节点的TEMP域。使解析更准确。temp_ids为分配过TEMP域的节点。
pdf.build_data_and_sub_tree_node(
    temp_ids,
    standard_flag=flag+now_id_split_char,
    id_split_char = now_id_split_char
) # 扩张子节点，完善DATA域。
if bool(tables): pass # 处理表格的语句，参照前一个样式。
ST = SpecialText(pdf.tree) # 获取特殊文本对象进行再处理
now = datetime.datetime.today() # 获取当前时间
ST.perfect_tree(f'{now:%Y-%m-%d %H:%M:%S}', f'{file_name}') # 这里传入的参数，只用于修饰，不作其他用途。主要用来彰显时效性。
ST.to_json(path=os.getcwd(),file_name=f'{file_name[:-4]}.json') # 保存为json文件，其他参数的使用参见官方的json文档。
