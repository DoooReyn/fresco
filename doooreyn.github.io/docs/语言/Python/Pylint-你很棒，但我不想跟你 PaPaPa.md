# Pylint : 你很棒，但我不想跟你 PaPaPa ...

> 这是一篇读后感，原文来自 **Itamar** 的 **[Why Pylint is both useful and unusable, and how you can actually use it](https://codewithoutrules.com/2016/10/19/pylint/)**。文章不长，简明扼要，大致是说了这么三点：

1. [Pylint](https://www.pylint.org/) 的好处，以及如何帮助提升开发效率

-   解释了大项目中基本不使用 [Pylint](https://www.pylint.org/) 的原因
-   如何调教 [Pylint](https://www.pylint.org/) 使其发挥应有的实效

> 本文在原文的基础上进行了一些个 ( xīu ) 性 ( chǐ ) 的展开和解读。因此，在各位司机加满汽油、暖上引擎 _(磨 🗡 霍霍、擦枪走 🔥)_.....之前，还是要谨小慎微地给您递上一个十分贴心到位的友情提醒："本文已开启洪荒模式，其间 **wulitaotao**，气流紊乱，不可小觑；无关人士请自觉避让，*(小清新尤其)*注意此乃分流车道；最后，前方即将到达高速入口，请各位务必集中精力，谨慎驾驶，一路平安！😋"。

---

## Step.1 掀起你的盖头来，让我看看你的脸 👰🏻

> 你是蛇群里的[美杜莎](https://www.python.org)，你是托起希望的[雅典娜](https://pypi.python.org)，你只用回眸看我的那束光，便将我原本百毒不侵的心脏，吹作烟、散为云，我将一生奉你为神祇，匍匐在你脚下，做你最虔诚的信徒，从此再无畏死亡和黑暗......

概括的讲，[Pylint](https://www.pylint.org/) 是一个作用于 **Python** 的实时代码分析的命令行工具，它有助于开发人员在编写代码的过程中，及时发现和修正代码中存在的问题，这其中包括了**检测标准代码风格、重构帮助、错误检测、完全定制、编辑器集成、IDE 集成、UML 视图、...... **。
作为送给 **Python** 程序员的礼物，[Pylint](https://www.pylint.org/) 就是一记看轻实重的化骨绵掌，直打得你心神荡漾，眼波流淌，骨头酥脆，一碰即碎。

## Step.2 打开我，解锁更多姿势 👄

> ......
> 千姿百态是我，风情万种是我；
> 正当花好月圆夜，罗裳朦胧时;
> 请你，
> 轻轻打开我。
> ......

_（题外：😣 实在编不下去了，请自觉脑补。）_

对于不同的平台 [Pylint](https://www.pylint.org/) 有不同的打开方式。对，你没看错，主流的方式就有以下`8`种。所以不用担心车型不同、车系有别\*（我们有各种式样、各种厚度、各种尺寸，包您可以找到最衬您雄风的一款）\*\*，请放开手脚尽情享用！

1. **Debian 和 Ubuntu **

```bash
sudo apt-get install pylint
```

2. **Fedora**

```bash
sudo yum install pylint
```

3. **Gentoo**

```bash
emerge pylint
```

4. **openSUSE**

```bash
sudo zypper install pylint  # python2.7
sudo zypper install python3-pylint  #  python 3.x
```

5. **Arch Linux**

```bash
pacman -S python2-pylint # if you live in the past
pacman -S python-pylint  # if you live in the future
```

6. **OS X**

```bash
pip install pylint
```

7. **Windows**

```bash
pip install pylint
```

屌丝[问题](http://docs.pylint.org/installation.html#note-for-windows-users)多。 8. **From Source, using Git**

```bash
git clone https://github.com/PyCQA/pylint
git clone https://github.com/PyCQA/astroid
```

## Step.3 你很棒，但我不想跟你 PaPaPa ...  🤥

> 摘自原文：Pylint is useful, but many projects don't use it. For example, I went and checked just now, and neither Twisted nor Django nor Flask nor Sphinx seem to use Pylint. Why wouldn't these large, sophisticated Python projects use a tool that would automatically catch bugs for them?

文中提到，[Pylint](https://www.pylint.org/) 是个有用的工具，但是在像 **Twisted, Django, Flask, Sphinx** 这样出了名的大工程中却看不到它的踪影，这是为什么呢？这里有两个原因：

> 摘自原文：One problem is that it's slow, but that's not the real problem; you can always just run it on the CI system with the other slow tests. The real problem is the amount of output.

表面看来是它的问题是运行效率低*（ 需要对大量文件进行分析 ）*；但主要问题来自于使用 [Pylint](https://www.pylint.org/) 会产生大量的输出，且大部分属于无用的垃圾信息*( 这个问题要归咎于 [Pylint](https://www.pylint.org/) 的默认输出方式 )*。举 🌰 来说：

> 摘自原文：I ran pylint on a checkout of Twisted and the resulting output was 28,000 lines of output (at which point pylint crashed, but I'll assume that's fixed in newer releases). Let me say that again: 28,000 errors or warnings.

使用 [Pylint](https://www.pylint.org/) 检查 **Twisted** 项目，结果产生了`28,000` 行输出*（运行到这里崩溃了，不然可不止这么点哦~）*，也就是说有`28,000` 行的错误或警告*（ -\_-!!! )*。

再举一个不算有用的警告的 🌰：

```bash
W:675, 0: Class has no __init__ method (no-init)
```

见微知著，我们可以预想*（ 不，应该是明确 ）* [Pylint](https://www.pylint.org/) 妹纸的输出真的是往**铤而走险、弹尽粮绝**的路子上走，大概这就是为什么这些大佬*（老司机）*们拒绝上 [Pylint](https://www.pylint.org/) 的原因吧。

## Step4. 此路不通？别啊，我是可以调教的！😘

**😤 知道了你们这群死狗的想法，心里其实很不爽的说：**“臭男人，嘴巴上说不要，身体却很诚实。说到底，还不是嫌弃我输出太强，身体受不了嘛。一个个都是老贱的骨头！”

**😊 但话呢还是要漂亮地说：**“别急着走呀，我是可以调教的嘛。只要把**指令**输入到 `.pylintrc` 配置文件中，你就能完全支配我的动作和行为，制作专属于你的定制版哦~。”

😜“啥？你不知道有哪些**指令**？唔，是我的错，忘了告诉你这件事了。这儿有一本[说明书](https://pylint.readthedocs.io/en/latest/)，不懂就翻翻看，不要自己瞎鼓捣哦，不然我会坏掉的。”

😏“哦，对了，这儿还有两份参考配置，你可以借鉴一下别人是怎么做的：[XX](https://github.com/ClusterHQ/flocker/blob/master/.pylintrc), [OO](https://github.com/datawire/quark/blob/master/.pylintrc)。好了，你先好好看着吧，今晚我等你，一定要来哦~。”

---

## 就算长时疲劳驾驶，也请不要错过高速出口
