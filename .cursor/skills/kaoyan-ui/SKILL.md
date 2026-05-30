---
name: kaoyan-ui
description: >-
  考研考公学习打卡系统的前端美化规范。在美化 app/templates/、Bootstrap 5 页面、
  Jinja2 模板、style.css 时使用。与 hallmark、effective-ui-design 配合：
  本 skill 约束技术栈与项目结构，另两个 skill 约束美学与无障碍。
---

# 考研考公打卡系统 — UI 规范

## 技术约束（必须遵守）

- **栈**：Jinja2 模板 + Bootstrap 5 CDN + `app/templates/static/style.css`
- **禁止**：引入 React/Vue/Tailwind；不要改 FastAPI 路由逻辑除非用户明确要求
- **结构**：所有页面 `{% extends "base.html" %}`，导航只在 `base.html` 维护
- **交互**：表单提交用 `fetch()` 调 `/api/*`，保持现有 API 契约

## 品牌方向

- **气质**：专注、克制、备考工具感（非 SaaS 营销页）
- **主色**：深蓝 `#1e3a5f` 或墨绿 `#1a4d3e`（二选一，全站统一）
- **字体**：标题 `Noto Serif SC` 或 `Source Han Serif`；正文 `system-ui` / `PingFang SC`
- **禁止**：紫粉渐变 Hero、全站 Inter、icon 方块三列功能卡、过度圆角堆叠卡片

## 页面要点

| 页面 | 优化重点 |
|------|----------|
| `index.html` | 进度卡片信息层级、预警状态醒目但不刺眼 |
| `subjects.html` | 表格可读性、空状态、表单对齐 |
| `plans.html` | 计划树改为可读列表/折叠树，避免裸 JSON pre |
| `punch.html` | 科目名显示（非仅 ID）、今日记录卡片化 |
| `progress.html` | 完成率进度条、科目对比表 |
| `stats.html` | 字符画图表容器、打卡率数字突出 |
| `data.html` | 备份/导出操作区危险色区分（恢复按钮） |

## CSS 变量（写入 style.css）

```css
:root {
  --color-primary: #1e3a5f;
  --color-primary-hover: #152a45;
  --color-surface: #f8f9fb;
  --color-card: #ffffff;
  --color-text: #1a1a1a;
  --color-text-muted: #6b7280;
  --color-danger: #b42318;
  --color-success: #067647;
  --radius-md: 12px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,.08);
}
```

## 工作流程

1. 先读 `hallmark`：audit 目标模板 → 按 punch list 改
2. 再读 `effective-ui-design`：对比度、间距 8pt、表单 label、按钮层级
3. 读 `awesome-cursorrules-ui`：Toss 设计系统 + Jinja2/Bootstrap 规则（`.cursor/rules/` 自动挂载）
4. 最后按本 skill 检查：是否破坏 Jinja2 变量、API 路径、Bootstrap 类名一致性

## 验收清单

- [ ] 移动端导航可折叠（Bootstrap navbar-toggler）
- [ ] 表格小屏不横向溢出（`table-responsive`）
- [ ] 空数据有友好提示，非空白
- [ ] 主按钮一种强调色，危险操作用 `btn-outline-danger`
- [ ] 未删除现有 `{% for %}` 与 `fetch` 逻辑
