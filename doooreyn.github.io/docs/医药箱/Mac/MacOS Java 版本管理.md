# MacOS Java 版本管理

1. `/usr/libexec/java_home -V` 可以查看当前可用的 Java 版本列表。

    ```bash
    > /usr/libexec/java_home -V
    Matching Java Virtual Machines (3):
    1.8.0_162, x86_64: "Java SE 8" /Library/Java/JavaVirtualMachines/jdk1.8.0_162.jdk/Contents/Home
    1.6.0_65-b14-468, x86_64: "Java SE 6" /Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Home
    1.6.0_65-b14-468, i386: "Java SE 6" /Library/Java/JavaVirtualMachines/1.6.0.jdk/Contents/Home
    /Library/Java/JavaVirtualMachines/jdk1.8.0_162.jdk/Contents/Home
    ```

2. 在 Shell 配置中添加如下配置并保存:

    ```bash
    function setjdk() {
        export JAVA_HOME=`/usr/libexec/java_home -v $@`
    }
    ```

    接着使用 `source .zshrc` 刷新后调用 `setjdk 1.6` 即可切换 Java 版本。
