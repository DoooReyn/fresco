# Lua_API lua_call & lua_callk

## 开篇
> 今天来简单了解一下 Lua 的函数调用：lua_call。

## 解析

### 函数调用协议
> `void lua_call (lua_State *L, int nargs, int nresults);`
> 
> 要调用一个函数请遵循以下协议：首先，要调用的函数应该被压入栈；接着，把需要传递给这个函数的参数按正序压栈； 这是指第一个参数首先压栈。最后调用一下 `lua_call`；`nargs` 是你压入栈的参数个数。 当函数调用完毕后，所有的参数以及函数本身都会出栈。 而函数的返回值这时则被压栈。 返回值的个数将被调整为 `nresults` 个，除非 `nresults` 被设置成 `LUA_MULTRET`。 在这种情况下，所有的返回值都被压入堆栈中。 `Lua` 会保证返回值都放入栈空间中。 函数返回值将按正序压栈（第一个返回值首先压栈）， 因此在调用结束后，最后一个返回值将被放在栈顶。


### lua_call 的定义

``` c
/*
** 'load' and 'call' functions (load and run Lua code)
*/
LUA_API void  (lua_callk) (lua_State *L, int nargs, int nresults,
                           lua_KContext ctx, lua_KFunction k);

#define lua_call(L,n,r)		lua_callk(L, (n), (r), 0, NULL)
```

可以看出 `lua_call` 是一个宏定义，它的内部实现实际上是由 `lua_callk` 来完成的。


### lua_callk 

`lua_callk` 接收 `5` 个参数，其中：`L` 是线程状态，`narg` 是目标函数的参数个数，`nresult` 是目标函数返回值个数，`ctx` 是 `continuation-function` 上下文环境，`k` 是一个 `continuation-function`。我们先看 `lua_KContext` 和 `lua_KFunction` 类型的定义，再来说 `continuation-function`：

- **lua_KContext**

``` c
/* type for continuation-function contexts */
typedef LUA_KCONTEXT lua_KContext;

/*
@@ LUA_KCONTEXT is the type of the context ('ctx') for continuation
** functions.  It must be a numerical type; Lua will use 'intptr_t' if
** available, otherwise it will use 'ptrdiff_t' (the nearest thing to
** 'intptr_t' in C89)
*/
#define LUA_KCONTEXT	ptrdiff_t

#if !defined(LUA_USE_C89) && defined(__STDC_VERSION__) && \
    __STDC_VERSION__ >= 199901L
#include <stdint.h>
#if defined(INTPTR_MAX)  /* even in C99 this type is optional */
#undef LUA_KCONTEXT
#define LUA_KCONTEXT	intptr_t
#endif
#endif
``` 

`lua_KContext` 是 `LUA_KCONTEXT` 的别名，`Lua` 首选采用 `intptr_t` 作为 `LUA_KCONTEXT` 的正身，其次是 `ptrdiff_t`；两者的区别可以参考文末的 `intptr_t && ptrdiff_t` 部分。总之，`LUA_KCONTEXT` 必须是数值类型，记住这点即可。


- **lua_KFunction**

``` c
/*
** Type for continuation functions
*/
typedef int (*lua_KFunction) (lua_State *L, int status, lua_KContext ctx);
```

`lua_KFunction` 是一个函数指针类型，在 `Lua` 中它被用于定义一个 `continuation-function`。何谓 `continuation-function`？简单的理解，它类似于闭包，可以保存程序的执行环境，但在实现上却大相径庭；具体可以参考文末的 `continuations` 部分。


- **lua_callk**

现在来看 `lua_callk` 的内部实现：

``` c
LUA_API void lua_callk (lua_State *L, int nargs, int nresults,
                        lua_KContext ctx, lua_KFunction k) {
  StkId func;
  lua_lock(L);
  api_check(L, k == NULL || !isLua(L->ci),
    "cannot use continuations inside hooks");
  api_checknelems(L, nargs+1);
  api_check(L, L->status == LUA_OK, "cannot do calls on non-normal thread");
  checkresults(L, nargs, nresults);
  func = L->top - (nargs+1);
  if (k != NULL && L->nny == 0) {  /* need to prepare continuation? */
    L->ci->u.c.k = k;  /* save continuation */
    L->ci->u.c.ctx = ctx;  /* save context */
    luaD_call(L, func, nresults);  /* do the call */
  }
  else  /* no continuation or no yieldable */
    luaD_callnoyield(L, func, nresults);  /* just do the call */
  adjustresults(L, nresults);
  lua_unlock(L);
}
```

`api_check(L, k == NULL || !isLua(L->ci), "...");` 用于检查 `continuation-function` 是否可用。

`api_checknelems(L, nargs+1)` 检查栈中的元素是否足够，这里栈中元素数量参照是 `nargs+1`，`1` 指的是目标函数，也就是说，至少需要保证目标函数和目标参数已经被 `push`到栈中了，才能保证目标函数被正常地调用。

