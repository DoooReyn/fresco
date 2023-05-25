# 更简洁的 lua 逻辑代码

---

> 原文来自 [justbilt](http://blog.justbilt.com/2016/06/26/terse-lua-code/)

---

> 爱因斯坦的质能方程 `E=MC^2`, 用在编程界同样适用 `Error = More Code ^ 2`. 代码越多, 出错的可能性就更大, 这个结论很正确呀. 那么我们如何使用更少的代码实现同样的需求呢 ?

## 一. 普通技

### 1. bool 值与 if 语句的择决

让我们来看一段代码:

```lua
local monthly_is_taken = app.player:getAttribute("monthly_is_taken")
if monthly_is_taken == true then
    self._monthly_take:setButtonEnabled(false)
else
    self._monthly_take:setButtonEnabled(true)
end
```

显然这个 `if` 语句是没有必要的, 我们可以直接使用 `bool` 进行函数参数传递:

```lua
local monthly_is_taken = app.player:getAttribute("monthly_is_taken")
self._monthly_take:setButtonEnabled(monthly_is_taken)
```

我们可以看到减少了 %60 的代码, 逻辑反而变得更清晰了.

### 2. 减少非必须的中间变量

我们都明白了中间变量的意义, 主要是为提高代码的可读性. 但是有时候中间变量的太多, 在增加码量的同时, 也会打断我们的我们的思路.

比如我们要算一个等差数列的和, 我们都知道使用公式 `(首项+末项)*项数/2`, 我们看一下这个实现:

```lua
local array = {1,3,5,7,9}
local array_len = #array
local first_element = array[1]
local last_element = array[array_len]
local sum = (first_element+last_element)*array_len/2
```

就不如下面这个实现:

```lua
local array = {1,3,5,7,9}
local sum = (array[1]+array[#array])*#array/2
```

这样的话, 我们上一个示例的代码可以进一步精简:

```lua
self._monthly_take:setButtonEnabled(app.player:getAttribute("monthly_is_taken"))
```

### 3. 使用 elseif 优化 if 语句

如果是逻辑相悖的判断条件, 我们可以使用 `elseif` 语句连接, 而不用多个 `if` 语句.

```lua
if self.item_id == "43" then
    -- do some thing
end

if self.item_id == "69" then
    -- do some thing
end

if self.item_id == "75" then
    -- do some thing
end
```

我们可以修改为:

```lua
if self.item_id == "43" then
    -- do some thing
elseif self.item_id == "69" then
    -- do some thing
elseif self.item_id == "75" then
    -- do some thing
end
```

这样修改后, 对逻辑的执行时间也优化哟, 因为一但有一个 `if` 语句命中, 后面的 `elseif` 都不会再去判断了.

### 4. 使用 config 优化 if-elseif 语句

如果一个逻辑中有大量的 `if-elseif` 语句, 我么就可以使用 `config` 的形式替换掉它, 使得逻辑更加简洁.

让我们看一个示例:

```lua
if _data.type == GameEnum.MailType.MAIL_TYPE_SYSTEM then
    self._title:setString(_data.content.content.subtype)
    self._name:setString(TextEnum.CNReset.SYSTEM)
    self.title = TextEnum.CNReset.SYSTEM_INFORMATION
elseif _data.type == GameEnum.MailType.MAIL_TYPE_ALLIANCE_KICK then
    self._title:setString(TextEnum.CNReset.KICK)
    self._name:setString(TextEnum.CNReset.SYSTEM)
    self.title = TextEnum.CNReset.KICK
elseif _data.type == GameEnum.MailType.MAIL_TYPE_ALLIANCE_JOIN then
    self._title:setString(TextEnum.CNReset.JOIN_IN)
    self._name:setString(TextEnum.CNReset.SYSTEM)
    self.title = TextEnum.CNReset.JOIN_IN
elseif _data.type == GameEnum.MailType.MAIL_TYPE_ALLIANCE_REJECT then
    ...
```

这是一段关于邮件标题的逻辑, 这里只节选出了 1/4 的代码, 真的是又臭又长. 我们可以这样子去优化它:

```lua
local CONFIG = {
    [GameEnum.MailType.MAIL_TYPE_SYSTEM] = {title = XXX, name = XXX},
    [GameEnum.MailType.MAIL_TYPE_ALLIANCE_KICK] = {title = XXX, name = XXX},
    [GameEnum.MailType.MAIL_TYPE_ALLIANCE_JOIN] = {title = XXX, name = XXX},
    [GameEnum.MailType.MAIL_TYPE_ALLIANCE_REJECT] = {title = XXX, name = XXX},
    ...
}

local config = CONFIG[_data.type]
if config then
    self._title:setString(config.title)
    self._name:setString(config.name)
end
```

因为只是代码节选, 所以上面修改是一段伪代码, 但是看起来超级清爽的有木有! 对于一开始无法确定的数据如何配置呢? 我们可以配置一个 `function`, 用的时候取出来调用就可以啦.

## 二. 黑科技

### 1. 数据默认值的设定

当我们拿到一段数据后, 总是要先预处理数据, 后面才是使用数据. 预处理阶段很重要的一步就是某些数据的默认值.

```lua
function sum3(_num1, _num2, _num3)
    if not _num1 then
        _num1 = 0
    end
    if not _num2 then
        _num2 = 0
    end
    if not _num3 then
        _num3 = 0
    end
    return _num1 +　_num2 + _num3
end
```

很繁琐是不是, 这时候我们可以使用 `and` 和 `or` 来优化默认值的设置:

```lua
function sum3(_num1, _num2, _num3)
    _num1 = _num1 or 0
    _num2 = _num2 or 0
    _num3 = _num3 or 0
    return _num1 +　_num2 + _num3
end
```

当 `or` 的前面部分是 `nil` 或者 `false` 的情况下, 返回这个表达式的值后面部分. 下面我列举一下常用类型的默认值用法:

```lua
-- number
a = a or 0
-- string
a = a or ""
-- function
a = a or function()end
-- table
a = a or {}
-- boolean
a = a == nil and true
```

这里值得一提的是 `boolean` 类型, 如果希望默认值是 `false` 话, 就不需要默认值, 因为 `nil` 和 `false` 对于判断来说以意义一致. 而如果希望默认值是 `true` 的话, 并不是 `a = a or true`, 而是 `a == nil and true`, 大家可以细想一下其中的含义.

### 2. table 中元素的初始化

比如我们要统计一个列表中, 每个元素出现的次数:

```lua
local list = {1,2,2,3,1,3}
local counter = {}
for i,v in ipairs(list) do
    if not counter[v] then
        counter[v] = 0
    end
    counter[v] = counter[v] + 1
end
```

因为 `counter` 不可能提前初始化好, 所以总是要判断存不存在这个元素, 我们也可以利用上面提到的技巧做这个事情:

```lua
local list = {1,2,2,3,1,3}
local counter = {}
for i,v in ipairs(list) do
    counter[v] = (counter[v] or 0) + 1
end
```

是不是变得很简洁 ?
