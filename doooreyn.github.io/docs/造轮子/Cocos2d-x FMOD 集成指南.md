# FMOD 集成指南

作者：**Reyn**

## 前提

[FMOD](https://www.fmod.com/)是为游戏开发者准备的音频引擎，比起 Cocos2d-x 内置的`SimpleAudioEngine`，其专业能力超出`SimpleAudioEngine`好几个量级。长期以来，我们内部使用的一直是`SimpleAudioEngine`，期间出现过音频无法播放、丢失等问题，为解决`SimpleAudioEngine`的硬伤，我们决定使用`FMOD`替换掉`SimpleAudioEngine`。这篇文章就旨在讲解`FMOD`集成的过程。

## 方案

本次集成基于开源方案[cocos2d-x-fmod](https://github.com/semgilo/cocos2d-x-fmod)，然而由于`cocos2d-x-fmod`集成的 api 过于简陋，没有发挥出`fmod`应有的强大，比如：设置音量缺失、不区分音乐和音效、不提供重播功能等，因此我在其基础上新增了很多 API 以适应项目的需要，并尽量向`SimpleAudioEngine`提供的 API 看齐。API 的扩展在此处不是重点，下面重点说明集成的过程。

## 一、代码集成

1. 拉取 [cocos2d-x-fmod](https://github.com/semgilo/cocos2d-x-fmod)
2. 将`fmod`目录复制到`frameworks⁩/cocos2d-x⁩/external`
3. 将`lua_fmod_auto.cpp`和`lua_fmod_auto.hpp`复制到`frameworks⁩/cocos2d-x⁩/cocos/scripting/lua-binding/manual` _(这里是一个坑，虽然它是 auto，但实际上是 manual，因此把它丢到 manual 下)_
4. 修改`frameworks/cocos2d-x/cocos/scripting/lua-bindings/manual/CCLuaStack.cpp`
    ```cpp
    ...
    #include "fmod/lua_fmod_auto.hpp"
    ...
    // 2.register
    bool LuaStack::init(void)
    {
    	...
        register_all_cocos2dx_fmod(_state);
    	...
    	return true;
    }
    ```

## 二、Windows 集成

1. 将`FMODAudioEngine.cpp`和`FMODAudioEngine.h`添加到`libcocos2d`工程
   ![](https://github.com/semgilo/cocos2d-x-fmod/raw/master/images/fmod/win/add_engine.png)
2. 将`lua_fmod_auto.cpp`和`lua_fmod_auto.hpp`添加到`libluacocos2d`工程
   ![](http://mindoc_c30b4fc1e995f4cf56cd1f0896e85cc7.cynking.com:8181/uploads/202108/client/attach_169a38ad3a1c800a.jpg)
3. 配置 fmod 的附加库目录
   ![](https://github.com/semgilo/cocos2d-x-fmod/raw/master/images/fmod/win/add_lib_search_path.png)
4. 添加 fmod 的附加依赖项
   ![](https://github.com/semgilo/cocos2d-x-fmod/blob/master/images/fmod/win/add_libs.png?raw=true)
5. 编译，成功后需要将`fmodL.dll`动态库复制到生成目录，否则程序会提示`fmodL.dll`而运行不起来

### 三、Android 集成

1. 将`fmod.jar`复制到`app/libs`目录下，并修改`app/build.gradle`将其添加为库：

```gradle
// fmod
implementation files('libs\\fmod.jar')
```

2. 修改`AppActivity.java`

```java
	...
	static
	{
		//加载fmodL动态库
		System.loadLibrary("fmodL");
	}
	...
	protected void onCreate(Bundle savedInstanceState) {
	...
	// 初始化fmod
	org.fmod.FMOD.init(this);
	...
	}
	···
	protected void onDestroy() {
		···
		org.fmod.FMOD.close();
		···
		super.onDestroy();
	}
	···
```

3. 修改`cocos/Android.mk`:

```plaintext
	···
	LOCAL_STATIC_LIBRARIES += fmod_static
	···
	$(call import-module,fmod/prebuilt/android)
```

4. 修改`cocos/scripting/lua-bindings/proj.android/Android.mk`:

```plaintext
	···
	LOCAL_SRC_FILES += ../manual/fmod/lua_fmod_auto.cpp

	LOCAL_C_INCLUDES := $(LOCAL_PATH)/../../../../external/lua/tolua \
	···
						$(LOCAL_PATH)/../manual/fmod \
						$(LOCAL_PATH)/../../../../external/fmod \
	···
	LOCAL_EXPORT_C_INCLUDES := $(LOCAL_PATH)/../../../../external/lua/tolua \
	···
						$(LOCAL_PATH)/../manual/fmod \
						$(LOCAL_PATH)/../../../../external/fmod \
	···
```
