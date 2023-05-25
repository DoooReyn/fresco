# 安装 Composer

```shell
# 下载composer安装脚本
php -r "copy('https://install.phpcomposer.com/installer', 'composer-setup.php');"
# 执行composer安装
php composer-setup.php
# 删除安装脚本
php -r "unlink('composer-setup.php');"
# 全局安装composer
mv composer.phar /usr/local/bin/composer
# 验证
composer --version
# 保持最新版本
composer selfupdate
```
