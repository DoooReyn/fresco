# Lua_API lua_atpanic

## 开篇
> 今天继续往下解析第 4 个 API ：lua_atpanic 。  

## 解析
### 释义
> panic 有崩溃的意思。望文生义，我们可以猜测 lua_atpanic 是处置 Lua 程序崩溃时的方法。且看官方参考文档对 [lua_atpanic](http://cloudwu.github.io/lua53doc/manual.html#lua_atpanic) 的解释：
>> Sets a new panic function and returns the old one (see §4.6).
	设置一个新的 panic 函数，并返回之前设置的那个。
  
> [§4.6 – Error Handling in C](http://cloudwu.github.io/lua53doc/manual.html#4.6)

>> 在内部实现中，Lua 使用了 C 的 longjmp 机制来处理错误。（如果你使用 C++ 编译，Lua 将换成异常；细节请在源代码中搜索 LUAI_THROW。） 当 Lua 碰到任何错误 （比如内存分配错误、类型错误、语法错误、还有运行时错误）它都会抛出一个错误出去； 也就是调用一次长跳转。在保护环境下，Lua 使用 setjmp 来设置一个恢复点；任何发生的错误都会跳转到最近的一个恢复点。

>> 如果错误发生在保护环境之外， Lua 会先调用 panic 函数 （参见 lua_atpanic） 然后调用 abort 来退出宿主程序。 你的 panic 函数只要不返回 （例如：长跳转到你在 Lua 外你自己设置的恢复点） 就可以不退出程序。panic 函数以错误消息处理器（参见 §2.3）的方式运行；错误消息在栈顶。 不同的是，它不保证栈空间。 做任何压栈操作前，panic 函数都必须先检查是否有足够的空间 （参见 §4.2）。

>> 大多数 API 函数都有可能抛出错误，例如在内存分配错误时就会抛出。每个函数的文档都会注明它是否可能抛出错误。

>> 在 C 函数内部，你可以通过调用 lua_error 来抛出错误。

### 实现

``` c
LUA_API lua_CFunction lua_atpanic (lua_State *L, lua_CFunction panicf) {
  lua_CFunction old;
  lua_lock(L);
  old = G(L)->panic;
  G(L)->panic = panicf;
  lua_unlock(L);
  return old;
}
```

其中，`lua_CFunction` 是个函数指针，定义在 `lua.h 105`:

``` c
/*
** Type for C functions registered with Lua
*/
typedef int (*lua_CFunction) (lua_State *L);
```

`G(L)` 是个宏定义，意在取得 `L` 的 `l_G` 域中的数据：

``` c
// lstate.h 186
#define G(L)	(L->l_G)
```

我们之前一直没有分析过 `lua_State` 的结构，原因是因为它太复杂了，一时半会讲不清楚，只好一层一层去剥开，去理解。现在我们找到它的定义：

``` c
/*
** 'per thread' state
*/
struct lua_State {
  CommonHeader;
  unsigned short nci;  /* number of items in 'ci' list */
  lu_byte status;
  StkId top;  /* first free slot in the stack */
  global_State *l_G;
  CallInfo *ci;  /* call info for current function */
  const Instruction *oldpc;  /* last pc traced */
  StkId stack_last;  /* last free slot in the stack */
  StkId stack;  /* stack base */
  UpVal *openupval;  /* list of open upvalues in this stack */
  GCObject *gclist;
  struct lua_State *twups;  /* list of threads with open upvalues */
  struct lua_longjmp *errorJmp;  /* current error recover point */
  CallInfo base_ci;  /* CallInfo for first level (C calling Lua) */
  volatile lua_Hook hook;
  ptrdiff_t errfunc;  /* current error handling function (stack index) */
  int stacksize;
  int basehookcount;
  int hookcount;
  unsigned short nny;  /* number of non-yieldable calls in stack */
  unsigned short nCcalls;  /* number of nested C calls */
  l_signalT hookmask;
  lu_byte allowhook;
};
```

看到 `l_G` 是 `global_State *` 类型，`global_State` 是个结构体：

``` c
/*
** 'global state', shared by all threads of this state
*/
typedef struct global_State {
  lua_Alloc frealloc;  /* function to reallocate memory */
  void *ud;         /* auxiliary data to 'frealloc' */
  l_mem totalbytes;  /* number of bytes currently allocated - GCdebt */
  l_mem GCdebt;  /* bytes allocated not yet compensated by the collector */
  lu_mem GCmemtrav;  /* memory traversed by the GC */
  lu_mem GCestimate;  /* an estimate of the non-garbage memory in use */
  stringtable strt;  /* hash table for strings */
  TValue l_registry;
  unsigned int seed;  /* randomized seed for hashes */
  lu_byte currentwhite;
  lu_byte gcstate;  /* state of garbage collector */
  lu_byte gckind;  /* kind of GC running */
  lu_byte gcrunning;  /* true if GC is running */
  GCObject *allgc;  /* list of all collectable objects */
  GCObject **sweepgc;  /* current position of sweep in list */
  GCObject *finobj;  /* list of collectable objects with finalizers */
  GCObject *gray;  /* list of gray objects */
  GCObject *grayagain;  /* list of objects to be traversed atomically */
  GCObject *weak;  /* list of tables with weak values */
  GCObject *ephemeron;  /* list of ephemeron tables (weak keys) */
  GCObject *allweak;  /* list of all-weak tables */
  GCObject *tobefnz;  /* list of userdata to be GC */
  GCObject *fixedgc;  /* list of objects not to be collected */
  struct lua_State *twups;  /* list of threads with open upvalues */
  unsigned int gcfinnum;  /* number of finalizers to call in each GC step */
  int gcpause;  /* size of pause between successive GCs */
  int gcstepmul;  /* GC 'granularity' */
  lua_CFunction panic;  /* to be called in unprotected errors */
  struct lua_State *mainthread;
  const lua_Number *version;  /* pointer to version number */
  TString *memerrmsg;  /* memory-error message */
  TString *tmname[TM_N];  /* array with tag-method names */
  struct Table *mt[LUA_NUMTAGS];  /* metatables for basic types */
  TString *strcache[STRCACHE_N][STRCACHE_M];  /* cache for strings in API */
} global_State;
```

可以看出，`panic` 是 `global_State` 的一个成员，它在发生未保护的错误时会被调用。
因此，`lua_atpanic` 的作用就是将 `global_State` 的成员 `panic` 替换成 `panicf`，最后返回 `panic` 给调用者。

我们搜索下源码，看看 `lua_atpanic` 是如何调用的：

``` c
// lauxlib.h 1011
static int panic (lua_State *L) {
  lua_writestringerror("PANIC: unprotected error in call to Lua API (%s)\n",
                        lua_tostring(L, -1));
  return 0;  /* return to Lua to abort */
}


LUALIB_API lua_State *luaL_newstate (void) {
  lua_State *L = lua_newstate(l_alloc, NULL);
  if (L) lua_atpanic(L, &panic);
  return L;
}
```

原来 `Lua` 默认定义了一个 `panic` 函数，并且在创建新的 `lua_State` 线程状态的时候都会将默认的 `panic` 注册到 `global_State` 下。

其实不太懂在注册新的 `panic` 函数时为什么要返回之前的 `panic` 函数，可能是为了暂时替换而后还需要恢复吧。现在说不清楚，因为没有可应用的场景或者想象不出那样的应用场景，且留待之后回答。

## 终了
- 过于复杂的结构可以先放过，不求甚解，但脑袋里一定得有点概念。