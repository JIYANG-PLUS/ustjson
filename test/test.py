from ustjson.testjson import Test
import os,pprint

os.chdir('/Users/jiyang/Desktop')
json_data = Test(json_file='test.json')

pprint.pprint(json_data.get_head_and_data('1.6.1'))