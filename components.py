import json
import os
import time

import pandas as pd


def get_current_day():
    current_day = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    return current_day


def get_current_time():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return current_time


class Logger:
    """
    filename:文件名，不带后缀，后缀固定.txt
    dst:输出目标。console-控制台、file-文件、all
    reverse:逆序写入，最新的在最上面。默认是顺序写入，最新的在最下面
    """

    def __init__(self, filename="log", dst="all", reverse=False):
        self.filename = filename
        self.dst = dst
        self.reverse = reverse
        pass

    def to_console(self, content):
        """输出到控制台"""
        print(content)
        pass

    def to_file(self, content):
        """输出到文件"""
        file_path = self.filename + ".txt"
        # 判断文件是否存在，若无则新建
        if not os.path.isfile(file_path):
            with open(file_path, mode='a', encoding='utf_8'): pass

        if self.reverse:
            # 逆序写入，最新的插入到最前，读出原有文件内容，移动索引到开始，写入新的数据，然后写入旧的数据
            with open(file_path, mode='r+', encoding='utf_8') as file_object:
                # 把字符串写入文件，写入多个字符串需要自行换行
                old = file_object.read()
                file_object.seek(0)
                file_object.write(content + "\n")
                file_object.write(old)
                file_object.flush()  # 提交更新。写入文件后，python在关闭文件时保存文件，如需在关闭前就保存，需要使用flush()
        elif not self.reverse:
            # 顺序写入，最新的插入到最后
            with open(file_path, mode='a+', encoding='utf_8') as file_object:
                file_object.write(content + "\n")
                file_object.flush()  # 提交更新。写入文件后，python在关闭文件时保存文件，如需在关闭前就保存，需要使用flush()

    def info(self, *content):
        content_str = ''
        for i in content:
            content_str = content_str + " " + str(i)
        content = get_current_time() + " " + content_str
        if self.dst == "console":
            self.to_console(content)
        elif self.dst == "file":
            self.to_file(content)
        elif self.dst == "all":
            self.to_console(content)
            self.to_file(content)


class Transformer:
    def __init__(self):
        pass

    def headers_str_to_dict(self, headers_str):
        """
        根据requests的定义，headers是字典，post_data是字符串（推荐json格式）
        此函数用于将burpsuite中复制的字符串格式的headers转换为dict
        注意：转换后的值是str格式的，某些数字值需要自行改成数字
        """
        headers_list = headers_str.strip().split("\n")
        headers_list = list(filter(None, headers_list))
        keys = []
        values = []
        for header_str in headers_list:
            header_list = header_str.split(":")
            keys.append(header_list[0].strip())
            values.append(header_list[1].strip())
        headers_dict = dict(zip(keys, values))
        print(headers_dict)
        return headers_dict

    def str_to_list(self, my_str):
        """把多行字符串按行分割转化为列表"""
        my_list = my_str.split('\n')  # 分行
        for index, element in enumerate(my_list, 0):  # 多虑前后的空格
            my_list[index] = element.strip()
        my_list = list(filter(None, my_list))  # 过滤空元素
        return my_list


class Checker:
    def check_dir(self, dir_path):
        """检查目录，若无则新建"""
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def check_file(self, file_path):
        """检查文件，若无则新建"""
        if not os.path.isfile(file_path):
            with open(file_path, mode='a', encoding='utf_8'): pass


class File_Operater:
    """操作文件"""

    def output_to_excel(self, my_list, filename, sheet_name="newsheet"):  # 传入 列表、保存文件名
        """
        传入的列表举例，多个字典组成列表，每个字典表示一行
        [
        {"姓名": ["张三"],"部门": ["综窗"],"政治面貌": ["党员"]},
        {"姓名": ["李四"],"部门": ["医保"],"政治面貌": ["群众"]}
        ]
        传入的文件名举例："mytable.xlsx"
        """
        print("正在保存到excel文件")
        df_output = pd.DataFrame({})  # df_output是用于最终输出的变量
        for my_dict in my_list:
            df_temp = pd.DataFrame(my_dict, index=[0])
            df_output = pd.concat([df_output, df_temp])
        df_output.index = range(1, len(df_output) + 1)  # 重建索引
        df_output.to_excel(filename, sheet_name)
        print("保存 " + str(df_output.shape[0]) + " 条数据到文件:" + filename + "成功")

    def input_from_excel(self, filename):
        df_input = pd.DataFrame(pd.read_excel(filename))
        return df_input

    def output_to_json(self, my_json, filename):
        with open(filename, mode='w', encoding='utf_8') as file_object:
            json.dump(my_json, file_object, ensure_ascii=False, indent=1, separators=(',', ':'))  # 把复杂字典players写入到file_object，不要混合写入列表和字典，读取时会报错

    def input_from_json(self, filename):
        with open(filename, mode='r', encoding='utf_8') as file_object:
            content = json.load(file_object)  # 从file_object读取内容
            return content


# 用于调试
if __name__ == '__main__':
    my_file_operator = File_Operater()
    # my_list = [
    #     {"姓名": ["张三"], "部门": ["综窗"], "政治面貌": ["党员"]},
    #     {"姓名": ["李四"], "部门": ["医保"], "政治面貌": ["群众"]}
    # ]
    # my_file_operator.output_to_json(my_list,'temp.json')
    content = my_file_operator.input_from_json('temp.json')
    print(content)
