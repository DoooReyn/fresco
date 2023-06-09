# LUA_API lua_absindex

> 本系列不会讲 Lua 的基础语法，由于Lua的轻便简洁，读者自行搜索了解，很快就可以入门。  
> 本节开始，将直接进入 Lua 的 C API 探索，探索顺序基本与 Lua 参考手册一致。
> 因为是第一次读 Lua 源码，若有错误，尚请指教和见谅。

## lua_absindex
### 解析
我们找到 `lua_absindex` 在源码中的定义：

``` c
// lapi.c 160
/*
** convert an acceptable stack index into an absolute index
*/
LUA_API int lua_absindex (lua_State *L, int idx) {
  return (idx > 0 || ispseudo(idx))
         ? idx
         : cast_int(L->top - L->ci->func) + idx;
}
```

解释下注释：将一个可接受的索引 idx 转换为绝对索引。  
注意到实现中有一个函数 `ispseudo(idx)`，可以知道它用来检验索引是否处于可接受的范围内。  
我们找到 `ispseudo(idx)` 的定义：

``` c
// lapi.c 46
#define ispseudo(i)		((i) <= LUA_REGISTRYINDEX)
```

我靠，原来是一个宏定义，它的作用是将索引值 `idx` 跟 `LUA_REGISTRYINDEX` 做比较。  
继续查找 `LUA_REGISTRYINDEX` 的定义：

``` c
// lua.h 42
/*
** Pseudo-indices
** (-LUAI_MAXSTACK is the minimum valid index; we keep some free empty
** space after that to help overflow detection)
*/
#define LUA_REGISTRYINDEX	(-LUAI_MAXSTACK - 1000)
```

简单解释下注释：`-LUAI_MAXSTACK` *(注意是负值)* 是栈最小的有效索引，同时 Lua 保留了一些空闲空间来检测溢出。  
我们接着来看 `LUAI_MAXSTACK` ：

``` c
// luaconf.h 705
/*
@@ LUAI_MAXSTACK limits the size of the Lua stack.
** CHANGE it if you need a different limit. This limit is arbitrary;
** its only purpose is to stop Lua from consuming unlimited stack
** space (and to reserve some numbers for pseudo-indices).
*/
#if LUAI_BITSINT >= 32
#define LUAI_MAXSTACK		1000000
#else
#define LUAI_MAXSTACK		15000
#endif
```

注释里头说：`LUAI_MAXSTACK` 限制了 Lua 堆栈的大小，而 `LUAI_MAXSTACK` 的大小则由整型数值的字节大小决定。  
好，假设我们是 64 位，那么 `ispssudo` 就可以重写为：

``` c
#define ispseudo(i)		((i) <= (-1000000 - 1000))
```

现在我们知道，`LUA_REGISTRYINDEX` 定义为 `堆栈最小的有效索引-1000`，我们暂且称之为**注册表索引**。  
回到 `lua_absindex` 上来，如果索引 `idx` 大于 0 或者小于**注册表索引**，那么其绝对索引就原样输出；反之，则使用 `cast_int(L->top - L->ci->func) + idx` 进行输出。  
找到 `cast_int` 的定义：

``` c
// llimits.h 111
#define cast(t, exp)	((t)(exp))
// llimits.h 116
#define cast_int(i)	cast(int, (i))
```

很简单，`cast_int` 就是将数据强制转换为整型。  
而 `L->top - L->ci->func` 计算的是**栈顶元素索引与当前调用函数在栈内的索引之间的差值**，根据这个差值，我们可以间接知道栈内元素的个数。我们看获得栈内元素个数的函数 `lua_gettop` 定义就知道了：

``` c
LUA_API int lua_gettop (lua_State *L) {
  return cast_int(L->top - (L->ci->func + 1));
}
```

现在，简短的几行代码都得到解释了，我们可以据此得出一个结论：当给定输入参数，也即索引时，`lua_absindex` 的输出预期： 

- 正数：原样输出
- 超出注册表索引：原样输出
- 在负数可接受索引范围内：栈内元素个数+1+索引

### 测试
- 测试用例
``` c
#include <lua.hpp>
#include <lualib.h>
#include <lauxlib.h>
void test_lua_api_absindex(int index)
{
    lua_State *L = luaL_newstate();
    // 压入 index 个元素
    for(int i=1; i<=index; i++)
    {
        lua_pushnumber(L, 1);
    }
    int positive = lua_absindex(L, 10);
    int pseudo   = lua_absindex(L, -1001000);
    int negative = lua_absindex(L, -100);
    printf("lab_absindex got result : \n postive = %d\npseudo = %d\nnegative = %d", positive, pseudo, negative);
}
int main(int argc, const char * argv[]) {
    test_lua_api_absindex(1000);
    return 0;
}
```

- 输出
``` c
lab_absindex got result : 
postive = 10
pseudo = -10001000
negative = 901 // 1000 + 1 - 100
Program ended with exit code: 0
```
结果符合我们的预期。