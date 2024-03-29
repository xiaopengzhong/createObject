#@File   : .py
#@Time   : 2024/3/12 10:57
#@Author : 
#@Software: PyCharm
import os


import yaml


def read_field():
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接绝对路径
    api_field_path = os.path.join(current_dir, 'field.yml')
    with open(file=api_field_path, encoding='utf-8') as fp:
        content = fp.read()
        data = yaml.safe_load(content)
        return data.get('Field')
if __name__ == '__main__':
    print(read_field())