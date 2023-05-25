# Mac zsh 粘贴加速

**解决方案**：粘贴下面 👇 代码到 `.zshrc` 并刷新。

```zsh
pasteinit() {
  OLD_SELF_INSERT=${${(s.:.)widgets[self-insert]}[2,3]}
  zle -N self-insert url-quote-magic # I wonder if you'd need `.url-quote-magic`?
}

pastefinish() {
  zle -N self-insert $OLD_SELF_INSERT
}
zstyle :bracketed-paste-magic paste-init pasteinit
zstyle :bracketed-paste-magic paste-finish pastefinish
```

**问题指引**：[官方 issue](https://github.com/zsh-users/zsh-autosuggestions/issues/238)
