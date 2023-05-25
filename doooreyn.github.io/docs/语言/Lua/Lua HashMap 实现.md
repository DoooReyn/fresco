# Lua HashMap 实现

## 说点什么

上次介绍了一个较为严格的 Lua 数组的实现——[LuaArray](http://www.jianshu.com/p/d6beb48683d2)，这次奉上 [LuaHashMap](https://github.com/DoooReyn/LuaHashMap) 的实现。当然，机制和[LuaArray](http://www.jianshu.com/p/d6beb48683d2) 一样，我们就不介绍了。

## 基本要求

1. 除了`nil`，任何值都可以作为键；
2. 可通过键直接访问和修改值；
3. 对不存在的键进行赋值将创建新的键值对映射；
4. 可开启键值数据类型过滤，即类似严格类型映射： `HashMap(String, String)`，非匹配的键值映射将被过滤或做无效处理；
5. 提供基本的方法来操作键值对。

## 硬性约束

1. 不允许直接修改内置的方法，如有需要，请手动扩展 `__methods__` 列表；

## 实现

### 1. 构造

同 [LuaArray](http://www.jianshu.com/p/d6beb48683d2) ，首先我们需要创建一个 HashMap 的改造方法`Map()`，其中约定 `new_map` 为构造返回的 HashMap 实例， `__map__`用于存储键值对映射，`__methods__` 用于存储内置的键值对映射的操作方法：

```lua
function Map()
    local new_map = {}
    local __map__ = {}
    local __methods__ = {}
    -- do something to construct a map
    return new_map
end
```

### 2. 元表

元表需要提供了访问映射表和内置方法的途径，以及新增或修改一对映射的流程：

```lua
function Map()
    local new_map = {}
    local __map__ = {}
    local __methods__ = {}

    local mt = {
        __index = function(t, k)
            -- 可以获得根据键获得值
            if __map__[k] then
                return __map__[k]
            end
            -- 可以获得内置方法
            if __methods__[k] then
                return __methods__[k]
            end
        end,
        __newindex = function(t, k, v)
            -- 首先检查内置方法列表中是否存在对应键，
            -- 为了避免思维的理解误区，我们不建议在
            -- __map__中存储与__methods__的同名映射
            if __methods__[k] then
                print('[warning] can not override native method.')
                return
            end
            -- set 方法用于设置键值对映射，我们后面再说明
            __methods__:set(k, v)
        end
    }
    setmetatable(new_map, mt)

    return new_map
end
```

### 3. 类型过滤

键值对都有类型，为了保持 HashMap 中的键值对类型一致，需要对映射表开启类型检查和过滤。在构造的时候，可以传入键值的类型`ktype`、`vtype`，默认`ktype`、`vtype`都为`Mixed`(混合，也就是原生态的 lua table 了)，接下来只要对类型进行过滤即可：

```lua
-- 表长度
function table.len(tbl)
    local count = 0
    for k, v in pairs(tbl) do
        count = count + 1
    end
    return count
end

-- 打印表
function table.print(tbl)
    local format = string.format
    for k,v in pairs(tbl) do
        print(format('[%s] => ', k), v)
    end
end

-- 以键作为值来构造表
function table.keyAsValue(...)
    local arr = {...}
    local ret = {}
    for _,v in ipairs(arr) do
        ret[v] = v
    end
    return ret
end

-- 数据类型定义
DATA_TYPE = table.keyAsValue('boolean', 'number', 'string', 'function', 'table', 'thread', 'nil')

-- 检查HashMap 的键值类型
local function checkHashType(tp)
    if not (tp == 'Mixed' or DATA_TYPE[tp]) then
        tp = 'Mixed'
    end
    return tp
end

-- HashMap 构造
function Map(ktype, vtype)
    local new_map = {}
    local __map__ = {}
    local __methods__ = {}
    local __key_type__, __value_type__ = checkHashType(ktype), checkHashType(vtype)

    -- 映射表类型
    function __methods__:typeOf()
        return string.format('HashMap<%s, %s>',__key_type__,__value_type__)
    end
    -- 映射表长度
    function __methods__:len()
        return table.len(__map__)
    end
    -- 设置一个映射
    function __methods__:set(k, v)
        -- 需要检查映射表类型
        if (__key_type__ == 'Mixed' or type(k) == __key_type__)
        and (__value_type__ == 'Mixed' or type(v) == __value_type__) then
            __map__[k] = v
        end
    end
    -- 解除一个映射
    function __methods__:unset(k)
        __map__[k] = nil
    end
    -- 打印映射表
    function __methods__:print()
        table.print(__map__)
    end
    -- 过滤键类型
    function __methods__:filterKey(tp)
        print('filter key type:',tp)
        for k,v in pairs(__map__) do
            if not checkType(type(k), tp) then
                __map__[k] = nil
            end
        end
    end
    -- 过滤值类型
    function __methods__:filterValue(tp)
        print('filter value type:',tp)
        for k,v in pairs(__map__) do
            if not checkType(type(v), tp) then
                __map__[k] = nil
            end
        end
    end
    -- 设置键类型
    function __methods__:setKeyType(type)
        if not checkType(type, nil) then
            if __key_type__ == type then
                return
            end
            __key_type__ = type
            self:filterKey(type)
        end
    end
    -- 设置值类型
    function __methods__:setValueType(type)
        if not checkType(type, nil) then
            if __value_type__ == type then
                return
            end
            __value_type__ = type
            self:filterValue(type)
        end
    end
    -- 过滤值
    function __methods__:filter(val)
        for k,v in pairs(__map__) do
            if v == val then
                __map[k] = nil
            end
        end
    end

    -- 元表
    local mt = {
        __index = function(t, k)
            if __map__[k] then
                return __map__[k]
            end
            if __methods__[k] then
                return __methods__[k]
            end
        end,
        __newindex = function(t, k, v)
            -- 首先检查内置方法列表中是否存在对应键，
            -- 为了避免思维的理解误区，我们不建议在
            -- __map__中存储与__methods__的同名映射
            if __methods__[k] then
                print('[warning] can not override native method.')
                return
            end
            -- 设置映射时需要检查映射类型
            __methods__:set(k, v)
        end
    }
    setmetatable(new_map, mt)

    return new_map
end
```

以上。

PS:

1. [在线测试](http://www.shucunwang.com/RunCode/lua/#id/452b2ad7605a479ea5d78efc832621f8)
2. [完整代码](https://github.com/DoooReyn/LuaHashMap)