`api_check(L, L->status == LUA_OK, "...");` 用于检查线程状态是否正常，只有处于正常状态下的线程才可以调用目标函数。

`checkresults` 被用于检查当前栈空间是否足够容纳目标函数返回的参数个数：

``` c
#define checkresults(L,na,nr) \
     api_check(L, (nr) == LUA_MULTRET || (L->ci->top - L->top >= (nr) - (na)), \
	"results from function overflow current stack size")

/* option for multiple returns in 'lua_pcall' and 'lua_call' */
#define LUA_MULTRET	(-1)
```

`func = L->top - (nargs+1);` 操作试图从栈中取出目标函数。接下来，会检查线程 `L` 的 `nny` 域，`nny` 记录了调用栈上不能被挂起的次数，通过判断 `nny` 的值，就可以知道当前过程能否挂起：

``` c
LUA_API int lua_isyieldable (lua_State *L) {
  return (L->nny == 0);
}
```

对于可挂起的过程，会保存上下文环境和 `cotinuation-function`，然后使用 `luaD_call` 调用目标函数；对于不可挂起的过程，则使用 `luaD_callnoyield` 去调用目标函数。我们看两者实现的细节：

``` c
/*
** Call a function (C or Lua). The function to be called is at *func.
** The arguments are on the stack, right after the function.
** When returns, all the results are on the stack, starting at the original
** function position.
*/
void luaD_call (lua_State *L, StkId func, int nResults) {
  if (++L->nCcalls >= LUAI_MAXCCALLS)
    stackerror(L);
  if (!luaD_precall(L, func, nResults))  /* is a Lua function? */
    luaV_execute(L);  /* call it */
  L->nCcalls--;
}


/*
** Similar to 'luaD_call', but does not allow yields during the call
*/
void luaD_callnoyield (lua_State *L, StkId func, int nResults) {
  L->nny++;
  luaD_call(L, func, nResults);
  L->nny--;
}
```

可知，`luaD_callnoyield` 在 `luaD_call` 的基础上增加了对 `nny` 的操作，在调用目标函数之前，通过 `nny` 的自增保证在调用过程中不被挂起，而在调用完成之后需要 `nny` 的自减来恢复。

`luaD_call` 在调用目标函数之前需要先检查嵌套的C调用是否超过栈允许的瓶颈，否则会报出栈溢出错误。接着 `luaD_call` 会进行一次预调用 `luaD_precall`，`luaD_precall` 会创建新的可调用环境，并针对 目标函数的类型对相关信息进行填充。如果目标函数是 C 函数，则在 `luaD_precall` 就可以完成目标函数的调用；如果目标函数是 Lua 函数，那么 `luaD_precall` 只会进行相关信息的填充，而后返回，由 `luaV_execute` 来完成对目标函数的调用。*（`luaD_precall` 和 `luaV_execute` 的具体实现部分比较艰深，先搁置在案，以后再拨冗整理。）*

目标函数被调用之后，栈中的内容被重新整理，也就是把目标函数和目标参数从栈中推出，再把返回参数压入栈中。`adjustresults` 确保返回值被全部压栈。

``` c
#define adjustresults(L,nres) \
    { if ((nres) == LUA_MULTRET && L->ci->top < L->top) L->ci->top = L->top; }
```


### lua_call 总结

- `lua_call` 的内部实现基于 `lua_callk` 和 `lua_State` 的 `nny` 标记；
- `lua_call` 不需要 `cotinuation-function`，也就是说在调用目标函数的过程中，它不容许被挂起；
- 借助 `lua_State` 的 `nny` 标记，可以判断一个函数是否可以被挂起；
- 在调用目标函数之后，目标函数和其参数都会被出栈，而后会将目标函数的返回值全部入栈。


## 终了
- 遇到了很多新的概念，脑袋瓜子被冲刷得七荤八素，晕。
- 现在不懂没关系，以后茅塞顿开的可能性就水涨船高了，我时常这么安慰自己。

## 参考

- **intptr_t** && **ptrdiff_t**
	- [What is the use of intptr_t?](http://stackoverflow.com/questions/35071200/what-is-the-use-of-intptr-t)
	- [Confused about the use of ptrdiff_t in C++](http://stackoverflow.com/questions/14307844/confused-about-the-use-of-ptrdiff-t-in-c)
	- [variables of type size_t and ptrdiff_t](http://stackoverflow.com/questions/7956763/variables-of-type-size-t-and-ptrdiff-t)

- **continuations**
	- [Lua 5.2 如何实现 C 调用中的 Continuation](http://blog.codingnow.com/2012/06/continuation_in_lua_52.html)
	- [Understanding continuations](http://lambda-the-ultimate.org/node/86)