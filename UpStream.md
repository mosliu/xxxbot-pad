步骤一：将你的 Fork 克隆到本地

    打开你的终端或 Git Bash。

    导航到你想要存放项目的本地目录。

    克隆你的 Fork仓库： 将下面命令中的 mosliu 替换成你的 GitHub 用户名（如果不同的话）。
    Bash

git clone https://github.com/mosliu/xxxbot-pad.git

进入项目目录：
Bash

    cd xxxbot-pad

现在，你的 Fork 仓库的 main (或者 master，取决于默认分支名) 分支的副本已经在你的本地计算机上了。

步骤二：进行修改

    在本地项目中进行你需要的修改。 你可以使用任何你喜欢的代码编辑器。

    查看修改状态：
    Bash

git status

添加修改到暂存区：
Bash

git add .  # 添加所有修改过的文件
# 或者 git add <文件名>  # 添加指定文件

提交修改：
Bash

git commit -m "你的提交信息，清晰描述你做了什么修改"

将修改推送到你的 GitHub Fork 仓库：
Bash

    git push origin main  # 或者 git push origin master，取决于你的分支名

步骤三：添加原项目为上游 (Upstream)

为了能够获取原项目 (NanSsye/xxxbot-pad) 的更新，你需要将其添加为一个远程仓库，通常我们称之为 upstream。

    在你的本地项目目录中，运行以下命令：
    Bash

git remote add upstream https://github.com/NanSsye/xxxbot-pad.git

验证是否添加成功：
Bash

    git remote -v

    你应该能看到类似下面的输出，其中 origin 指向你的 Fork，upstream 指向原项目：

    origin  https://github.com/mosliu/xxxbot-pad.git (fetch)
    origin  https://github.com/mosliu/xxxbot-pad.git (push)
    upstream        https://github.com/NanSsye/xxxbot-pad.git (fetch)
    upstream        https://github.com/NanSsye/xxxbot-pad.git (push)

步骤四：定期将上游的更新合并到你的 Fork

当原项目 (NanSsye/xxxbot-pad) 有新的更新时，你需要将这些更新同步到你的本地仓库，然后再推送到你的 GitHub Fork。

    确保你在你的本地主分支上 (通常是 main 或 master)：
    Bash

git checkout main  # 或者 git checkout master

从上游仓库抓取最新的更改：
Bash

git fetch upstream

这个命令会将上游仓库的所有分支和提交下载到你的本地，但不会自动合并任何内容。

将上游仓库的主分支合并到你的本地主分支：

    选项一：使用 git merge (推荐给初学者)
    Bash

git merge upstream/main  # 假设原项目的主分支是 main
# 或者 git merge upstream/master 如果原项目的主分支是 master

如果存在冲突，Git 会提示你手动解决冲突。解决冲突后，你需要再次 git add . 和 git commit。

选项二：使用 git rebase (使提交历史更线性，但需谨慎使用，特别是多人协作时)
Bash

    git rebase upstream/main # 假设原项目的主分支是 main
    # 或者 git rebase upstream/master 如果原项目的主分支是 master

    Rebase 会将你的本地提交“重放”到上游分支的最新提交之后。同样，如果存在冲突，需要解决冲突，然后使用 git rebase --continue。

将合并后的代码推送到你的 GitHub Fork 仓库：
Bash

    git push origin main  # 或者 git push origin master

总结和建议：

    定期 git fetch upstream：养成定期检查上游更新的习惯。
    在合并前确保本地工作区是干净的：即所有本地修改都已经提交或者储藏 (stash)。