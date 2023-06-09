# LUA_API lua_arith (1)

## 开篇
> 本节的目标是 `lua_arith`。  
> 从字面意义上看，`arith` 是 `arithmetic` 的缩写，也就是算术的意思。可见它是与 Lua 的算数运算息息相关的，理解它有助于我们理解 Lua 的算术规则。  
> 废话不说，放马来吧！

## 解析
`lua_arith` 声明在 `lua.h` ：

``` c
// lua.h 211
LUA_API void  (lua_arith) (lua_State *L, int op);
```

`lua_State` 是 lua 的状态机内容，我们暂时不管，适当时机会逐渐展开说明。除此之外，`lua_arith` 接收一个整型数据 `op` 作为参数，`op` 是 `operator` 的缩写，意指**运算符**。因为运算符是整型，所以必然有各种运算符的定义，也不用费劲去找，它就在声明的上方：

``` c
#define LUA_OPADD	0	// + 加		/* ORDER TM, ORDER OP */	
#define LUA_OPSUB	1	// - 减
#define LUA_OPMUL	2	// * 乘
#define LUA_OPMOD	3	// % 取模
#define LUA_OPPOW	4	// ^ 幂次方
#define LUA_OPDIV	5	// / 除
#define LUA_OPIDIV	6	// // 向下取整除法
#define LUA_OPBAND	7	// 与
#define LUA_OPBOR	8	// 或
#define LUA_OPBXOR	9	// 异或
#define LUA_OPSHL	10	// 逻辑左移
#define LUA_OPSHR	11	// 逻辑右移
#define LUA_OPUNM	12	// 取负
#define LUA_OPBNOT	13	// 非
```

现在我们可以猜测一下 `lua_arith` 的实现了：想象中，一般根据运算符进行 `swicth`，然后在各个 `case` 中实现具体不同的运算吧。先这样定下来，然后来看它的实现：

``` c
// lua_api.c 302
LUA_API void lua_arith (lua_State *L, int op) {
  lua_lock(L);
  if (op != LUA_OPUNM && op != LUA_OPBNOT)	
    api_checknelems(L, 2);  /* all other operations expect two operands */
  else {  /* for unary operations, add fake 2nd operand */
    api_checknelems(L, 1);
    setobjs2s(L, L->top, L->top - 1);
    api_incr_top(L);
  }
  /* first operand at top - 2, second at top - 1; result go to top - 2 */
  luaO_arith(L, op, L->top - 2, L->top - 1, L->top - 2);
  L->top--;  /* remove second operand */
  lua_unlock(L);
}
```

第 1 行，`lua_lock(L);`，不知道什么用，看它的定义：

``` c
// llimits.h 213
/*
** macros that are executed whenever program enters the Lua core
** ('lua_lock') and leaves the core ('lua_unlock')
*/
#if !defined(lua_lock)
#define lua_lock(L)	((void) 0)
#define lua_unlock(L)	((void) 0)
#endif
```

注释的意思是，当Lua 程序进入核心 `core` 时需执行 `lua_lock`，离开核心 `core` 时需执行 `lua_unlock`。可是我们看到的是 `((void) 0)`，妈的，这不是相当于什么都没做吗？那有什么意义呢？
无奈，只好Google之，于是找到一篇 [Purpose of lua_lock and luc_unlock][1]，以下是节选和翻译：
> If you port Lua to another platform, you are "allowed" to overwrite lua_lock with your own definition; and this definition should essentially be a mutex, to disallow cross-thread operations on the same Lua objects. Essentially, when implemented, it should act similarly to Python's Global Interpreter Lock (GIL).

> 当需要将 `Lua` 移植到其他平台时，可以重写 `lua_lock`。必须注意的是，为了避免线程间对同一 `Lua` 对象的操作，`lua_lock` 的定义必须是**互斥**的，且其实现中其行为应该和 `Python` 的**全局解释器锁（GIL）**类似。

意思是，`lua_lock` 和 `lua_unlock` 主要用于线程间通信的情况，一般情况下我们不需要考虑，`Lua` 官方也对其做了保留，如果有需要涉及到多线程操作，则需开发者自行实现互斥行为。想了解更多，可以看看这篇 [Lua Threads Tutorial][2]。


我们接着看第 2 行，这边出现了一个分支条件，`if (op != LUA_OPUNM && op != LUA_OPBNOT)` 。注意到 `LUA_OPUNM` 和 `LUA_OPBNOT` 是单目运算符，且随后的注释也补充说明，其下的操作要求 2 个操作数，也就是双目运算；那么 `else` 分支显然是对于单目运算而言了，对于单目运算，有这样的说明：添加了第 2 个伪操作数。什么意思？我们留待后面说明。

我们移驾到第 3 行， `api_checknelems(L, 2);` ，找到它的定义：

``` c
// lapi.h 20
#define api_checknelems(L,n)	api_check(L, (n) < (L->top - L->ci->func), \
				  "not enough elements in the stack")
```
上一节，我们介绍过 `(L->top - L->ci->func)`，它的意义是获知当前栈内元素的个数，那么 `api_checknelems(L, n)` 的意图就很明白了，就是检查当前栈内元素是否足够，如果索引 n 大于栈内元素，那么就访问了栈内不存在的元素，那想当然就越界了。 
我们继续看下去，看看是不是这样。继续找到 `api_check`：

``` c
// llimits.h 97
/*
** assertion for checking API calls
*/
#if !defined(luai_apicheck)
#define luai_apicheck(l,e)	lua_assert(e)
#endif

#define api_check(l,e,msg)	luai_apicheck(l,(e) && msg)
```

