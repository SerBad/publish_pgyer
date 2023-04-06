import argparse
import re
import subprocess
import os

class BuildOptions:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="自动打包文件")
        self.parser.add_argument("--path", type=str, required=True, help="apk的路径")
        self.parser.add_argument("--password", type=str, required=True, help="你自己的密码")
        self.parser.add_argument("--jks_path", type=str, required=True, help="你自己jks的地址")
        self.parser.add_argument("--alias", type=str, default="release", help="你自己alias")

    def parse(self):
        return self.parser.parse_args()


# 用来执行jar包的
def query_by_command(execute: str):
    print(execute)
    output = subprocess.Popen(execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = output.stdout.readlines()
    return res


def get_min_sdk_version(file: str) -> str:
    res = query_by_command("aapt2 dump badging {}".format(file))
    for line in res:
        m = re.match(r'sdkVersion:\'([^\']*)\'', line.decode('UTF-8'))
        if m is not None:
            print("get_min_sdk_version  ", m[1])
            return m[1]
    return "21"


def query_by_apksigner(input_path: str, output_path: str):
    # apksigner 是来自于sdk.dir
    execute = "apksigner sign --ks {} --ks-key-alias {} --min-sdk-version {} --out {} {}".format(jks_path,
                                                                                                 args.alias,
                                                                                                 get_min_sdk_version(
                                                                                                     input_path),
                                                                                                 output_path,
                                                                                                 input_path)
    print(execute)
    # 这个是为了自动输入密码
    echo = subprocess.Popen(['echo', password], stdout=subprocess.PIPE)
    output = subprocess.Popen(execute, shell=True, stdout=subprocess.PIPE, stdin=echo.stdout, stderr=subprocess.STDOUT)
    while output.poll() is None:
        print(output.stdout.readline())
    print("签名完成，开始校验==========》》》》》")
    execute = "apksigner verify {}".format(output_path)
    print(execute)
    output = subprocess.Popen(execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while output.poll() is None:
        print(output.stdout.readline().decode('UTF-8'))
    print("校验完成==========》》》》》")


if __name__ == '__main__':
    parser = BuildOptions()
    args = parser.parse()
    # 替换自己的jks地址
    jks_path = args.jks_path
    # 替换自己的密码
    password = args.password
    apk_path = args.path
    query_by_apksigner(apk_path, apk_path)
