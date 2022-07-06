新建文件``upload_pgyer.py``，代码如下

```python
import os

import requests
import argparse

import json
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

upload_url = 'https://upload.pgyer.com/apiv1/app/upload'


class UploadOptions:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="自动上传文件")
        self.parser.add_argument("--path", type=str, required=True, help="apk的绝对路径，或者apk的根目录")
        self.parser.add_argument("--uKey", type=str, required=True, help="uKey")
        self.parser.add_argument("--api_key", type=str, required=True, help="_api_key")

    def parse(self):
        return self.parser.parse_args()


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

        # uKey和_api_key去下面这个网站去获取
        # https://www.pgyer.com/doc/api#uploadApp
        e = MultipartEncoder(
            fields={'uKey': args.uKey,
                    '_api_key': args.api_key,
                    'file': (os.path.basename(path), open(path, 'rb'), 'application/octet-stream')}
        )


        def my_callback(monitor):
            print('\r', '上传进度：', monitor.bytes_read / monitor.len, end='', flush=True)


        print(e)
        m = MultipartEncoderMonitor(e, my_callback)
        response = requests.post(upload_url, data=m, headers={'Content-Type': m.content_type})

        # 如果不用带进度，可以用下面的这个方法
        # response = requests.post(upload_url, data={
        #     'uKey': args.uKey,
        #     '_api_key': args.api_key,
        # }, files={'file': open(path, 'rb')})

        response.encoding = "utf-8"
        print('\n', response.request.url, response.request.method)
        print(response.request.headers)

        print("返回的内容为-->", response.status_code, json.loads(response.text))
        print('===================>')
```

在Android项目中的``build.gradle``，新建一个task，可以替换成自己需要的文件目录

```gradle
task uploadpython(type: Exec) {
    commandLine 'python3', '../upload_pgyer.py', '--path', "$buildDir/outputs/apk", '--uKey', '你自己的key', '--api_key', '你自己的key'
}
```

需要注意的是，新版本的apk不在outputs下面了，是在``"$buildDir/intermediates/apk"``下面。
然后使用下面的命令就可以上传了。

```
./gradlew  uploadpython
```

项目地址，https://github.com/SerBad/publish_pgyer

# git子模块

可以使用git的submodule方法来把其他git的子模块添加到项目里面去
使用方法是

```commandline
git submodule add https://github.com/SerBad/publish_pgyer.git
```