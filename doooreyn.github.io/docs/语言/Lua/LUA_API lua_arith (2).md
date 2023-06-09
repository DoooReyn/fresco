# LUA_API lua_arith (2)

## 开篇
> 上一节分析了 `lua_arith` 的大部分代码，由于篇幅原因，留到本节将继续讲解剩余的部分：
``` c
luaO_arith(L, op, L->top - 2, L->top - 1, L->top - 2);
L->top--;  /* remove second operand */
lua_unlock(L);
```

## 解析
现在我们来看运算规则 `luaO_arith` ：

``` c
// lobject.c 123
void luaO_arith (lua_State *L, int op, const TValue *p1, const TValue *p2,
                 TValue *res) {
  switch (op) {
    case LUA_OPBAND: case LUA_OPBOR: case LUA_OPBXOR:
    case LUA_OPSHL: case LUA_OPSHR:
    case LUA_OPBNOT: {  /* operate only on integers */
      lua_Integer i1; lua_Integer i2;
      if (tointeger(p1, &i1) && tointeger(p2, &i2)) {
        setivalue(res, intarith(L, op, i1, i2));
        return;
      }
      else break;  /* go to the end */
    }
    case LUA_OPDIV: case LUA_OPPOW: {  /* operate only on floats */
      lua_Number n1; lua_Number n2;
      if (tonumber(p1, &n1) && tonumber(p2, &n2)) {
        setfltvalue(res, numarith(L, op, n1, n2));
        return;
      }
      else break;  /* go to the end */
    }
    default: {  /* other operations */
      lua_Number n1; lua_Number n2;
      if (ttisinteger(p1) && ttisinteger(p2)) {
        setivalue(res, intarith(L, op, ivalue(p1), ivalue(p2)));
        return;
      }
      else if (tonumber(p1, &n1) && tonumber(p2, &n2)) {
        setfltvalue(res, numarith(L, op, n1, n2));
        return;
      }
      else break;  /* go to the end */
    }
  }
  /* could not perform raw operation; try metamethod */
  lua_assert(L != NULL);  /* should not fail when folding (compile time) */
  luaT_trybinTM(L, p1, p2, res, cast(TMS, (op - LUA_OPADD) + TM_ADD));
}
```

### TValue

注意到参数 `3, 4` 是两个操作数，且它们都是 `TValue *` 类型，我们找到 `TValue` 的定义：

```
// lobject.h 100
/*
** Union of all Lua values
*/
typedef union Value {
  GCObject *gc;    /* collectable objects : 可回收的对象 */
  void *p;         /* light userdata : 轻量级 userdata */
  int b;           /* booleans : 布尔值*/
  lua_CFunction f; /* light C functions : 轻量级 C 函数 */
  lua_Integer i;   /* integer numbers : 整型数 */
  lua_Number n;    /* float numbers : 浮点数 */
} Value;


#define TValuefields  Value value_; int tt_


typedef struct lua_TValue {
  TValuefields;
} TValue;
```

`TValue` 是一个结构体别名，用它可以定义一个结构体，其中包含一个联合体 `value_` 和一个整型数 `tt_`；而 `value_` 包含了所有 `Lua` 的值类型：`可回收的对象`、`轻量级 userdata`、`布尔值`、`轻量级 C 函数`、`整型数` 和 `浮点数`。也就是说，除了 `GCObject`，其他 5 个数据类型是不用 `Lua` 回收机制的。

我们来看 `GCObject`：

``` c
// lobject.h 72
/*
** Common type for all collectable objects
*/
typedef struct GCObject GCObject;


/*
** Common Header for all collectable objects (in macro form, to be
** included in other objects)
*/
#define CommonHeader  GCObject *next; lu_byte tt; lu_byte marked


/*
** Common type has only the common header
*/
struct GCObject {
  CommonHeader;
};
```

知道 `GCObject` 首先是个结构体，其次它包含了三个域 ：`GCObject *next; lu_byte tt; lu_byte marked`；这里 `GCObject *` 又被替换为结构体类型 `struct GCObject *`。再看 `lu_byte` ：

