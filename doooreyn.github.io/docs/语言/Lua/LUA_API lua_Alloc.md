# LUA_API lua_Alloc

## 开篇
> 本节了解一下 `lua_Alloc` 这个 API。
> 由于它不是函数，而只是一个类型定义，因此不会分析得很详尽透彻。
> 此外，由于上节没有对 `LUA_API` 宏定义做出解释，本节会附带说明一下 。
> 虽然本节比较简短，但其中涉及到的知识比较复杂，消化起来需要一点时间，参考文献处给出了一些链接，可以帮助理解。


## 解析
首先还是找到定义处，出自 `lua.h`：

``` c
// lua.h 124
/*
** Type for memory-allocation functions
*/
typedef void * (*lua_Alloc) (void *ud, void *ptr, size_t osize, size_t nsize);
```

这里定义了一个函数指针类型`lua_Alloc`，它带 `4` 个参数，返回 `1` 个 `void *` 类型的值。在源码中搜索一下，找到一处用例: 

``` c
// luaxlib.h 462
static void *resizebox (lua_State *L, int idx, size_t newsize) {
  void *ud;
  // LUA_API lua_Alloc (lua_getallocf) (lua_State *L, void **ud);
  lua_Alloc allocf = lua_getallocf(L, &ud);	// 完成定义
  UBox *box = (UBox *)lua_touserdata(L, idx);
  void *temp = allocf(ud, box->box, box->bsize, newsize); // 这边才是函数原型调用
  ...
  return temp;
}
```

## 扩展 ：LUA_API 

在源码中，我们会经常看到某些函数开头都有一个 `LUA_API`，上一节没有解释，也是疏忽了。今天趁着没有忘记，来记录一下。
我们依然先找到它的定义：

``` c
// luaconf.h 232
/*
@@ LUA_API is a mark for all core API functions.
@@ LUALIB_API is a mark for all auxiliary library functions.
@@ LUAMOD_API is a mark for all standard library opening functions.
** CHANGE them if you need to define those functions in some special way.
** For instance, if you want to create one Windows DLL with the core and
** the libraries, you may want to use the following definition (define
** LUA_BUILD_AS_DLL to get it).
*/
#if defined(LUA_BUILD_AS_DLL)	/* { */

#if defined(LUA_CORE) || defined(LUA_LIB)	/* { */
#define LUA_API __declspec(dllexport)
#else						/* }{ */
#define LUA_API __declspec(dllimport)
#endif						/* } */

#else				/* }{ */

#define LUA_API		extern

#endif				/* } */


/* more often than not the libs go together with the core */
#define LUALIB_API	LUA_API
#define LUAMOD_API	LUALIB_API
```

通读注释，可以归纳出以下几点：  

- `LUA_API` 用于标志核心 `API` 函数；
- `LUALIB_API` 用于标志辅助库函数；
- `LUAMOD_API` 用于标志标准库函数；
- 当然，如果有特殊需求，可以自行修改定义。默认的，`LUA_API、 LUALIB_API、 LUAMOD_API` 是一样的。

我们继续查找 `LUA_BUILD_AS_DLL`，在 `src/Makefile` 中找到了它 *(`Makefile` 用于指导编译和链接时的行为)*：

``` Makefile
## Makefile 118
mingw:
	$(MAKE) "LUA_A=lua53.dll" "LUA_T=lua.exe" \
	"AR=$(CC) -shared -o" "RANLIB=strip --strip-unneeded" \
	"SYSCFLAGS=-DLUA_BUILD_AS_DLL" "SYSLIBS=" "SYSLDFLAGS=-s" lua.exe
	$(MAKE) "LUAC_T=luac.exe" luac.exe
```

说明一下，`mingw` 是将 GCC 编译器和 GNU Binutils 移植到 Win32 平台下的产物。这里是在构建 Windows 环境时作为参数传输进去，意思是要求 lua 在编译后导出 dll。这里没有 Windows 环境，也就不测试了，有兴趣的可以自己去倒腾一番。

由于笔者是MacOSX 环境，因此这里走的是 `#define LUA_API extern`，

## 终了
- 通读注释，很有帮助；
- 提高英文水平势在必行；
- 别吝惜提问，[StackOverflow](http://stackoverflow.com/) 会给你惊喜。

## 参考文献
** typedef **

- [typedef用法小结](http://blog.csdn.net/gungod/article/details/1400936)
- [typedef函数指针用法](http://blog.csdn.net/qll125596718/article/details/6891881)

** Makefile **

- [Makefile wikipedia](https://en.wikipedia.org/wiki/Makefile)
- [A Simple Makefile Tutorial](http://www.cs.colby.edu/maxwell/courses/tutorials/maketutor/)

** mingw **

- [mingw wikipedia](https://zh.wikipedia.org/wiki/MinGW)

** __declspec **

- [dllexport, dllimport](https://msdn.microsoft.com/en-us/library/3y1sfaz2.aspx)
- [__declspec(dllexport) & __declspec(dllimport)](http://www.cnblogs.com/xd502djj/archive/2010/09/21/1832493.html)

** extern **

- [Understanding “extern” keyword in C](http://www.geeksforgeeks.org/understanding-extern-keyword-in-c/)
- [How to correctly use the extern keyword in C](http://stackoverflow.com/questions/496448/how-to-correctly-use-the-extern-keyword-in-c)