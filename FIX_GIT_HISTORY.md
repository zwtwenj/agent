# 修复 Git 历史中的敏感信息

## 问题
GitHub Push Protection 检测到 `agent/.env` 文件中包含 API 密钥，阻止了推送。

## 解决方案

### 方案 1：使用 BFG Repo-Cleaner（推荐）

1. 下载 BFG：https://rtyley.github.io/bfg-repo-cleaner/
2. 运行清理：
```bash
java -jar bfg.jar --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### 方案 2：创建新分支（如果仓库是新的）

如果这是新仓库且只有几个提交，可以：

1. 创建新分支（不包含敏感信息）：
```bash
git checkout --orphan clean-main
git add .
git commit -m "Initial commit without secrets"
git branch -D main
git branch -m main
git push -f origin main
```

### 方案 3：使用 git filter-repo（需要安装）

```bash
pip install git-filter-repo
git filter-repo --path agent/.env --invert-paths
git push --force
```

### 方案 4：手动重写（当前情况）

由于历史中仍有密钥，需要：

1. 备份当前代码
2. 删除 .git 文件夹
3. 重新初始化仓库
4. 添加所有文件（.env 已在 .gitignore 中）
5. 提交并推送

## 当前状态

- ✅ 已创建 .gitignore
- ✅ 已从当前工作区移除 .env
- ⚠️ 历史提交中仍包含密钥内容

## 下一步

选择上述方案之一来完全清理历史。
