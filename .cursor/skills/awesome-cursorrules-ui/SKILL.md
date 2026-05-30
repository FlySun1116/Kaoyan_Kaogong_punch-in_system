---
name: awesome-cursorrules-ui
description: >-
  来自 PatrickJS/awesome-cursorrules 的前端美化 Cursor 规则索引。
  在美化 app/templates/、style.css、Bootstrap 页面时使用；
  与 kaoyan-ui、hallmark、effective-ui-design 配合。
---

# awesome-cursorrules 前端规则（本项目已安装）

> 仓库：https://github.com/PatrickJS/awesome-cursorrules

已从该仓库挑选并**适配本项目栈**（Bootstrap 5 + Jinja2 + 原生 JS），安装为 `.cursor/rules/*.mdc`，编辑对应文件时自动挂载。

## 已安装规则

| 规则文件 | 原仓库来源 | 作用 |
|----------|------------|------|
| `toss-style-design-system.mdc` | toss-style-design-system | 克制配色、间距、排版、卡片、无障碍 |
| `html-bootstrap-javascript.mdc` | html-tailwind-css-javascript（已改 Bootstrap） | HTML 语义、Bootstrap 组件、fetch 交互 |
| `jinja2-templates.mdc` | shopify-theme-dev-liquid（已改 Jinja2） | 模板结构、宏、空状态、静态资源 |
| `hallmark.mdc` | nutlope/hallmark | 反 AI 审美、audit/redesign |

## 与本项目 Skills 的配合顺序

1. **kaoyan-ui** — 技术栈约束（禁止 Tailwind/React、品牌色、页面清单）
2. **toss-style-design-system** + **effective-ui-design** — 设计 token、对比度、8pt 间距
3. **hallmark** — audit / redesign，避免通用 AI 风
4. **jinja2-templates** + **html-bootstrap-javascript** — 实现细节

## 触发示例

```
按 hallmark audit app/templates/index.html
加载 kaoyan-ui + toss-style-design-system，美化进度页环形图区域
redesign subjects.html，保留 Jinja2 与 API
```

## 更新方式

```bash
# 在项目根目录执行，重新拉取并覆盖（需手动再适配 globs/栈说明）
curl -sL -o .cursor/rules/toss-style-design-system.mdc \
  https://raw.githubusercontent.com/PatrickJS/awesome-cursorrules/main/rules/toss-style-design-system.mdc
```

安装日期：2026-05-30
