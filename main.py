import logging
import string
import sys
import requests
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QLineEdit, QLabel, \
    QCheckBox, QComboBox, QProgressDialog

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
        self.update_app_id()  # 初始化时获取令牌并保存

    def init_ui(self):
        # 创建一个垂直布局
        layout = QVBoxLayout(self)

        # 创建一个标签和下拉框，用于选择环境
        self.env_label = QLabel('选择环境', self)
        self.env_select = QComboBox(self)
        self.env_select.addItems(["测试环境", "生产环境"])
        self.env_select.currentIndexChanged.connect(self.update_app_id)

        # 创建一个标签和输入框，用于输入对象名称1
        self.field_name_label = QLabel('请输入对象名称1', self)
        self.field_name_input = QLineEdit(self)

        # 创建一个标签和输入框，用于输入App ID
        self.app_id_label = QLabel('请输入App ID', self)
        self.app_id_input = QLineEdit(self)
        self.app_id_input.setText('51518')

        # 创建一个复选框，用于控制第二个对象输入框是否显示
        self.show_object_checkbox = QCheckBox('显示第二个对象输入框', self)
        self.show_object_checkbox.stateChanged.connect(self.show_object_input)

        # 创建第二个对象名称标签和输入框
        self.object_name_label = QLabel('请输入对象1的子对象名称', self)
        self.object_name_input = QLineEdit(self)

        # 将所有控件添加到布局中
        layout.addWidget(self.env_label)
        layout.addWidget(self.env_select)
        layout.addWidget(self.field_name_label)
        layout.addWidget(self.field_name_input)
        layout.addWidget(self.app_id_label)
        layout.addWidget(self.app_id_input)
        layout.addWidget(self.show_object_checkbox)
        layout.addWidget(self.object_name_label)
        layout.addWidget(self.object_name_input)

        # 隐藏第二个对象名称标签和输入框
        self.object_name_label.setVisible(False)
        self.object_name_input.setVisible(False)

        # 创建一个按钮，用于创建对象
        btn_create_form = QPushButton('创建对象', self)
        btn_create_form.clicked.connect(self.create_form)
        layout.addWidget(btn_create_form)

        # 设置窗口布局
        self.setLayout(layout)

        # 设置窗口大小和标题
        self.setGeometry(500, 500, 500, 250)
        self.setWindowTitle('Field Creation Tool')

        # 显示窗口
        self.show()

    def update_app_id(self):
        env = self.env_select.currentText()
        if env == "测试环境":
            self.app_id_input.setText('51518')
        elif env == "生产环境":
            self.app_id_input.setText('51496')
        self.x_user_token = self.get_headers_with_token()  # 切换环境时重新获取令牌

    def get_base_url(self):
        env = self.env_select.currentText()
        if env == "测试环境":
            return "http://developers.test2.youxin.plus"
        elif env == "生产环境":
            return "http://developers.pre.youxin.plus"
        else:
            return "http://developers.test2.youxin.plus"

    def show_object_input(self, state):
        self.object_name_label.setVisible(state == Qt.Checked)
        self.object_name_input.setVisible(state == Qt.Checked)

    def send_sms(self):
        # 发送短信验证码的接口
        sms_api_url = f"{self.get_base_url()}/api-login/sms/preview-login"
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

    # 登录获取 token
    def get_headers_with_token(self):
        preview_token = self.send_sms()
        if preview_token is None:
            return None
        if preview_token:
            login_url = f"{self.get_base_url()}/api-login/login"
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

                return x_user_token

            except requests.exceptions.RequestException as err:
                QMessageBox.critical(self, '错误', f'登录失败：{err}')
                return None

    def get_headers(self):
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Cookie": "_bl_uid=qdlFeiX0y1FdXe1wkg6I5sd6n8da",
            "X-User-Token": self.x_user_token,  # 使用获取的登录 token
            "X-Expend-Log-App-Id": self.app_id_input.text()
        }
        return headers

    # 创建对象接口
    def create_form(self):
        # 创建进度对话框
        progress_dialog = QProgressDialog("创建对象中...", "取消", 0, 100, self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)

        def update_progress(value):
            progress_dialog.setValue(value)
            if value >= 100:
                progress_dialog.close()

        # 异步执行创建对象的过程
        QTimer.singleShot(100, lambda: self._create_form(update_progress))

    def _create_form(self, update_progress):
        # 检查第一个对象输入框是否有值
        if not self.field_name_input.text():
            QMessageBox.critical(self, '错误', '请输入对象1名称')
            return
        # 检查字段名和App ID是否为空
        if not self.app_id_input.text():
            QMessageBox.critical(self, '错误', '请输入App ID')
            return
        # 获取用户输入的 fieldName 参数
        field_name = self.field_name_input.text()
        form_params = [{
            "type": "base",
            "name": field_name,
            "formCode": "formCode1",
            "desc": "",
            "titleField": {
                "fieldName": "名称",
                "fieldKey": "Name",
                "type": "text"
            },
            "appId": self.app_id_input.text()
        }]
        object_name = self.object_name_input.text()
        form2_param = {
            "type": "base",
            "name": object_name,
            "formCode": "form_code2",
            "desc": "",
            "titleField": {
                "fieldName": "名称",
                "fieldKey": "Name",
                "type": "text"
            },
            "appId": self.app_id_input.text()
        }
        # 第二个对象框不隐藏且有值才创建
        if self.object_name_input.isVisible() and object_name:
            form_params.append(form2_param)
        api_url = f"{self.get_base_url()}/api-meta/form/save"
        # 创建成功和失败的对象列表
        result_message = []
        progress = 0
        for param in form_params:
            try:
                param['formCode'] = self.get_default_form_code()
                logger.info(f"创建对象的参数{param}")
                response2 = requests.post(url=api_url, json=param, headers=self.get_headers())
                response2.raise_for_status()
                data2 = response2.json()
                self.form_code = data2.get("data").get("formCode")
                logger.info(f'创建的对象名称：{self.form_code}')
                if form_params.index(param) == 0:
                    message = self.create_field(self.form_code, self.field_name_input.text(), read_field()['form1'])
                else:
                    message = self.create_field(self.form_code, self.object_name_input.text(), read_field()['form2'])
                result_message.append(message)
            except requests.exceptions.RequestException as err:
                QMessageBox.critical(self, '错误', f'对象创建失败：{err}')

            # 更新进度条
            progress += int(100 / len(form_params))
            update_progress(progress)

        messages = '\n'.join(result_message)
        update_progress(100)
        QMessageBox.information(self, '', messages)

    # 获取对象id的接口,用户创建对象时传参
    def get_default_form_code(self):
        api_url = f"{self.get_base_url()}/api-meta/form-info/getDefaultCode"
        try:
            response = requests.get(url=api_url, headers=self.get_headers())
            response.raise_for_status()
            data = response.json()
            default_form_code = data.get('data')
            return default_form_code
        except requests.exceptions.RequestException as err:
            QMessageBox.critical(self, '错误', f'无法获取默认表单编码：{err}')
            return None

    # 获取对象布局的接口，用于字段加到布局里和二维码字段
    def get_page_id(self, form_code, type=None):
        page_url = f"{self.get_base_url()}/api-meta/form/layout/{form_code}/list?page=1&num=100"
        if type:
            if isinstance(type, str):
                type = [type]
            page_url += f"&type={'&'.join(type)}"
        try:
            response = requests.get(url=page_url, headers=self.get_headers())
            response.raise_for_status()
            data = response.json().get('data')
            page_id = [page['pageId'] for page in data]
            return page_id
        except requests.exceptions.RequestException as err:
            QMessageBox.critical(self, '错误', f'无法获取pageId：{err}')
            return None

    # 创建对象字段的接口
    def create_field(self, form_code, form_name, payloads):
        success_fields = []
        failed_fields = []
        base_url = self.get_base_url()

        logger.info(f"开始创建字段 - 对象id: {form_code}, 对象名称: {form_name}")

        for payload in payloads:
            field_type = payload['saveParam'].get('type')
            # 跳过summary字段创建如果第二个对象框没有显示
            if field_type == 'summary' and not self.object_name_input.isVisible():
                logger.info("第二个对象框未显示，跳过创建summary字段")
                continue

            api_url = f"{base_url}/api-meta/field-info/save/{form_code}"
            version = self.get_api_version(form_code)
            logger.info(f"获取的字段版本号: {version}")

            if field_type in ['rich', 'qrCode']:
                pageIds = self.get_page_id(form_code, 'layout')
            else:
                pageIds = self.get_page_id(form_code)

            if version is not None:
                payload['saveParam'].update(version=version, addToPageIds=pageIds)

                if field_type in ['associationForm', 'masterDetail']:
                    addToRelateListParam = {"addToPageIds": self.get_page_id(form_code, 'layout')}
                    payload['saveParam'].update(useFormId=self.form_id, addToRelateListParam=addToRelateListParam)
                elif field_type == 'qrCode':
                    qrCodeConfig = {
                        "source": "system",
                        "nativeForm": True,
                        "formCode": form_code,
                        "pageType": "layout",
                        "pageCode": self.get_page_id(form_code, 'layout')[0],
                        "customData": "",
                        "queryFieldsFilter": [],
                        "redirectParams": [],
                        "validTime": 0,
                        "refreshPeriod": None
                    }
                    payload['saveParam'].update(qrCodeConfig=qrCodeConfig)
                elif self.object_name_input.isVisible() and self.object_name_input.text() and field_type == 'summary':
                    summaryInfo = {
                        "summaryFieldAccessPath": f"zhuxiang__c_{self.form2_code}",
                        "summaryFunction": "SUM",
                        "fieldName": "shuzhi__c"
                    }
                    payload['saveParam'].update(summaryInfo=summaryInfo)

                try:
                    field_name = payload['saveParam']['name']
                    logger.info(f"创建 {field_type} 字段请求参数: {payload}")
                    response = requests.post(url=api_url, json=payload, headers=self.get_headers())
                    response.raise_for_status()
                    success_fields.append(payload['saveParam']["name"])
                    logger.info(f"创建字段成功: {field_name}, 返回结果: {response.json()}")
                except requests.exceptions.RequestException as err:
                    failed_fields.append((payload['saveParam']["name"], str(err)))
                    logger.error(f"创建字段失败: {payload['saveParam']['name']}, 错误: {err}")
            else:
                logger.error("无法获取版本号！")
                QMessageBox.critical(self, '错误', '无法获取版本号！')

        success_message = f'{form_name} 对象 创建字段: {", ".join(success_fields)}。' if success_fields else ''
        failed_message = f'创建失败字段: {", ".join([f"{name} ({error})" for name, error in failed_fields])}' if failed_fields else ''

        if success_message:
            logger.info(f"成功消息: {success_message}")
            return success_message

        if failed_message:
            logger.error(f"失败消息: {failed_message}")
            return failed_message

    # 获取字段版本号的接口
    def get_api_version(self, form_code):
        api_url = f"{self.get_base_url()}/api-meta/form/{form_code}"
        payload = {}
        try:
            response = requests.post(api_url, json=payload, headers=self.get_headers())
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