``` c
// llimits.h 35
/* chars used as small naturals (so that 'char' is reserved for characters) */
typedef unsigned char lu_byte;
```

可知，`lu_byte` 就是简单的类型别名，用一个 `unsigned char` 类型来表示。
综上对 `GCObject` 的分析，可得：所有的 `GCObject` 都用一个**单向链表**串了起来，每个 `GCObject` 对象都携带 `tt, marked` 两个标记*（其中 `tt` 用来识别其类型，`marked` 域用于标记清除的工作，这些是后话了，现在我也不懂）*。

现在是不是可以理解 Lua 官方对值和类型的说明了：
> Lua is a dynamically typed language. This means that variables do not have types; only values do. There are no type definitions in the language. All values carry their own type.

因为 `TValue` 携带了所有的 `Lua` 值类型，这就是变量没有类型，只有值才有类型的原因！


## Operator Rules

解释完 `TValue`，我们来归纳一下 `switch` 之后的运算符规则：

- `LUA_OPBAND、 LUA_OPBOR、 LUA_OPBXOR、 LUA_OPSHL、 LUA_OPSHR、 LUA_OPBNOT` 遵循 `[1]` 操作；
- `LUA_OPDIV、 LUA_OPPOW` 遵循 `[2]` 操作；
- `LUA_OPADD、 LUA_OPSUB、 LUA_OPMUL、 LUA_OPMOD、 LUA_OPUNM` 遵循 `default` `[3]` 操作。

下面以 `[1]` 作为切入口来解析具体的运算服规则，由于其他操作活类似或略有不同，因此不再多费唇舌。
注意到 `[1]` 中的元素都是单目运算符，其运算规则为：

``` c
{
    lua_Integer i1; lua_Integer i2;
    if (tointeger(p1, &i1) && tointeger(p2, &i2)) {
      setivalue(res, intarith(L, op, i1, i2));
      return;
    }
    else break;  /* go to the end */
}
```

按步骤来说：

1. 声明两个 `lua_Integer` 类型数据 `i1, i2`；
2. 将两个操作数进行类型转换，并将结果分别存储到 `i1, i2`；
3. 如果转换成功，则执行运算后直接返回。
4. 如果转换失败，则跳出 `switch`。

接下来我们逐个分析几个要点：

1. `lua_Integer`
2. `tointeger`
3. `ntarith`
4. `setivalue`


### 1. lua_Integer

`lua_Integer` 定义在 `lua.h 93` 行：`typedef LUA_INTEGER lua_Integer;`。这里是为 `LUA_INTEGER` 定义了别名 `lua_Integer`。而 `LUA_INTEGER` 在 `luaconf.h 524 ~ 574` 行之间有详细的说明，它指代的是整型数据类型。


### 2. tointeger

`tointeger` 定义在 `lvm.h 43` 行：  

``` c
#define tointeger(o,i) \
    (ttisinteger(o) ? (*(i) = ivalue(o), 1) : luaV_tointeger(o,i,LUA_FLOORN2I))
```

再看 `ttisinteger` 和 `ivalue` 是这么定义的：

``` c
/* raw type tag of a TValue */
#define rttype(o) ((o)->tt_)

#define checktag(o,t)   (rttype(o) == (t))
#define ttisinteger(o)    checktag((o), LUA_TNUMINT)

#define check_exp(c,e)    (lua_assert(c), (e))
#define val_(o)   ((o)->value_)
#define ivalue(o) check_exp(ttisinteger(o), val_(o).i)
```

现在我们知道 `o` 是 `Lua` 原始值 `TValue *o`, `rttype(o)` 获取的是原始值的 `tt_` 标记，而 `tt_` 则是原始值类型标记，因此通过 `checktag(o,t)` 可以检查原始值类型标记 `tt_` 是否与预期 `t` 符合，已达到检查值类型的目的。

接着看 `ivalue(o)`：首先它通过 `ttisinteger(o)` 检查当前原始值的类型标记 `tt_` 是不是整型作为断言的判断条件，其次通过 `val_(o)` 取出原始值的真实值 `value_` 中的整型域作为断言的消息，最后通过 `check_exp(c,e)` 进行断言操作。

