# 如何用 Python 实现字符串插值

> 原文来自： [How to Implement String Interpolation in Python - DZone Web Dev](https://dzone.com/articles/how-to-implement-string-interpolation-in-python-br)，本文是在自行理解之后的翻译，粗浅之处，望请谅解。

字符串插值是将字符串中的占位符替换为局域变量的过程。许多编程语言都可以做到，比如 Scala：

```Scala
// Scale 2.10+
var name = "John";
println(s"My name is $name")
>>> My name is John
```

Perl:

```Perl
my $name = "John";
print "My name is $name";
>>> My name is John
```

CoffeeScript:

```CoffeeScript
name = "John"
console.log "My name is #{name}"
>>> My name is John
```

… 还有很多。

乍看之下，似乎不大可能使用 `Python` 实现字符串插值，但实际上，我们只需要两行代码就可以实现。

首先，让我们从基础开始说起。通常我们构建一个复杂的 `Python` 字符串时都会使用 `format` 函数：

```Python
print "Hi, I am {} and I am {} years old".format(name, age)
>>> Hi, I am John and I am 26 years old
```

可以看出，`format` 的实现比字符串连接看起来整洁许多：

```Python
print "Hi, I am " + name + " and I am " + str(age) + " years old"
Hi, I am John and I am 26 years old
```

但如果通过这种方式使用 `format` 函数，输出的内容就取决于参数的位置顺序：

```Python
print "Hi, I am {} and I am {} years old".format(age, name)
Hi, I am 26 and I am John years old
```

为了避免这种情况，我们可以构造键值对形式的参数序列传给 `format` 函数，如下：

```Python
print "Hi, I am {name} and I am {age} years old".format(name="John", age=26)
Hi, I am John and I am 26 years old
print "Hi, I am {name} and I am {age} years old".format(age=26, name="John")
Hi, I am John and I am 26 years old
```

这里，为实现字符串插值，我们不得不传入将所有变量传入 `format` 函数，但是这依然没有达到我们想要的效果，因为 `name` 和 `age` 并不是局域变量。那么，`format` 函数可以在某种程度上访问到局域变量吗？

答案是可以的，使用 `locals` 函数我们能够获得存储着所有局域变量对象的字典：

```Python
name = "John"
age = 26
locals()
>>> {
 ...
 'age': 26,
 'name': 'John',
 ...
}
```

现在，我们可以将这个字典传给 `format` 函数了。不幸的是，我们不能像这样调用 `s.format(locals())` :

```Python
print "Hi, I am {name} and I am {age} years old".format(locals())
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
<ipython-input-5-0fb983071eb8> in <module>()
----> 1 print "Hi, I am {name} and I am {age} years old".format(locals())
KeyError: 'name'
```

这是因为 `locals` 函数返回的是一个字典，而 `format` 函数期望的是键值对参数序列。
幸运的是，我们可以使用 `**` 操作符将字典转换为键值对参数序列。如下，假设我们有一个期望键值对序列作为参数的函数：

```Python
def foo(arg1=None, arg2=None):
    print "arg1 = " + str(arg1)
    print "arg2 = " + str(arg2)
```

那么，我们就可以将存储于字典中的参数进行解包传入了：

```Python
d = {
    'arg1': 1,
    'arg2': 42
}
foo(**d)
>>> arg1 = 1
arg2 = 42
```

现在，使用这项技巧，我们就可以完成字符串插值的初版了，它大概长成这样：

```Python
print "Hi, I am {name} and I am {age} years old".format(**locals())
Hi, I am John and I am 26 years old
```

以上代码确实可以达到我们的需求，但看起来既笨重又不雅观。因为在进行字符串插值的时候，我们每次都不得不写上长长的一串 `format(\*\*locals())` 。如果能够写一个函数来完成这个过程会好很多，像这样：

```Python
# Can we implement inter() function in Python?
print inter("Hi, I am {name} and I am {age} years old")
>>> Hi, I am John and I am 26 years old
```

你可能觉得这不科学，因为如果我们将完成字符串插值的代码移动到另一个函数中，那么它不就无法访问原本作用域中的局域变量了吗：

```Python
name = "John"
print inter("My name is {name}")
...
def inter(s):
  # How can we access "name" variable from here?
  return s.format(...)
```

然而，这是有可能的。`Python` 提供了 `sys.\_getframe` 方法，借用它的便利，我们可以方便地监测到用于保存当前局域变量的 `frame` 对象:

```Python
import sys
def foo():
     foo_var = 'foo'
     bar()
 def bar():
     # sys._getframe(0) would return frame for function "bar"
     # so we need to to access 1-st frame
     # to get local variables from "foo" function
     previous_frame = sys._getframe(1)
     previous_frame_locals = previous_frame.f_locals
     print previous_frame_locals['foo_var']
foo()
>>> foo
```

> **稍作解释：** > `f_locals` 是`frame` 的一个属性，它用于保存对应作用域的局域对象字典，因此可以通过 `f_locals[‘foo_var’]` 获取到函数 `foo` 的局域变量 `foo_var`。
> 关于`frame` 和 `f_locals`，可以参考[python inspect 模块解析 - 2.9. 栈帧(frame)](https://my.oschina.net/taisha/blog/55597) 或者 [Python 程序的执行原理 - PyFrameObject](http://python.jobbole.com/84599/) 部分。

现在的工作就只剩将获得的 `frame` 数据与函数 `format` 结合起来了。下面就给出实现 Python 字符串插值的两行代码，请尽情使用吧：

```Python
def inter(s):
    return s.format(**sys._getframe(1).f_locals)

## example
name = "John"
age = 26
print inter("Hi, I am {name} and I am {age} years old")
>>> Hi, I am John and I am 26 years old
```
