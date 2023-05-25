# 安装 Swoole

```shell
# 下载swoole源码
wget https://github.com/swoole/swoole-src/archive/refs/tags/v4.6.7.zip
# 解压
unzip v4.6.7.zip
# 编译
cd swoole-src-4.6.7
phpize && ./configure --enable-openssl --enable-http2 --enable-swoole-json --enable-swoole-curl && make && make install
# 启用swoole扩展
vi /etc/php.ini
# 添加swoole到php.ini
extension=swoole.so
# 验证
php -m | grep swoole
```
