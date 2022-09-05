新建文件``upload_pgyer.py``，[代码见](https://github.com/SerBad/publish_pgyer/blob/master/upload_pgyer.py)

在Android项目中的``build.gradle``，新建一个task，可以替换成自己需要的文件目录

```gradle
task uploadpython(type: Exec) {
    commandLine 'python3', "${rootDir.absolutePath}/publish_pgyer/upload_pgyer.py", '--path', "$buildDir/outputs/apk", '--api_key', '你自己的key'
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