注意到 `api_check` 被 `luai_apicheck` 绑定，而 `luai_apicheck` 又被 `lua_assert` 绑定。注释说，此方法是**用于检查 API 调用的断言**。
哇靠，真TM心累，找了这么久，发现结果是**断言**，而 `lua_assert` 的行为现在还没有显山露水，仍旧是迷迷糊糊的，只好再找下去了。
我们来找 `luai_apicheck`，看看有没有其他定义。结果还真有，好累，来看看吧：

``` c
// luaconf.h 683
/*
@@ LUA_USE_APICHECK turns on several consistency checks on the C API.
** Define it as a help when debugging C code.
*/
#if defined(LUA_USE_APICHECK)
#include <assert.h>
#define luai_apicheck(l,e)	assert(e)
#endif
```

意思是，如果开启了 `LUA_USE_APICHECK`，那么 `luai_apicheck` 使用的是标准的 `C 断言 assert`。
结合上文，如果 `LUA_USE_APICHECK` 未开启，那么 `luai_apicheck` 使用的是 `Lua 的断言 lua_asser`。
OK，搞定！现在我们可以放心地来找 `lua_assert` 了。结果发现，尼玛，居然又有两处定义！好吧，先看第一处：

``` c
// llimits.h 84
/* internal assertions for in-house debugging */
#if defined(lua_assert)
#define check_exp(c,e)		(lua_assert(c), (e))
/* to avoid problems with conditions too long */
#define lua_longassert(c)	((c) ? (void)0 : lua_assert(0))
#else
#define lua_assert(c)		((void)0)
#define check_exp(c,e)		(e)
#define lua_longassert(c)	((void)0)
#endif
```

我们跳过 `lua_assert` 已定义的情况*（因为它下面的内容对我们的理解来说并没有什么用）*，看未定义时的情况：
`#define lua_assert(c)		((void)0)`
哦，万岁，又是什么都不做。
看注释怎么解释的：这个是用于内部调试的内部断言。
嗯哼，什么意思？还用说，用诙谐一点的手法说，又当了一回甩手掌柜呀：
> 亲爱的客官呀，如果您有内部调试的需求，麻烦自己定义 `lua_assert` 的行为，否则本店是一概不做特殊处理啦。您有本事自己去扩展、去倒腾吧，哈哈哈！欢迎光临！谢谢慢走！


来看第二处，位于 `lualib.h 53` 行：

``` c
// lublib.h 53
#if !defined(lua_assert)
#define lua_assert(x)	((void)0)
#endif
```
`lualib.h` 定义了 `Lua` 的标准库。同样的，仍然是不作处理。意思明摆着：如果您之前没有定义断言行为，那么往后我也不做特殊处理哦。

那么，两处有什么不同呢？猜测：第一处用于需要对源码进行修改时进行内部调试的情况；而第二处则面向外部 C API用户，为什么？因为它只针对标准库！

看了这么多，终于知道 `api_checknelems(L, 2);` 是为了检查栈内元素是否有2个以上，如果没有就抛出断言；也就是说，如果栈内元素不满足操作数的要求，那就出错了。
同样的，对于单目运算 `api_checknelems(L, 1);` 亦然。

千辛万苦，跋山涉水，我们终于来到了第 5 行：`setobjs2s(L, L->top, L->top - 1);`。这回我们找到相关定义，一并推出：

``` c
// lobject.h 190
#define checkliveness(L,obj) \
	lua_longassert(!iscollectable(obj) || \
		(righttt(obj) && (L == NULL || !isdead(G(L),gcvalue(obj)))))

// lobject.h 259
#define setobj(L,obj1,obj2) \
	{ TValue *io1=(obj1); *io1 = *(obj2); \
	  (void)L; checkliveness(L,io1); }

// lobject.h 269
/* from stack to (same) stack */
#define setobjs2s	setobj
```

将宏定义替换之后，可以将 `setobjs2s(L, L->top, L->top - 1);` 展开为：

``` c
{
	TValue *io1=(L->top); 
	*io1 = *(L->top - 1);
	(void)L; 
	checkliveness(L,io1);// 垃圾回收相关，这里不展开说明，只要知道它用于检查 Lua 对象是否可用即可
}

```

紧接着执行 `api_incr_top(L)`：

``` c
#define api_incr_top(L)   {L->top++; api_check(L, L->top <= L->ci->top, \
				"stack overflow");}
```

先让栈顶索引自增，接着检查 `L->top <= L->ci->top`。  
关于这里栈顶索引为什么要自增？联系上下文，应该是要腾出一个空间给第二个伪操作数。

接下来我们看第 10 行，为什么要特别看这个注释，因为这里有一个重要的提示：

``` c
/* first operand at top - 2, second at top - 1; result go to top - 2 */
``` 
意思是：以上准备工作万何曾之后，现在的情况是，第一个操作数位于栈内 `top - 2` 处，第二个操作数位于 `top - 1` 处，然后我们会把运算结果会放在 `top - 2` 处。


*这节篇幅太长了，笔者也累了，先撂下一笔，下节我们继续。*


## 终了
- 学习要不厌其烦，但篇幅太长，不烦休息一会再战。
- 看源码真的可以懂不少东西，所以不要害怕，总会有收获等着你。


## 参考

** lua_lock **

- [Purpose of lua_lock and lua_unlock](http://stackoverflow.com/questions/3010974/purpose-of-lua-lock-and-lua-unlock)
- [Threads Tutorial](http://lua-users.org/wiki/ThreadsTutorial)

** lua_assert **

- [lua_assert macro definition](http://lua-users.org/lists/lua-l/2015-11/msg00142.html)



[1]: http://stackoverflow.com/questions/3010974/purpose-of-lua-lock-and-lua-unlock "Purpose of lua_lock and lua_unlock"
[2]: http://lua-users.org/wiki/ThreadsTutorial "Threads Tutorial"