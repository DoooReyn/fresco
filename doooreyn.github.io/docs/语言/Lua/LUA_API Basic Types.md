# Lua_API Basic Types

## 开篇
> 介绍了基本运算之后，我们发现还没有正式地去介绍 Lua 的基本类型。今天我们趁机歇息一下，不往下讲新的 API，把基本类型认识一遍，就算达成今天的目标了。

## 解析

### 基本类型定义
为了便于理解，我们先行阅读官方的[参考手册](http://www.lua.org/manual/5.3/manual.html#2.1)关于**基本类型**的说明：

> There are eight basic types in Lua: nil, boolean, number, string, function, userdata, thread, and table. The type nil has one single value, nil, whose main property is to be different from any other value; it usually represents the absence of a useful value. The type boolean has two values, false and true. Both nil and false make a condition false; any other value makes it true. The type number represents both integer numbers and real (floating-point) numbers. The type string represents immutable sequences of bytes. Lua is 8-bit clean: strings can contain any 8-bit value, including embedded zeros ('\0'). Lua is also encoding-agnostic; it makes no assumptions about the contents of a string.
> 
> [翻译](http://cloudwu.github.io/lua53doc/manual.html#2.1)可以看云风的版本:
>
> Lua 中有八种基本类型： nil、boolean、number、string、function、userdata、 thread 和 table。 Nil 是值 nil 的类型， 其主要特征就是和其它值区别开；通常用来表示一个有意义的值不存在时的状态。 Boolean 是 false 与 true 两个值的类型。 nil 和 false 都会导致条件判断为假； 而其它任何值都表示为真。 Number 代表了整数和实数（浮点数）。 String 表示一个不可变的字节序列。 Lua 对 8 位是友好的： 字符串可以容纳任意 8 位值， 其中包含零 ('\0') 。 Lua 的字符串与编码无关； 它不关心字符串中具体内容。

现在看 `lua.h` 中对基本类型的定义：

``` c
/*
** basic types
*/
#define LUA_TNONE		(-1)

#define LUA_TNIL		0
#define LUA_TBOOLEAN		1
#define LUA_TLIGHTUSERDATA	2
#define LUA_TNUMBER		3
#define LUA_TSTRING		4
#define LUA_TTABLE		5
#define LUA_TFUNCTION		6
#define LUA_TUSERDATA		7
#define LUA_TTHREAD		8

#define LUA_NUMTAGS		9	// 基本类型 tag 总数
```

`LUA_NUMTAGS` 是基本类型总数，它计的是 `9` 种，没有算上 `LUA_TNONE`。  
如何如何？如何不算 `LUA_TNONE` 呢？怎么说是 `9` 种而不是官方说的 `8` 种呢？  
别急，我们先抛开疑惑，看下如何获取数据的基本类型。

### 值类型判断
`Lua` 提供了 `13` 个值类型判断的接口，其中 `8` 个基于 `lua_type` 接口完成：

``` c
#define lua_isfunction(L,n)	(lua_type(L, (n)) == LUA_TFUNCTION)
#define lua_istable(L,n)	(lua_type(L, (n)) == LUA_TTABLE)
#define lua_islightuserdata(L,n)	(lua_type(L, (n)) == LUA_TLIGHTUSERDATA)
#define lua_isnil(L,n)		(lua_type(L, (n)) == LUA_TNIL)
#define lua_isboolean(L,n)	(lua_type(L, (n)) == LUA_TBOOLEAN)
#define lua_isthread(L,n)	(lua_type(L, (n)) == LUA_TTHREAD)
#define lua_isnone(L,n)		(lua_type(L, (n)) == LUA_TNONE)
#define lua_isnoneornil(L, n)	(lua_type(L, (n)) <= 0)

LUA_API int             (lua_isnumber) (lua_State *L, int idx);
LUA_API int             (lua_isstring) (lua_State *L, int idx);
LUA_API int             (lua_iscfunction) (lua_State *L, int idx);
LUA_API int             (lua_isinteger) (lua_State *L, int idx);
LUA_API int             (lua_isuserdata) (lua_State *L, int idx);

LUA_API int             (lua_type) (lua_State *L, int idx);
LUA_API const char     *(lua_typename) (lua_State *L, int tp);
```

#### lua_type
首先来看看 `lua_type` 是怎么实现的：
``` c
LUA_API int lua_type (lua_State *L, int idx) {
  StkId o = index2addr(L, idx);
  return (isvalid(o) ? ttnov(o) : LUA_TNONE);
}

// StkId
typedef TValue *StkId;  /* index to stack elements */

// isvalid
#define isvalid(o)	((o) != luaO_nilobject)

// luaO_nilobject
/*
** (address of) a fixed nil value
*/
#define luaO_nilobject		(&luaO_nilobject_)

// luaO_nilobject_
LUAI_DDEF const TValue luaO_nilobject_ = {NILCONSTANT};

// NILCONSTANT
/* macro defining a nil value */
#define NILCONSTANT	{NULL}, LUA_TNIL

// ttnov
/* type tag of a TValue with no variants (bits 0-3) */
#define ttnov(o)	(novariant(rttype(o)))

// rttype
/* raw type tag of a TValue */
#define rttype(o)	((o)->tt_)

// novariant
/* tag with no variants (bits 0-3) */
#define novariant(x)	((x) & 0x0F)
``` 

其中 `StdId` 是一个 `TValue *` 类型，由注释得知，`index2addr(L, idx);` 的原意是取出栈中对应索引处的元素*(原始值)*。

##### isvalid

现在假设我们从栈中取出了一个原始值，我们往下走到 `isvalid`。它将原始值与一个 `luaO_nilobject` 对象做比较，以此判定原始值是否有效；而 `luaO_nilobject` 对象的定义是一个地址，其中存储的是一个常量 `luaO_nilobject_`；`luaO_nilobject_` 是一个 `const TValue *` 类型，它的携带正体由 `NILCONSTANT` 规定；由于 `NILCONSTANT` 是一个宏定义，我们将其带入展开后得到 `luaO_nilobject_` 的完整定义：

``` c
LUAI_DDEF const TValue luaO_nilobject_ = {{NULL}, LUA_TNIL};

// LUAI_DDEF 定义为空，看来它只是 Lua 为了区别其他定义方式的一个标记而已
#define LUAI_DDEF	/* empty */
``` 

也就是说，`luaO_nilobject_` 是一个原始值，且其 `value_` 域为 `{NULL}`，类型标记 `tt_` 域为 `LUA_TNIL`，这就是一个 `nil` 值的正体定义。  
好，现在我们知道 `isvalid` 的机制是将原始值与 `nil` 原始值做比较，如果有效，原始值的类型就是 `ttnov(o)` 执行的结果，否则就是 `LUA_TNONE` 类型。

##### ttnov
我们接着看 `ttnov`，它取出原始值的类型标记 `tt_`，然后对其进行位运算，取出前四位。
为什么是前四位？我们来深入考察一下 `tt_`，我们知道 `tt_` 是一个 `int` 类型的值，之前的对它的作用定义是携带原始值的类型标记，实际上它的功用远不止如此：

``` c
// lobject.h 31
/*
** tags for Tagged Values have the following use of bits:
** bits 0-3: actual tag (a LUA_T* value)
** bits 4-5: variant bits
** bit 6: whether value is collectable
*/
```

通过注释我们了解到，`tt_` 被分成3个部分，其中：

- 0 - 3 : 大类型标记
- 4 - 5 : 子类型标记
- 6 : 可回收标记

我们找到子类型定义：

``` c
// lobject.h 19
/*
** Extra tags for non-values
*/
#define LUA_TPROTO	LUA_NUMTAGS		/* function prototypes */
#define LUA_TDEADKEY	(LUA_NUMTAGS+1)		/* removed keys in tables */

/*
** number of all possible tags (including LUA_TNONE but excluding DEADKEY)
*/
#define LUA_TOTALTAGS	(LUA_TPROTO + 2)

// ...

/* Variant tags for functions */
#define LUA_TLCL	(LUA_TFUNCTION | (0 << 4))  /* Lua closure */
#define LUA_TLCF	(LUA_TFUNCTION | (1 << 4))  /* light C function */
#define LUA_TCCL	(LUA_TFUNCTION | (2 << 4))  /* C closure */


/* Variant tags for strings */
#define LUA_TSHRSTR	(LUA_TSTRING | (0 << 4))  /* short strings */
#define LUA_TLNGSTR	(LUA_TSTRING | (1 << 4))  /* long strings */


/* Variant tags for numbers */
#define LUA_TNUMFLT	(LUA_TNUMBER | (0 << 4))  /* float numbers */
#define LUA_TNUMINT	(LUA_TNUMBER | (1 << 4))  /* integer numbers */


/* Bit mark for collectable types */
#define BIT_ISCOLLECTABLE	(1 << 6)
```

将其与 `lua.h` 里定义的大类型归并整理后得到 `tt_` 可存储的所有 `tag` 定义：
``` c
#define LUA_TNONE             (-1) 	/* none : no value */
#define LUA_TNIL              0		/* nil */
#define LUA_TBOOLEAN          1		/* bool */
#define LUA_TLIGHTUSERDATA    2		/* light userdata */
#define LUA_TNUMBER           3		/* number */
  #define LUA_TNUMFLT         (LUA_TNUMBER | (0 << 4))  /* float numbers */
  #define LUA_TNUMINT         (LUA_TNUMBER | (1 << 4))  /* integer numbers */
#define LUA_TSTRING           4		/* string */
  #define LUA_TSHRSTR         (LUA_TSTRING | (0 << 4))  /* short strings */
  #define LUA_TLNGSTR         (LUA_TSTRING | (1 << 4))  /* long strings */
#define LUA_TTABLE            5		/* table */
#define LUA_TFUNCTION         6		/* function */
  #define LUA_TLCL            (LUA_TFUNCTION | (0 << 4))  /* Lua closure */
  #define LUA_TLCF            (LUA_TFUNCTION | (1 << 4))  /* light C function */
  #define LUA_TCCL            (LUA_TFUNCTION | (2 << 4))  /* C closure */
#define LUA_TUSERDATA         7		/* userdata */
#define LUA_TTHREAD           8		/* thread */
#define LUA_NUMTAGS           9		/* numtags */

#define LUA_TPROTO            LUA_NUMTAGS		/* proto */
#define LUA_TDEADKEY          (LUA_NUMTAGS+1)	/* table 中已移除的键，现在不甚懂 */
#define LUA_TOTALTAGS         (LUA_TPROTO+2)	/* 大类总数 */
#define BIT_ISCOLLECTABLE     (1 << 6)			/* 使能可回收 */
```

回到 `ttnov`，现在可以清楚地知道它取 `tt_` 前四位的意义：**得到原始值的大类型**。

##### lua_type 总结

- `lua_type` 首先判断原始值是否有效，最后再根据有效结果返回原始值的大类型；
- 通过将原始值与 `nil` 原始值进行比较，从而得到原始值是否有效；
- 通过获取原始值类型标记 `tt_` 的前四位可以得到原始值的大类型。

#### 子类型判断
由于 `lua_type` 只能用于原始值的大类型判断，而不能用于子类型。因此 Lua 单独分出了检查子类型的方法。而我们已经知道对原始值类型的判断的原理总是基于 `tt_` 域，就不展开讲了：

``` c
// lobject.h 126

/* raw type tag of a TValue */
#define rttype(o)	((o)->tt_)

/* tag with no variants (bits 0-3) */
#define novariant(x)	((x) & 0x0F)

/* type tag of a TValue (bits 0-3 for tags + variant bits 4-5) */
#define ttype(o)	(rttype(o) & 0x3F)

/* type tag of a TValue with no variants (bits 0-3) */
#define ttnov(o)	(novariant(rttype(o)))


/* Macros to test type */
#define checktag(o,t)		(rttype(o) == (t))
#define checktype(o,t)		(ttnov(o) == (t))
#define ttisnumber(o)		checktype((o), LUA_TNUMBER)
#define ttisfloat(o)		checktag((o), LUA_TNUMFLT)
#define ttisinteger(o)		checktag((o), LUA_TNUMINT)
#define ttisnil(o)		checktag((o), LUA_TNIL)
#define ttisboolean(o)		checktag((o), LUA_TBOOLEAN)
#define ttislightuserdata(o)	checktag((o), LUA_TLIGHTUSERDATA)
#define ttisstring(o)		checktype((o), LUA_TSTRING)
#define ttisshrstring(o)	checktag((o), ctb(LUA_TSHRSTR))
#define ttislngstring(o)	checktag((o), ctb(LUA_TLNGSTR))
#define ttistable(o)		checktag((o), ctb(LUA_TTABLE))
#define ttisfunction(o)		checktype(o, LUA_TFUNCTION)
#define ttisclosure(o)		((rttype(o) & 0x1F) == LUA_TFUNCTION)
#define ttisCclosure(o)		checktag((o), ctb(LUA_TCCL))
#define ttisLclosure(o)		checktag((o), ctb(LUA_TLCL))
#define ttislcf(o)		checktag((o), LUA_TLCF)
#define ttisfulluserdata(o)	checktag((o), ctb(LUA_TUSERDATA))
#define ttisthread(o)		checktag((o), ctb(LUA_TTHREAD))
#define ttisdeadkey(o)		checktag((o), LUA_TDEADKEY)
```

### 值类型别名
看完值类型的判断，来看值类型的别名。值类型别名由 `lua_typename` 给出，定义如下：

``` c
LUA_API const char *lua_typename (lua_State *L, int t) {
  UNUSED(L);
  api_check(L, LUA_TNONE <= t && t < LUA_NUMTAGS, "invalid tag");
  return ttypename(t);
}

// UNUSED
/* macro to avoid warnings about unused variables */
#if !defined(UNUSED)
#define UNUSED(x)	((void)(x))
#endif

// ttypename
#define ttypename(x)	luaT_typenames_[(x) + 1]

// luaT_typenames_
static const char udatatypename[] = "userdata";

LUAI_DDEF const char *const luaT_typenames_[LUA_TOTALTAGS] = {
  "no value",
  "nil", "boolean", udatatypename, "number",
  "string", "table", "function", udatatypename, "thread",
  "proto" /* this last case is used for tests only */
};

/*
** number of all possible tags (including LUA_TNONE but excluding DEADKEY)
*/
#define LUA_TOTALTAGS	(LUA_TPROTO + 2)
```

其中，`UNUSED` 用于防止未使用变量提示警告；`api_check` 检查类型tag `t` 是否在指定范围 `[-1,9)` 内；`ttypename` 才是真正获取值类型别名的方法，我们看到它是一个宏定义，内部实际上使用了一个不可变长数组 `luaT_typenames_`，用于存储类型别名，数组中的元素分别对应到指定的基本类型；注意到 `LUA_TLIGHTUSERDATA` 和 `LUA_TUSERDATA` 被统一命名为 `userdata`，也就是说，在 `Lua` 层，对这两种类型是不做区分的；现在联系到 `LUA_NUMTAGS` 的计数范围 `[0,8]`，就可以理解 `8` 种基本类型的由来了。

那为什么 `LUA_TNONE` 和 `LUA_TPROTO` 不算呢？我们注意到 `LUA_TPROTO` 的注释说明，它是额外的标记，本身不带任何值，因此也就不计算在值类型中。而 `LUA_TNONE` 则没有那么明确，于是 StackOverflow 找答案，找到一个：[Is 'none' one of basic types in Lua?](http://stackoverflow.com/questions/38562720/is-none-one-of-basic-types-in-lua?noredirect=1#comment64516259_38562720)，回答说：
>  No. It not a type. It is only for use with C API.

也就是说，`LUA_TNONE` 是一个辅助类型标记，它仅供 C API 使用，对 `Lua` 层它是不可见的，因此也就不计入基本类型当中了。


## 终了
- 勤思考，多动脑，纵使一时不解，也可加深理解，终能乘风破浪也。
- 上下文联系是多么重要，语文没白学。
