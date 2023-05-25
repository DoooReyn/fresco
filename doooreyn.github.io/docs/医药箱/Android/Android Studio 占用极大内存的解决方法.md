# Android Studio 占用极大内存的解决方法

## 原因

> -xmx 参数是 Java 虚拟机启动时的参数，用于限制最大堆内存。
> Android Studio 启动时设置了这个参数，并且默认值很小，没记错的话，只有 768mb。
> 一旦工程变大，IDE 运行时间稍长，内存就开始吃紧，频繁触发 GC，自然会卡。

## 解决方案

-   Help -> Change Memory Settings
-   Max Heap Size 改为 2048 或 4096
-   Save and Restart
