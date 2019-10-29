# Use of this source code is governed by the MIT license.
__license__ = "MIT"

__all__ = ['show_table']

import tkinter
from tkinter import ttk
from typing import List,Any,NoReturn

def show_table(head: str, data: List[Any]) ->NoReturn:
    top = tkinter.Tk()
    top.title(head[1:])
    top.geometry("800x400+200+100") #设置窗口大小及位置

    table = ttk.Treeview(top) # 初始化控件
    table["columns"] = data[0]    # #定义列

    for column in data[0]: # 第一行是字段名。
        table.column(column, width=50)
        table.heading(column, text=column)

    for i, v in enumerate(data[1:]):
        table.insert("", i, text=str(i+1), values=v)

    table.pack()
    top.mainloop()