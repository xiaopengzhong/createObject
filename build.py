import os
import subprocess


def package_pyqt5_project(project_path, project_name):
    # 构建打包命令
    command = f'pyinstaller --onefile --windowed --add-data "field.yml;." --add-data "read_api_field.py;." main.py'
    try:
        # 执行打包命令
        subprocess.run(command, shell=True, check=True, cwd=project_path)
        print("项目打包成功！")

        # 生成的可执行文件路径
        dist_path = os.path.join(project_path, 'dist', f'{project_name}.exe')
        print(f"可执行文件路径：{dist_path}")
    except subprocess.CalledProcessError as e:
        print("项目打包失败！")
        print(e)
if __name__ =='__main__':
    # 替换为您的项目路径和项目名称的绝对路径
    project_path = os.path.dirname(os.path.abspath(__file__))
    project_name = 'main'
    # 执行打包操作
    package_pyqt5_project(project_path, project_name)