# 查看文件 md5 sha1 sha256 值

## 原理

-   **md5**: `certuitl -hashfile filepath MD5`
-   **sha1**: `certutil -hashfile filepath SHA1`
-   **sha256**: `certuitl -hashfile filepath SHA256`

## 封装到批处理文件

```bat
certutil -hashfile %1 MD5
```

保存为 **md5.bat**，放到环境变量可以访问到的路径下，直接在命令行下敲命令即可：

```shell
md5 file_path
```

其他类似处理即可。