我们回过头看 `ttisinteger`，就可以拆成 `tt + isinteger`，意思是原始值的标记 `tt_` 标记的是不是整型类型。那么 `LUA_TNUMINT` 指代的就是 `Lua` 中的整型类型了。来看看是不是这样：

``` c
#define LUA_TNUMBER   3

/* Variant tags for numbers */
#define LUA_TNUMFLT (LUA_TNUMBER | (0 << 4))  /* float numbers */
#define LUA_TNUMINT (LUA_TNUMBER | (1 << 4))  /* integer numbers */
```

一看不得了，我们顺便知道了 `LUA_TNUMBER` 定义了 `LUA_TNUMFLT` 和 `LUA_TNUMINT`，也就是 `number` 类型包含了整型和浮点型，这也跟官方的介绍不谋而合：
> The type number represents both integer numbers and real (floating-point) numbers. 

然而，有点经验的同学可能有疑问了：在 `Lua 5.2` 版本中，所有的 `number` 不都是浮点数吗？那这又是什么鬼？
一个可能是我们理解错了，一个可能就是在 `Lua 5.3` 版本中对其做出了修改。我们看版本变更日志是否有提及此事：
> 8.1 – Changes in the Language   
>
> - The main difference between Lua 5.2 and Lua 5.3 is the introduction of an integer subtype for numbers. Although this change should not affect "normal" computations, some computations (mainly those that involve some kind of overflow) can give different results.  
You can fix these differences by forcing a number to be a float (in Lua 5.2 all numbers were float), in particular writing constants with an ending .0 or using x = x + 0.0 to convert a variable. (This recommendation is only for a quick fix for an occasional incompatibility; it is not a general guideline for good programming. For good programming, use floats where you need floats and integers where you need integers.)  

> - The conversion of a float to a string now adds a .0 suffix to the result if it looks like an integer. (For instance, the float 2.0 will be printed as 2.0, not as 2.) You should always use an explicit format when you need a specific format for numbers.

> 简单翻译： 
>  
> - Lua 5.3 与 Lua 5.2 版本主要的差别就是 numbers 新增了子类型 integer。尽管这个改动并不影响“普通”的计算，但部分计算（主要是一些涉及溢出的计算）可能会与之前的版本的计算结果有所不同。  
> 一个修正的方案是将 number 强转为 float (在 Lua 5.2 中所有的 numbers 都是 float)。你可以在常熟后加上 .0 或者使用 x = x + 0.0 的方法来转换。（但这些建议是为了兼容而作的妥协，而并非良好的编程纲领，好的方式是：当用 float 则用 float，当用 integer 则用 integer，泾渭分明，分而治之。）
> - 当将 float 转换为 string 时，如果结果看上去像是 integer，会在结果最后加上 .0。（举个例子，浮点型 2.0 打印出来是 2.0，而不是 2。）

果不其然，我们的分析是正确的，大家可以用两个版本分别验证一下：

``` bash
Lua 5.2.4
> a = 1 + 3.0
> print(a)
4
---------------
Lua 5.3.3
> a = 1 + 3.0
> print(a)
4.0
```

另提一点， 5.3 版本的解释器已经支持直接计算了：

``` bash
Lua 5.2.4
> 1 + 3.0
stdin:1: unexpected symbol near '1'

Lua 5.3.3
> 1 + 3.0
4.0
```

现在剩下一个 `luaV_tointeger` 还在浆糊之中，我们再行探究：

