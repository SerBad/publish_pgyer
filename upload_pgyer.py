import os
import time

import requests
import argparse

import json
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

# _api_key去下面这个网站去获取
# https://www.pgyer.com/account/api

token_url = "https://www.pgyer.com/apiv2/app/getCOSToken"
build_info_url = "https://www.pgyer.com/apiv2/app/buildInfo"

# 企业微信群机器人配置说明
# https://developer.work.weixin.qq.com/document/path/91770
wechat_webhook = ""


class UploadOptions:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="自动上传文件")
        self.parser.add_argument("--path", type=str, required=True, help="apk的绝对路径，或者apk的根目录")
        self.parser.add_argument("--api_key", type=str, required=True, help="_api_key")

    def parse(self):
        return self.parser.parse_args()


# 获取上传文件的token
def getCOSToken(_api_key: str):
    e = MultipartEncoder(
        fields={
            '_api_key': _api_key,
            'buildType': "android"}
    )
    result_response = requests.post(token_url, data=e, headers={'Content-Type': e.content_type})
    text = json.loads(result_response.text)
    print("获取token的方式-->", result_response.status_code, text)
    return text["data"]


# 检查上传文件之后的发布进度
def buildInfo(_api_key: str, build_key: str) -> bool:
    e = MultipartEncoder(
        fields={
            '_api_key': _api_key,
            'buildKey': build_key}
    )
    build_info_response = requests.post(build_info_url, data=e, headers={'Content-Type': e.content_type})

    data = json.loads(build_info_response.text)
    code = data["code"]
    if code == 1216:
        print("发布失败-->", build_info_response.text)
        return True
    elif code == 0:
        wechat(data['data'])
        print("发布成功-->", build_info_response.text)
        return True
    else:
        print("发布中-->", build_info_response.text)
        time.sleep(5)
        return buildInfo(_api_key, build_key)


def count_size(size: int) -> str:
    return str(float('%.2f' % (size / 1024 / 1024))) + "MB"


def wechat(data):
    e = {
        'msgtype': "text",
        'text': {
            "content": "更新了白鹭湾\n" +
                       "应用名称：" + data["buildName"] + "\n" +
                       "版本号：" + data["buildVersion"] + "\n" +
                       "应用大小：" + count_size(data["buildFileSize"]) + "\n" +
                       "应用二维码地址：" + data["buildQRCodeURL"] + "\n" +
                       "应用更新时间：" + data["buildUpdated"] + "\n"
        }}

    result_response = requests.post(wechat_webhook, data=json.dumps(e), headers={'Content-Type': "application/json"})
    text = json.loads(result_response.text)
    print("推送企业微信群消息-->", text)


# MultipartEncoderMonitor的进度反馈
def my_callback(monitor):
    print('\r', '上传进度：', monitor.bytes_read / monitor.len, end='', flush=True)


# 使用的是python3，需要pip3 install requests requests_toolbelt
if __name__ == '__main__':
    parser = UploadOptions()
    args = parser.parse()
    print(args)
    paths = []
    # 支持只上传一个apk文件
    # 或者传入多个apk的文件的根目录，会自动解析
    if os.path.isfile(args.path):
        paths.append(args.path)
    else:
        for root, ds, fs in os.walk(args.path):
            print(root, ds, fs)
            if len(fs) > 0:
                for f in fs:
                    file = os.path.join(root, f)
                    if os.path.isfile(file) and str(file).endswith('.apk'):
                        paths.append(file)

    for path in paths:
        print("开始上传", path)
        token_response = getCOSToken(args.api_key)
        # 参考文档
        # https://www.pgyer.com/doc/view/api#fastUploadApp
        e = MultipartEncoder(
            fields={
                'key': token_response["key"],
                'signature': token_response["params"]["signature"],
                'x-cos-security-token': token_response["params"]["x-cos-security-token"],
                'file': (os.path.basename(path), open(path, 'rb'), 'application/octet-stream')}
        )

        print(e)
        m = MultipartEncoderMonitor(e, my_callback)
        response = requests.post(token_response["endpoint"], data=m, headers={'Content-Type': m.content_type})
        # 如果不用带进度，可以用下面的这个方法
        # response = requests.post(token_response["endpoint"], data=e, headers={'Content-Type': e.content_type})

        response.encoding = "utf-8"
        print('\n', response.request.url, response.request.method)
        print(response.request.headers)
        if response.status_code == 204:
            print("上传成功-->")
        else:
            print("上传失败-->")

        buildInfo(args.api_key, token_response["key"])
        print('===================>')
