步骤一：将你的 Fork 克隆到本地
```
git clone https://github.com/mosliu/xxxbot-pad.git
cd xxxbot-pad
git remote add upstream https://github.com/NanSsye/xxxbot-pad.git
# 验证是否添加成功
git remote -v

git fetch upstream
git merge upstream/main
```

如果存在冲突，Git 会提示你手动解决冲突。解决冲突后，你需要再次 git add . 和 git commit。
将合并后的代码推送到你的 GitHub Fork 仓库：
```
    git add .
    git commit -m "Merge upstream changes"
    git push origin main 
```