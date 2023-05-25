# Mac 应用已损坏解决方案

## 问题说明

通常在非 Mac App Store 下载的软件都会提示“xxx 已损坏，打不开。您应将它移到废纸篓”或者“打不开 xxx，因为它来自身份不明的开发者”。

![Mac应用已损坏](https://image.iicheese.com/kxulb.jpg)

## 原因

Mac 电脑启用了安全机制，默认只信任 Mac App Store 下载的软件以及拥有开发者 ID 签名的软件，但是同时也阻止了没有开发者签名的 “老实软件”。

## 解决方案

1. 暂时关闭安全机制，让应用通过，完成后重新打开。该方法适用于绝大部分 `MacOS`。

```bash
# 关闭安全机制，需要管理员权限
> sudo spctl --master-disable
# 重新打开应用，成功打开后重新开启安全机制
> sudo spctl --master-enable
```

2. 通过清除文件的附加属性以绕过安全机制，其中 `/path/to/application`是应用的路径。该方法适用于 `MacOS 10.15`。

```bash
> sudo xattr -rd com.apple.quarantine /path/to/application
# 示例
> sudo xattr -rd com.apple.quarantine /Applications/Atom.app
```
