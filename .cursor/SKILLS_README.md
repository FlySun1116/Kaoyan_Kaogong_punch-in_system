# 已安装的前端美化 Skills & Rules

本项目 `.cursor/skills/` 与 `.cursor/rules/` 下已安装前端美化相关配置。

## Skills（Agent 主动加载）

| 技能 | 目录 | 用途 |
|------|------|------|
| **hallmark** | `skills/hallmark/` | 避免 AI 通用审美；build / audit / redesign / study |
| **effective-ui-design** | `skills/effective-ui-design/` | WCAG、间距、配色、排版、表单、按钮规范 |
| **kaoyan-ui** | `skills/kaoyan-ui/` | 本项目的 Bootstrap + Jinja2 约束与品牌色 |
| **awesome-cursorrules-ui** | `skills/awesome-cursorrules-ui/` | [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) 规则索引与配合方式 |

## Cursor Rules（编辑文件时自动挂载）

| 规则 | 文件 | 来源 |
|------|------|------|
| Hallmark | `rules/hallmark.mdc` | nutlope/hallmark |
| Toss 设计系统 | `rules/toss-style-design-system.mdc` | awesome-cursorrules |
| HTML + Bootstrap + JS | `rules/html-bootstrap-javascript.mdc` | awesome-cursorrules（Tailwind 版已适配） |
| Jinja2 模板 | `rules/jinja2-templates.mdc` | awesome-cursorrules（Liquid 版已适配） |

## 推荐使用方式

```
# 审计现有页面
按 hallmark audit app/templates/index.html

# 美化首页（推荐组合）
加载 kaoyan-ui + hallmark + effective-ui-design + awesome-cursorrules-ui，
redesign app/templates/index.html，保留 Jinja2 与 API

# 从参考站提取风格
hallmark study https://example.com
```

## 安装来源

| 组件 | 来源 |
|------|------|
| hallmark | https://github.com/nutlope/hallmark |
| effective-ui-design | https://github.com/sebastian-software/effective-ui-design-skill |
| kaoyan-ui | 项目自建 |
| awesome-cursorrules 三条规则 | https://github.com/PatrickJS/awesome-cursorrules |

## 更新 awesome-cursorrules 规则

重新下载后需检查 `globs` 与栈说明是否仍适配 Bootstrap + Jinja2：

```bash
BASE=https://raw.githubusercontent.com/PatrickJS/awesome-cursorrules/main/rules
curl -sL "$BASE/toss-style-design-system.mdc" -o .cursor/rules/toss-style-design-system.mdc
# html-tailwind 与 shopify-liquid 需手动合并到 html-bootstrap-javascript.mdc / jinja2-templates.mdc
```

最后更新：2026-05-30
