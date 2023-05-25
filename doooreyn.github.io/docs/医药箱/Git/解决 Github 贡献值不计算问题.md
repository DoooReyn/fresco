# 解决 Github 贡献值不计算问题

回顾一下去年的贡献值，发现竟然奇低无比。虽然去年的仓库大部分放在了  [coding.net](https://coding.net/)，但是怎么说小破站的更新频率也没有那么低呀。

前几天提交了几份新的仓库，统计一下发现虽然新增了贡献值，但只计算了创建仓库和初次提交两次贡献，后续的`commit`并没有计算在内。

这就纳闷了，于是写了个脚本，自动修改文件，添加并推送到仓库，然后看贡献值变化。

果然一点都没有变。

网上查了一下`GitHub 不记录贡献值`，终于给我找到了原因，原来是因为小破站要求 git 配置中的用户邮箱必须与小破站的一致。

这是原回答：[解决 GitHub 不记录贡献值问题](https://blog.csdn.net/qq_28802895/article/details/102761102)。

当然你也可以从[官方文档](https://help.github.com/en/github/setting-up-and-managing-your-github-profile/why-are-my-contributions-not-showing-up-on-my-profile)中找到解释。

> Commits must be made with an email address that has been added to your GitHub account, or the GitHub-provided noreply email address provided to you in your email settings, in order to appear on your contributions graph. For more information about noreply email addresses, see "Setting your commit email address."

> If the email address used for the commit hasn't been added to your GitHub profile, you must add the email address to your GitHub account. Your contributions graph will be rebuilt automatically when you add the new address.
