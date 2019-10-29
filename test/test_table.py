from ustjson.testjson import Test
from ustjson.Table import show
import os

os.chdir('/Users/jiyang/Desktop')
json = Test(json_file='test.json')
table = json.get_table('2.3.1')

if table:
    show(table[0][0], table[1:])
else:
    print('本节点下无表格。')