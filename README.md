# 营销长图文转化优化 · Conversion Copy Optimizer

基于基线方法论与优秀案例，诊断**已有的营销转化型长图文**（软文、种草文、投放落地页文案），输出带原文证据、分优先级的优化建议和可直接替换的改写示例。

> 方法论支持 @互联网营销袁超

## 它能做什么

- 判断内容行业与置信度、确认营销目标（留资 / 下单 / 认知等）
- 逐项对标检查：标题、钩子、证据链、信任背书、CTA、合规红线等通用检查点
- 教育 / 知识付费内容追加 E1–E9 专项检查（搜索型 vs 推荐型入口、信任配比、需求缺口、钩子成本、成果数字可信度等）
- 带评论区输入时，检查前排定调、作者回复、异议化解与正文—评论呼应（N21）
- 战略层体检 + 分级建议（P0/P1/P2）+ Before/After 改写示例
- 云端增量：内置公开 JSON 源，方法论更新后用户下次运行自动生效，无需重装

**不做**：从零创作、纯润色/缩写/翻译、单纯起标题、SEO 改写、消耗/CTR 类数据分析。

## 安装

### Codex（推荐）

```bash
npx skills@latest add yuanchao-cn/conversion-content-optimizer
```

安装后重启 Codex。在对话里直接描述任务即可按 description 自动触发，例如：

- `帮我看看这篇种草文为什么转化差，给出优化建议`
- `对照优秀案例检查这篇长图文的 CTA 和证据链`
- `判断这篇内容属于什么行业，营销目标应该定成什么`

### 手动安装（其他支持 SKILL.md 的 Agent）

把本仓库克隆或下载到对应技能目录，例如 Codex：

```bash
git clone https://github.com/yuanchao-cn/conversion-content-optimizer.git ~/.codex/skills/conversion-content-optimizer
```

Claude Code / Cursor / Gemini CLI / Windsurf 等支持 Agent Skills 的工具，放到各自 `skills/` 目录后重启即可。

## 目录结构

```
conversion-content-optimizer/
├── SKILL.md                              # 入口：frontmatter + 六步工作流
├── references/                           # 按需加载的方法论
│   ├── methodology.md                    # 四步心理链路 + 五层骨架
│   ├── industry-judgment.md              # 行业信号与置信度
│   ├── goal-confirmation.md              # 营销目标分类与 CTA 映射
│   ├── topic-and-headline.md / craft-and-writing.md
│   ├── content-strategy.md               # 战略层体检
│   ├── knowhow-checklist.md              # 通用对标检查（N1–N20 + 评论区 N21）
│   ├── emerging-knowhow.md               # 新观点（第十一至十三节）
│   ├── education-content.md              # 教育行业补充（E1–E9）
│   ├── case-library-index.md / case-template.md
│   └── methodology-refresh-2026.md        # 2026 方法论刷新（N22–N29，冲突时优先）
├── scripts/fetch_knowledge.py            # 云端增量拉取（标准库，带降级）
└── templates/optimization-report-template.md
```

## 云端增量

`scripts/fetch_knowledge.py` 内置公开 JSON URL，安装后零配置自动拉取。维护者更新 JSON 内容并递增 `version`/`updated_at`，所有用户下次运行自动生效。

- 本机可选覆盖：`~/.workbuddy/conversion-content-optimizer/knowledge-source.json`（合法 `url` 覆盖内置源；`{"enabled": false}` 禁用）
- 网络失败 / JSON 不合法 / 超 2MB → 自动 fallback 到包内基线，不中断诊断

## 兼容性说明

本技能最初为 WorkBuddy 技能市场开发（当前版本 v1.9.5），核心是开放的 Agent Skills（SKILL.md）格式。在非 WorkBuddy 环境：

- frontmatter 中的 `display_name` / `description_zh` / `description_en` / `examples_zh` / `examples_en` 是 WorkBuddy 市场展示字段，标准 Agent Skills 仅需 `name` + `description`，其余字段通常被忽略，不影响触发。
- SKILL.md 中以 `@references/xxx.md` 形式引用补充文档（WorkBuddy 规范）。若所用 Agent 不按该语法自动加载，直接读取 `references/` 下对应文件即可。
- 生成的报告末尾会带一行不醒目的小字「方法论支持 @互联网营销袁超」，请保留。

### 豆包工作（v1.9.5 起原生适配）

豆包开放平台对包结构和字段有独立要求，本仓库源码**不直接作为豆包上传包**，请使用随版本发布的豆包专用包：

- 包文件：`conversion-content-optimizer-doubao-v1.9.5.zip`（SKILL.md 位于 ZIP 根目录）
- 与仓库源码的差异：frontmatter 仅保留 `name` / `description` / `metadata`（display_name、display_description、icon），正文的 `@references/xxx.md` 改为 Markdown 相对链接 `[xxx.md](references/xxx.md)`，并附 512×512 图标 `assets/icon.png`。
- 上传：豆包开放平台 → 技能列表 → 创建技能 → 上传该 ZIP；发布范围选「企业专属」（管理员审核）或「公开上架」（需企业资质认证 + 平台审核）。
- 公开上架需另备：评测报告（飞书云文档链接并对审核人开放）、5–10 条示例提示词。
- 豆包 description 上限 300 字符，当前 234，合规。

### 其他平台分发包

- `conversion-content-optimizer-platform-v1.9.5.zip`：WorkBuddy 技能市场包（根目录一层技能目录 + 顶层展示字段）。
- `conversion-content-optimizer-agent-skills-v1.9.5.zip`：标准 Agent Skills 通用包（根目录 SKILL.md，保留 @ 引用语法）。
- 构建脚本：`data/build_releases.py`（维护者本地使用，读取 SKILL.md 的 version 自动生成三份包，版本保持 v1.9.5）。

## 保密

本仓库只包含可公开的方法论与抽象规律，不含任何私有案例原文、品牌名、链接、金额或未授权内容。真实案例只留在维护者本地私有层，不进入本仓库与云端 JSON。

## 版本

v1.9.5
