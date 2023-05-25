# Mac nvm 完全卸载指南

**第一步: 检查环境**

```bash
# echo $PATH
/usr/local/bin:/usr/local/sbin:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/root/.nvm/versions/node/v6.2.2/bin
```

**第二步: 删除 nvm 相关环境路径**

```bash
export PATH=/usr/local/bin:/usr/local/sbin:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
```

**第三步: 删除 nvm 相关目录**

```bash
rm -rf $NVM_DIR ~/.npm ~/.bower && unset NVM_DIR
```

**第四步: 从 shell 配置 _(例如：.bashrc/.zshrc)_ 中删除以下 nvm 相关环境变量**

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
```

**第五步: 重启 shell**