``` c
// lvm.c 94
/*
** try to convert a value to an integer, rounding according to 'mode':
** mode == 0: accepts only integral values
** mode == 1: takes the floor of the number
** mode == 2: takes the ceil of the number
*/
// 注意：integral 是完整的、整体的意思，而非整数！
int luaV_tointeger (const TValue *obj, lua_Integer *p, int mode) {
  TValue v;
 again:
  if (ttisfloat(obj)) {
    lua_Number n = fltvalue(obj); // 取原始值 value_ 的 n 域
    lua_Number f = l_floor(n);    // 对 n 进行 floor 操作，赋值给 f
    // 如果 n != f，那么 obj 就是不可转换为类整数的浮点数 （如2.01）
    if (n != f) {  /* not an integral value? */
      // 而如果 mode ＝ 0，即要求操作数可转换为类整数，那么就直接返回 0
      if (mode == 0) return 0;  /* fails if mode demands integral value */
      // 如果 mode > 1，即要求将操作数进行向上取整
      else if (mode > 1)  /* needs ceil? */
        f += 1;  /* convert floor to ceil (remember: n != f) */
    }
    // 然后执行 number 转换为 integer 操作
    return lua_numbertointeger(f, p);
  }
  else if (ttisinteger(obj)) {
    // 如果操作数本身就是整型数据，那么直接讲原始值的 value_ 的 整数域赋值给 *p 即可
    *p = ivalue(obj);
    return 1;
  }
  else if (cvt2num(obj) &&
            luaO_str2num(svalue(obj), &v) == vslen(obj) + 1) {
    // 如果操作数是字符串，且可完全转换为 number，则将操作数替换为转换后的值后，重头开始转换
    obj = &v;
    goto again;  /* convert result from 'luaO_str2num' to an integer */
  }
  // 转换失败
  return 0;  /* conversion failed */
}

/********* 补充定义 **********/

// fltvalue 
#define fltvalue(o) check_exp(ttisfloat(o), val_(o).n)

// l_floor 
#define l_floor(x)    (l_mathop(floor)(x))

// lua_numbertointeger 
#define lua_numbertointeger(n,p) \
  ((n) >= (LUA_NUMBER)(LUA_MININTEGER) && \
   (n) < -(LUA_NUMBER)(LUA_MININTEGER) && \
      (*(p) = (LUA_INTEGER)(n), 1))

// svalue 
// 从原始值中获取实际的字符串（字节数组）
/* get the actual string (array of bytes) from a Lua value */
#define svalue(o)       getstr(tsvalue(o))

// LUA_FLOORN2I 
// 默认 LUA_FLOORN2I ＝ 0
/*
** You can define LUA_FLOORN2I if you want to convert floats to integers
** by flooring them (instead of raising an error if they are not
** integral values)
*/
#if !defined(LUA_FLOORN2I)
#define LUA_FLOORN2I    0
#endif
```

现在，我们重新理解 `luaV_tointeger(o,i,LUA_FLOORN2I)` 就很简单了，就是将原始值 `o`
 转换为整型数据，然后赋值给 `i`，当然如果转换成功则返回 `1`，失败则返回 `0`。
回过头再看 tointeger 的定义：

``` c
#define tointeger(o,i) \
    (ttisinteger(o) ? (*(i) = ivalue(o), 1) : luaV_tointeger(o,i,LUA_FLOORN2I))
```

现在可以轻松地解释清楚了：如果原始值 `o` 的当前类型标记是整型，则取它的整型数据部分，并返回 `1`；否则，尝试进行转换，转换成功则取转换结果并返回 `1`，失败则返回 `0`；其中 `1` 代表成功，`0` 代表失败。完美！

### 3. intarith
`intarith` 可以拆解为 `int(eger)` 和 `arith(metic)`，顾名思义：整数运算的意思。我们来看定义：
``` c
static lua_Integer intarith (lua_State *L, int op, lua_Integer v1,
                                                   lua_Integer v2) {
  switch (op) {
    case LUA_OPADD: return intop(+, v1, v2);
    case LUA_OPSUB:return intop(-, v1, v2);
    case LUA_OPMUL:return intop(*, v1, v2);
    case LUA_OPMOD: return luaV_mod(L, v1, v2);
    case LUA_OPIDIV: return luaV_div(L, v1, v2);
    case LUA_OPBAND: return intop(&, v1, v2);
    case LUA_OPBOR: return intop(|, v1, v2);
    case LUA_OPBXOR: return intop(^, v1, v2);
    case LUA_OPSHL: return luaV_shiftl(v1, v2);
    case LUA_OPSHR: return luaV_shiftl(v1, -v2);
    case LUA_OPUNM: return intop(-, 0, v1);
    case LUA_OPBNOT: return intop(^, ~l_castS2U(0), v1);
    default: lua_assert(0); return 0;
  }
}

/********** 补充定义 **********/

#define intop(op,v1,v2) l_castU2S(l_castS2U(v1) op l_castS2U(v2))

#if !defined(l_castU2S)
#define l_castU2S(i)  ((lua_Integer)(i))
#endif

#if !defined(l_castS2U)
#define l_castS2U(i)  ((lua_Unsigned)(i))
#endif

/* unsigned integer type */
typedef LUA_UNSIGNED lua_Unsigned;

#define LUA_UNSIGNED    unsigned LUAI_UACINT

#define LUAI_UACINT   LUA_INTEGER

```

