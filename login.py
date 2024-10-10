#@File   : .py
#@Time   : 2024/3/29 14:36
#@Author : 
#@Software: PyCharm
import logging
import requests
from PyQt5.QtWidgets import QMessageBox
# 添加日志配置
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
class LoginManager:
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
                QMessageBox.critical(None, '错误', '验证码发送失败，请检查手机号！')
                return None
        except requests.exceptions.RequestException as err:
            QMessageBox.critical(None, '错误', f'验证码发送失败：{err}')
            return None

    def get_headers_with_token(self, appid):
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
                    QMessageBox.critical(None, '错误', '无法获取登录 token！')
                    return None

                headers = {
                    "Content-Type": "application/json;charset=UTF-8",
                    "Cookie": "_bl_uid=qdlFeiX0y1FdXe1wkg6I5sd6n8da",
                    "X-User-Token": x_user_token,  # 使用获取的登录 token
                    "X-Expend-Log-App-Id": appid
                }

                return headers

            except requests.exceptions.RequestException as err:
                QMessageBox.critical(None, '错误', f'登录失败：{err}')
                return None
if __name__ == '__mainn__':
    LM = LoginManager()
    print(LM.send_sms())
