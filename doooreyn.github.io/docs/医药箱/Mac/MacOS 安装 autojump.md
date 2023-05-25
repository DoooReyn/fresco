# MacOS 安装 autojump

## 安装

```bash
> brew install autojump
Updating Homebrew...
==> Auto-updated Homebrew!
==> Downloading https://homebrew.bintray.com/bottles/autojump-22.5.3.catalina.bottle.tar.gz
######################################################################## 100.0%
==> Pouring autojump-22.5.3.catalina.bottle.tar.gz
==> Caveats
Add the following line to your ~/.bash_profile or ~/.zshrc file (and remember
to source the file to update your current session):
  [ -f /usr/local/etc/profile.d/autojump.sh ] && . /usr/local/etc/profile.d/autojump.sh

If you use the Fish shell then add the following line to your ~/.config/fish/config.fish:
  [ -f /usr/local/share/autojump/autojump.fish ]; and source /usr/local/share/autojump/autojump.fish

zsh completions have been installed to:
  /usr/local/share/zsh/site-functions
==> Summary
```

## 配置

如果你用的是 `bash`，配置文件位于 `~/.bashrc` 或 `~/.bash_profile`；如果是 `zsh`，则位于 `~/.zshrc`。然后在配置文件中添加如下代码：

```bash
[ -f /usr/local/etc/profile.d/autojump.sh ] && . /usr/local/etc/profile.d/autojump.sh
```

如果你用的是 `fish`，那么配置文件是 `~/.config/fish/config.fish`；如果是 `omf`，则位于 `~/.local/share/omg/init.fish`。然后在配置文件中添加如下代码：

```fish
[ -f /usr/local/share/autojump/autojump.fish ];
```

保存后刷新一下配置文件：

```bash
> source /usr/local/share/autojump/autojump.fish
```

## 用法

只有打开过的目录 `autojump` `才会记录，所以使用时间越长，autojump` 才会越智能。

可以使用 `autojump` 命令，或者使用短命令 `j`.

```bash
> autojump --help
usage: autojump [-h] [-a DIRECTORY] [-i [WEIGHT]] [-d [WEIGHT]] [--complete]
                [--purge] [-s] [-v]
                [DIRECTORY [DIRECTORY ...]]

Automatically jump to directory passed as an argument.

positional arguments:
  DIRECTORY             directory to jump to

optional arguments:
  -h, --help            show this help message and exit
  -a DIRECTORY, --add DIRECTORY
                        add path
  -i [WEIGHT], --increase [WEIGHT]
                        increase current directory weight
  -d [WEIGHT], --decrease [WEIGHT]
                        decrease current directory weight
  --complete            used for tab completion
  --purge               remove non-existent paths from database
  -s, --stat            show database entries and their key weights
  -v, --version         show version information

Please see autojump(1) man pages for full documentation.

```
