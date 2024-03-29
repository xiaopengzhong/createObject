import logging
import sys
import requests
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QLineEdit, QLabel, \
    QHBoxLayout, QCheckBox

from read_api_field import read_field

# 添加日志配置
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FieldCreationTool(QWidget):
    def __init__(self):
        super().__init__()
        self.form_id = None
        self.form1_code = None
        self.form2_code = None
        self.init_ui()

    def init_ui(self):
        # 创建输入框和标签
        self.field_name_label = QLabel('请输入对象名称1', self)
        self.field_name_input = QLineEdit(self)
        self.field_name_input.setFixedHeight(30)  # 设置高度为30

        # 添加输入框和标签用于输入appId
        self.app_id_label = QLabel('请输入App ID', self)
        self.app_id_input = QLineEdit(self)
        self.app_id_input.setText('51518')  # 设置默认值为51518
        self.app_id_input.setFixedHeight(30)

        # 创建勾选框
        self.show_object_checkbox = QCheckBox('显示第二个对象输入框', self)
        self.show_object_checkbox.stateChanged.connect(self.show_object_input)

        # 创建对象输入框和标签
        self.object_name_label = QLabel('请输入对象名称2', self)
        self.object_name_input = QLineEdit(self)
        self.object_name_input.setFixedHeight(30)

        # 创建水平布局来放置对象输入框和标签
        object_layout = QHBoxLayout()
        object_layout.addWidget(self.object_name_label)
        object_layout.addWidget(self.object_name_input)

        # 隐藏对象输入框
        self.object_name_label.setVisible(False)
        self.object_name_input.setVisible(False)

        # 将标签和输入框放在水平布局中
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.field_name_label)
        input_layout.addWidget(self.field_name_input)

        # 将标签和输入框放在水平布局中
        app_id_layout = QHBoxLayout()
        app_id_layout.addWidget(self.app_id_label)
        app_id_layout.addWidget(self.app_id_input)

        # 创建垂直布局
        layout = QVBoxLayout(self)
        layout.addLayout(input_layout)
        layout.addLayout(app_id_layout)
        layout.addWidget(self.show_object_checkbox)
        layout.addLayout(object_layout)  # 添加对象输入框的水平布局
        # layout.addWidget(self.object_name_label)  # 不再需要单独添加标签
        # layout.addWidget(self.object_name_input)  # 不再需要单独添加输入框

        # 创建按钮
        btn_create_form = QPushButton('创建对象', self)
        btn_create_form.clicked.connect(self.create_form)
        btn_create_form.setFixedHeight(30)
        layout.addWidget(btn_create_form)

        self.setLayout(layout)

        # 设置窗口
        self.setGeometry(500, 500, 500, 250)
        self.setWindowTitle('Field Creation Tool')
        self.show()

    def show_object_input(self, state):
        if state == Qt.Checked:
            self.object_name_label.setVisible(True)
            self.object_name_input.setVisible(True)
        else:
            self.object_name_label.setVisible(False)
            self.object_name_input.setVisible(False)

    def send_sms(self):
        # 发送短信验证码的接口
        sms_api_url = "http://developers.test2.youxin.plus/api-login/sms/preview-login"
        sms_payload = {
            "phone": "13631276041",
            "code": "123569",
            "companyId": 666
        }

        try:
            response = requests.post(url=sms_api_url, json=sms_payload)
            response.raise_for_status()
            data = response.json()
            self.sms_token = data.get('data', {}).get('token')
            if self.sms_token:
                return self.sms_token
            else:
                QMessageBox.critical(self, '错误', '验证码发送失败，请检查手机号！')
                return None
        except requests.exceptions.RequestException as err:
            QMessageBox.critical(self, '错误', f'验证码发送失败：{err}')
            return None

    def get_headers_with_token(self):
        # 登录获取 token
        preview_token = self.send_sms()
        if preview_token is None:
            return None
        if preview_token:
            login_url = "http://developers.test2.youxin.plus/api-login/login"
            login_payload = {
                "companyId": 666,
                "token": preview_token
            }

            try:
                login_response = requests.post(url=login_url, json=login_payload)
                login_response.raise_for_status()
                login_data = login_response.json()
                x_user_token = login_data.get('data').get('token')

                if not x_user_token:
                    QMessageBox.critical(self, '错误', '无法获取登录 token！')
                    return None

                headers = {
                    "Content-Type": "application/json;charset=UTF-8",
                    "Cookie": "_bl_uid=qdlFeiX0y1FdXe1wkg6I5sd6n8da",
                    "X-User-Token": x_user_token,  # 使用获取的登录 token
                    "X-Expend-Log-App-Id": self.app_id_input.text()
                }

                return headers

            except requests.exceptions.RequestException as err:
                QMessageBox.critical(self, '错误', f'登录失败：{err}')
                return None

    def create_form(self):
        # 检查第一个对象输入框是否有值
        if not self.field_name_input.text():
            QMessageBox.critical(self, '错误', '请输入对象1名称')
            return

        # 获取用户输入的 fieldName 参数
        field_name = self.field_name_input.text()
        headers = self.get_headers_with_token()
        if headers is None:
            return

        # 检查字段名和App ID是否为空
        if not self.app_id_input.text():
            QMessageBox.critical(self, '错误', '请输入App ID')
            return

        # 每次创建对象都重新获取默认表单编码
        default_form_code = self.get_default_form_code()
        if default_form_code is None:
            QMessageBox.critical(self, '错误', '无法获取默认表单编码')
            return

        # 在此处添加触发创建表单接口的代码
        api_url = "http://developers.test2.youxin.plus/api-meta/form/save"

        # 创建成功和失败的对象列表
        success_objects = []
        failed_objects = []

        # 创建第一个对象
        form1_params = {
            "type": "base",
            "name": field_name,
            "formCode": default_form_code,
            "desc": "",
            "titleField": {
                "fieldName": "名称",
                "fieldKey": "Name",
                "type": "text"
            },
            "appId": self.app_id_input.text()
        }

        try:
            # 创建第一个对象
            response1 = requests.post(url=api_url, json=form1_params, headers=headers)
            response1.raise_for_status()
            data1 = response1.json()
            self.form1_code = data1.get("data").get("formCode")
            self.form_id = data1.get("data").get("id")
            logger.info(f'创建的对象1名称：{self.form1_code}')  # 添加日志记录
            success_objects.append(field_name)
            # 在此处调用创建字段的接口，传递 form_code 参数


        except requests.exceptions.RequestException as err:
            QMessageBox.critical(self, '错误', f'表单1创建失败：{err}')
            failed_objects.append(field_name)

        # 如果对象输入框2有值，则创建第二个对象
        object_name = self.object_name_input.text()
        # 第二个对象框不隐藏且有值才创建
        if self.object_name_input.isVisible() and object_name:
            try:
                # 创建第二个对象时重新获取默认表单编码
                default_form_code = self.get_default_form_code()
                if default_form_code is None:
                    QMessageBox.critical(self, '错误', '无法获取默认表单编码')
                    return

                # 创建第二个对象
                form2_params = {
                    "type": "base",
                    "name": object_name,
                    "formCode": default_form_code,
                    "desc": "",
                    "titleField": {
                        "fieldName": "名称",
                        "fieldKey": "Name",
                        "type": "text"
                    },
                    "appId": self.app_id_input.text()
                }

                # 创建第二个对象
                response2 = requests.post(url=api_url, json=form2_params, headers=headers)
                response2.raise_for_status()
                data2 = response2.json()
                self.form2_code = data2.get("data").get("formCode")
                logger.info(f'创建的对象2名称：{self.form2_code}')  # 添加日志记录
                success_objects.append(object_name)

                # 在此处调用其他接口，传递 form_code 参数


            except requests.exceptions.RequestException as err:
                QMessageBox.critical(self, '错误', f'表单2创建失败：{err}')
                failed_objects.append(object_name)

        if success_objects:
            # QMessageBox.information(self, '成功', f'成功创建对象: {", ".join(success_objects)}')
            self.create_field(self.form1_code, self.field_name_input.text(), read_field()['form1'])  # 创建第1个对象的字段
            if self.object_name_input.isVisible() and object_name:
                pids = self.get_page_id(self.form1_code, ['add', 'detail'])
                self.create_field(self.form2_code, self.object_name_input.text(), read_field()['form2'], useFormId=self.form_id,
                                  addToRelateListParam={"addToPageIds": pids})  # 创建第2个对象的字段



    def get_default_form_code(self):
        # 获取默认表单编码的接口
        headers = self.get_headers_with_token()
        if headers is None:
            return
        api_url = "http://developers.test2.youxin.plus/api-meta/form-info/getDefaultCode"
        try:
            response = requests.get(url=api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            default_form_code = data.get('data')
            return default_form_code
        except requests.exceptions.RequestException as err:
            QMessageBox.critical(self, '错误', f'无法获取默认表单编码：{err}')
            return None

    def get_page_id(self, form_code, type=None):
        headers = self.get_headers_with_token()
        page_url = f"http://developers.test2.youxin.plus/api-meta/form/layout/{form_code}/list?page=1&num=100"
        if type:
            if isinstance(type, str):
                type = [type]
            page_url += f"&type={'&'.join(type)}"
        try:
            response = requests.get(url=page_url, headers=headers)
            response.raise_for_status()
            data = response.json().get('data')
            page_id = [page['pageId'] for page in data]
            return page_id
        except requests.exceptions.RequestException as err:
            QMessageBox.critical(self, '错误', f'无法获取pageId：{err}')
            return None

    def create_field(self, form_code,form_name, payloads, **kwargs):
        headers = self.get_headers_with_token()
        if headers is None:
            return
        success_fields = []
        failed_fields = []
        # 在此处添加触发创建字段接口的代码
        for payload in payloads:
            api_url = f"http://developers.test2.youxin.plus/api-meta/field-info/save/{form_code}"
            version = self.get_api_version(form_code)  # 获取版本号
            logger.info(f'获取的version: {version}')
            if payload['saveParam']['type'] in ['rich', 'qrCode']:
                pageIds = self.get_page_id(form_code, 'add,detail')  # 获取布局id
            else:
                pageIds = self.get_page_id(form_code)  # 获取布局id
            # 检查是否成功获取版本号
            if version is not None:
                # 更新字段的version和addToPageIds
                payload['saveParam'].update(version=version, addToPageIds=pageIds)
                # 判断只有查找和主项才更新addToRelateListParam属性
                if payload['saveParam']['type'] in ['associationForm', 'masterDetail']:
                    payload['saveParam'].update(kwargs)

                try:
                    field_name = payload['saveParam']['name']  # 字段名称
                    logger.info(f'{field_name}字段传参: {payload}')
                    response = requests.post(url=api_url, json=payload, headers=headers)
                    response.raise_for_status()
                    success_fields.append(payload['saveParam']["name"])
                    logger.info(f'创建字段按的结果: {response.json()}')
                except requests.exceptions.RequestException as err:
                    failed_fields.append((payload['saveParam']["name"], str(err)))
            else:
                QMessageBox.critical(self, '错误', '无法获取版本号！')

        success_message = f'{form_name} 对象 创建字段: {", ".join(success_fields)}' if success_fields else ''
        failed_message = f'创建失败字段: {", ".join([f"{name} ({error})" for name, error in failed_fields])}' if failed_fields else ''

        if success_message:
            QMessageBox.information(self, '成功', success_message)

        if failed_message:
            QMessageBox.critical(self, '错误', failed_message)

    def get_api_version(self, form_code):
        api_url = f"http://developers.test2.youxin.plus/api-meta/form/{form_code}"
        payload = {}
        headers = self.get_headers_with_token()

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            version = data.get('data', {}).get('version')
            return version

        except requests.exceptions.RequestException as err:
            QMessageBox.critical(self, '错误', f'无法获取版本号：{err}')
            return None
if __name__ == '__main__':
    app = QApplication(sys.argv)
    field_tool = FieldCreationTool()
    sys.exit(app.exec_())
