# 发布到 GitHub 完整步骤(5 分钟)

## 0. 准备

- GitHub 账号(已有)
- 本地 git(已有)
- 已经通过 `gh auth login` 或配置 SSH key

## 1. 在 GitHub 上建一个空仓库

打开 https://github.com/new,填:

- **Repository name**:`trip-planner`(或 `codex-skill-trip-planner`)
- **Description**:`End-to-end trip planning skill with Glassmorphism + Isometric + Soft 3D mobile-friendly images`
- **Public**(推荐开源,方便别人用)
- ⚠️ **不要勾选** "Add a README file" / "Add .gitignore" / "Choose a license"(我们自己有)

→ 点 **Create repository**

记下 URL,假设是:`https://github.com/<your-username>/trip-planner`

## 2. 推送代码

```bash
cd /Users/a1234/Documents/UZI/00-archive/05-IOPH-JLP/trip-planner-github

# 初始化 git
git init
git add .
git commit -m "feat: initial release of trip-planner skill

- Glassmorphism + Isometric + Soft 3D UI design system
- 3:4 multi-page mobile image generator (Apple Color Emoji)
- Single long-screenshot generator
- 9-category travel essentials checklist
- 6 trip-type question templates
- ICS calendar generator
- Tested with Ipoh → Yibin 5D4N sample"

# 接 GitHub
git branch -M main
git remote add origin https://github.com/<your-username>/trip-planner.git
git push -u origin main
```

第一次 push 会要求输入 GitHub 用户名 + Personal Access Token(不是密码)。

## 3. 验证

打开 `https://github.com/<your-username>/trip-planner`,应该看到:

- README.md 渲染
- 7 张 screenshots/ 预览图
- 4 个 references/
- 3 个 scripts/
- 2 个 examples/

## 4. 从 GitHub 安装到 Codex

```bash
# <owner/repo> 填您的实际仓库名
/Users/a1234/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo <your-username>/trip-planner \
  --path trip-planner
```

**装好后**,新开任何 Codex thread,说"做行程规划"或"用 Glassmorphism 风格出图"就自动激活。

## 5. 后续更新

```bash
cd /path/to/trip-planner-github
# 改了 SKILL.md / scripts / references 后
git add .
git commit -m "feat: 改进 X"
git push
```

其他用户 `git pull` 后重跑安装命令即可同步。

## 6. 进一步(可选)

- 加 GitHub Actions:`.github/workflows/test.yml` 跑 `python scripts/render_story.py examples/...` 验证
- 加 issue template:`.github/ISSUE_TEMPLATE/bug_report.md`
- 加 CHANGELOG.md 记录版本
- 在 README 顶部加 GitHub Actions badge 显示 CI 状态
- 创建 `v1.0` release tag,别人可以直接 `git clone --branch v1.0`

## ❓ 常见问题

### Q: push 时要 Personal Access Token?
A: 2021 年后 GitHub 不再支持密码登录。生成 PAT:
https://github.com/settings/tokens/new
- 选 `repo` scope
- 复制 token,push 时贴上(代替密码)

### Q: 已有同名仓库?
A: 改名:`mv trip-planner-github trip-planner` 然后 push 到 `git@github.com:<u>/trip-planner.git`

### Q: 想私有仓库?
A: GitHub 上建时选 Private,clone 时用 SSH URL `git@github.com:...`,PAT 仍需 `repo` scope。

### Q: 装到 Codex 失败报 "Missing --path"?
A: 第二个参数 `--path` 必填,值为仓库里 skill 所在目录(本仓库是根目录就填 `.`)