`intop(op, v1, v2)`，先将 `v1, v2` 转换为无符号整型，计算出结果之后，再将结果转换为有符号整型。
`luaV_mod`、`luaV_div`、`luaV_shiftl` 则对应 `取模、除法、左移` 操作，这里就不展开了，读者自行探究。


### 4. setivalue

现在来看最后一个要点：`setivalue(v1, v2)`。
我们知道 `ivalue` 是取原始值的整型部分数值，那么不妨把 `setivalue` 拆解为 `set` 和 `ivalue`，解释为将 `v2` 赋值给 `v1` 的整型部分。来看看是不是这样？

``` c
#define setivalue(obj,x) \
  { TValue *io=(obj); val_(io).i=(x); settt_(io, LUA_TNUMINT); }

#define settt_(o,t) ((o)->tt_=(t))
```

我们看到 `setivalue` 和 `settt_` 是宏定义，我们用 `v1, v2` 带入后展开：

``` c
{ TValue *io=(v1); val_(io).i=(v2); io->tt_=(LUA_TNUMINT); }
```

果然，除了最后将原始值的类型标记 `tt_` 赋值为 `LUA_TNUMINT`，其他和我们所料不差。我们也需要谨记，当需要改变 `Lua` 值类型时，必须同时改变它的 `tt_` 类型标记。


### luaT_trybinTM
如果 `switch` 中的运算失败，继而跳出 `switch`，那么就需要执行 `luaT_trybinTM` ：

``` c
/* could not perform raw operation; try metamethod */
luaT_trybinTM(L, p1, p2, res, cast(TMS, (op - LUA_OPADD) + TM_ADD));
```
我们看注释说明：**如果无法执行原始的运算，则进行元方法运算。**
由于元方法涉及运算符的重载，这部分属于 `Lua` 元方法的内容，我们先标记一下，暂且跳过，等接触到元方法之后，回过头再来看这部分内容。

### 回到最初

``` c
// ...
luaO_arith(L, op, L->top - 2, L->top - 1, L->top - 2);
L->top--;  /* remove second operand */
lua_unlock(L);
```

当运算完成后，我们看到栈进行了一次自减操作，目的是移除位于栈中 `L->top - 1` 处的第二操作数，这个时候栈中 `L->top - 2` 索引处存储的则是运算结果了。


### 小结
- `TValue *` 定义的结构体是 `Lua` 的原始值；
- 原始值中携带两份数据，一个是 `Value` 联合体定义的 `value_`，它是携带真实值的正体；一个是类型标记 `tt_`；
- `value_` 包含了所有 `Lua` 值类型的数据，分别是：`可回收的对象 : gc`、`轻量级 userdata : p`、`布尔值 : b`、`轻量级 C 函数 : f`、`整型数 : i` 和 `浮点数 : n`；
- 当原始值数据变化时，类型标记 `tt_` 也将对应改变，如: `(o)->i=n_x`，则对应地 `(o)->tt_=LUA_TNUMINT`。


## 终了
1. 看一次源码，复习好多 C 知识，虽然很累，但很充实。
2. 栈的数据结构可以去复习一下。
3. 阅读中发现了很多 Lua 内置实现的彩蛋，有一种探险的惊喜。

## 参考
- [堆栈 Wikipedia](https://zh.wikipedia.org/wiki/%E5%A0%86%E6%A0%88)
- [基本数据结构：栈（stack）](http://www.cppblog.com/cxiaojia/archive/2012/08/01/185913.html)