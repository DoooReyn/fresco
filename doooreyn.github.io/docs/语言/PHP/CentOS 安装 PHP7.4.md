## 在 CentOS 上安装 PHP7.4

## 一、添加 EPEL 和 REMI 存储库

```shell
yum install epel-release -y
yum install https://rpms.remirepo.net/enterprise/remi-release-7.rpm -y
```

## 二、启用 REMI

```shell
yum install yum-utils -y
yum yum-config-manager --enable remi-php74
```

## 三、安装 PHP7.4

```shell
## 安装
yum install php php-cli php-fpm php-mysqlnd php-zip php-devel php-gd php-mcrypt php-mbstring php-curl php-xml php-pear php-bcmath php-json php-redis
## 验证
php -v
## 查看启用的模块
php -m
```
