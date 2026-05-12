# CTMS STAT — 临床研究统计编程项目管理系统

## 系统简介

CTMS STAT 是一个面向临床研究统计编程团队的项目管理系统，按 CDISC 标准（SDTMIG 3.4 / ADaMIG 1.3）构建任务体系。

### 核心功能

- **任务管理**：四级分类（文档撰写 / SDTM / ADaM / TFL），细化到具体 domain，支持 QC 审核流程
- **工时记录**：按天记录每项任务的工时，自动生成周报汇总和柱状图
- **权限控制**：四级角色（SP 编程员 / SA 统计师 / LSP 编程Leader / Admin 管理员），数据按 rank 隔离
- **角色配置化**：Admin 面板可自由增删角色，rank 值决定权限范围
- **文件管理**（开发中）：SAS/R 程序及输出文件的版本管理
- **管理看板**（开发中）：团队工作量统计、项目进度图表

---

## 环境要求

| 依赖 | 最低版本 |
|---|---|
| Python | 3.10+ |
| pip | 最新版 |

---

## 安装与启动

### 1. 克隆仓库

```bash
git clone https://github.com/kevinget-svg/CTMS-prog.git
cd CTMS-prog
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动应用

```bash
streamlit run app.py
```

浏览器访问：**http://localhost:8501**

> 端口被占用时可指定：`streamlit run app.py --server.port=8502`

### 5. 首次启动

系统会自动：
- 创建 SQLite 数据库（`data/ctms.db`）
- 注入演示数据（4 个用户、2 个项目、20+ 个任务、13 条工时记录）

---

## 测试账号

| 账号 | 密码 | 角色 | 职责 | 权限范围 |
|---|---|---|---|---|
| `admin` | `admin123` | 系统管理员 | 系统配置与维护 | 全部功能 |
| `lsp_wang` | `lsp123` | LSP 编程Leader | 布置任务、管理进度、审阅文件、数据归档 | 项目内全部任务和工时 |
| `sa_zhang` | `sa123` | SA 统计师 | 撰写SAP、审阅ADaM spec、审阅TFL结果 | 自己的 + 被分配审阅的任务 |
| `sp_li` | `sp123` | SP 编程员 | SAS/R编程、撰写spec、生成数据集和TFL | 仅自己的任务和工时 |

> 首次登录后请在侧边栏 **Change Password** 中修改密码。

---

## 角色与权限说明

| 角色 | Rank | 可见任务 | 可见工时 | 创建任务 | QC审阅 | 管理后台 |
|---|---|---|---|---|---|---|
| Admin | 40 | 全部 | 全部 | 是 | 是 | 是 |
| LSP | 35 | 本项目的全部 | 本项目的全部 | 是 | 是 | 否 |
| SA | 25 | 自己的 + 被分配审阅的 | 自己的 | 否 | 是 | 否 |
| SP | 10 | 仅自己的 | 自己的 | 否 | 否 | 否 |

> Rank 为数值，越大权限越高。Admin 面板 → Roles 标签可自定义角色和 rank 值。

---

## 任务类型体系（CDISC 标准）

任务创建时采用两级级联选择：

### 一级分类

| 分类 | 说明 |
|---|---|
| **文档撰写** | 各类研究文档的撰写与审阅 |
| **SDTM** | SDTM 数据集编程（SDTMIG 3.4） |
| **ADaM** | ADaM 数据集编程（ADaMIG 1.3） |
| **TFL** | 表格、图形和列表输出 |

### 二级子类型

**文档撰写**：`aCRF`、`SDTM Spec`、`ADaM Spec`、`define.xml`、`SDRG`、`ADRG`、`TFL Shell`

**SDTM（36 个 domain）**：`DM`、`AE`、`CM`、`LB`、`VS`、`MH`、`EG`、`EX`、`EC`、`DS`、`DV`、`IE`、`SV`、`SE`、`QS`、`DA`、`MB`、`MS`、`PC`、`PP`、`PR`、`RS`、`TU`、`TR`、`CO`、`DD`、`DI`、`FA`、`HO`、`PE`、`RE`、`SS`、`TD`、`TI`、`TS`、`TV`

**ADaM（14 个 domain）**：`ADSL`、`ADAE`、`ADCM`、`ADLB`、`ADVS`、`ADMH`、`ADEG`、`ADEX`、`ADTTE`、`ADQS`、`ADIS`、`ADRS`、`ADPC`、`ADPP`

**TFL（4 个子类）**：`T-POP`（人群分布）、`T-BASE`（基线特征）、`T-EFF`（疗效分析）、`T-SAFE`（安全性分析）

---

## 功能测试指南

---

### 一、基础功能（所有角色通用）

#### 1.1 登录与修改密码

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 打开 http://localhost:8501 | 显示 CTMS STAT 登录页面 |
| 2 | 输入错误密码，点击 Login | 提示 "Invalid username or password." |
| 3 | 用 `admin / admin123` 登录 | 进入 My Dashboard 页面 |
| 4 | 点击左侧栏 Change Password | 展开修改密码表单 |
| 5 | 输入当前密码 + 新密码（至少 6 位）+ 确认密码，提交 | 提示 "Password changed successfully." |
| 6 | 登出后用新密码重新登录 | 登录成功 |
| 7 | 将密码改回 `admin123` | 恢复测试账号 |

#### 1.2 侧边栏

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 查看侧边栏顶部 | 显示 "Welcome, Admin" 及角色名 |
| 2 | 切换 Active Project 下拉框 | 可筛选项目（ABC-123-001 / DEF-456-002） |
| 3 | 点击 Logout | 返回登录页 |

---

### 二、Admin 角色测试

> 登录 `admin / admin123`

#### 2.1 Admin 面板 — 用户管理

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 点击左侧 **Admin** 菜单 | 进入 Admin Panel |
| 2 | 查看 Users 标签的用户列表 | 显示 4 个用户（admin, lsp_wang, sa_zhang, sp_li） |
| 3 | 点击 Create New User | 展开新建表单 |
| 4 | 输入 Username: `testuser`，Password: `test123`，Full Name: `Test User`，选择角色 SP | |
| 5 | 点击 Create User | 提示创建成功 |
| 6 | 在下拉框选择 Test User，切换角色为 SA，点击 Update Role | 提示 "Role updated." |
| 7 | 点击 Deactivate User | 提示该用户已停用 |
| 8 | 用 `testuser / test123` 登录 | 无法登录（账号已停用） |
| 9 | 回到 admin，选择 Test User，点击 Reactivate User | 提示恢复成功 |
| 10 | 再次用 `testuser / test123` 登录 | 登录成功，角色为 SA |

#### 2.2 Admin 面板 — 项目管理

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 切换到 **Projects** 标签 | 显示 2 个演示项目 |
| 2 | 点击 Create New Project | 展开表单 |
| 3 | 输入 Protocol: `XYZ-789-003`，Study: `Phase I Oncology Study`，Sponsor: `XYZ Pharma` | |
| 4 | 点击 Create Project | 项目创建成功 |
| 5 | 展开新项目，点击 Add Member 添加 testuser | 成员列表出现 Test User |
| 6 | 修改状态为 On Hold，点击 Update Status | 状态变更 |

#### 2.3 Admin 面板 — 角色管理

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 切换到 **Roles** 标签 | 显示 4 个默认角色（SP/SA/LSP/Admin）及其 rank |
| 2 | 点击 Create New Role | 展开表单 |
| 3 | 输入 Name: `DM Programmer`，Rank: `15`，Description: `数据管理员` | |
| 4 | 点击 Create Role | 角色创建成功，rank 15 介于 SP(10) 和 SA(25) 之间 |
| 5 | 选中 DM Programmer，修改 Description 后点击 Save Changes | 更新成功 |
| 6 | 点击 Delete Role | 删除成功（该角色无关联用户时才能删除） |

> **Rank 说明**：10=SP，25=SA，35=LSP，40=Admin。rank 越大权限越高。自定义角色按 rank 值获得对应权限。

#### 2.4 Admin 面板 — 数据库

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 切换到 **Database** 标签 | 显示每张表的行数 |
| 2 | 点击 Re-initialize Seed Data | 重置为初始演示数据（谨慎操作） |

---

### 三、SP 编程员角色测试

> 登出 admin，登录 `sp_li / sp123`

#### 3.1 My Dashboard（个人看板）

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 查看顶部 4 个 KPI 彩色卡片 | 大字体数字，蓝色 (In Progress)、橙色 (In QC)、红色 (Overdue)、绿色 (本周工时) |
| 2 | 查看 My Projects | 显示项目卡片及完成进度 |
| 3 | 查看 Active Tasks | 仅显示分配给 sp_li 的任务 |
| 4 | 查看 Task Status 饼图 | 显示任务状态分布 |
| 5 | 查看 Hours This Week 柱状图 | 显示每日工时，含演示数据 |
| 6 | 查看 Recent Time Entries | 显示最近工时记录 |

#### 3.2 My Tasks（任务管理）

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 点击 **My Tasks** | 显示 sp_li 被分配的任务（含 SDTM/ADaM/TFL/文档撰写类） |
| 2 | 使用 Category 筛选 "SDTM" | 仅显示 SDTM 相关任务（如 DM、AE、LB 等 domain） |
| 3 | 使用 Status 筛选 "In Progress" | 仅显示进行中任务 |
| 4 | 点击任务上的 **→ In Progress** 按钮 | 状态变为 In Progress |
| 5 | 继续点击 **→ Awaiting QC** | 任务进入待审核 |
| 6 | 再点 **→ QC In Review** | 报错：非法状态转换 |
| 7 | 点击 **View** | 展开详情，显示 Category / Subtype / 描述等 |
| 8 | 点击 **Close Detail** | 关闭详情 |

> SP 看不到 **Create New Task** 按钮（仅 LSP/Admin 可见）。

#### 3.3 Timesheet（工时记录）

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 点击 **Timesheet** | 显示工时录入表单 |
| 2 | 选择 Date（默认今天） | |
| 3 | 选择 Task（从自己的任务中选一个） | |
| 4 | 输入描述："编写 xx 域 SAS 程序" | |
| 5 | Hours 设为 4.0 | |
| 6 | 点击 **Save Entry** | 提示 "Logged 4.0h on YYYY-MM-DD." |
| 7 | 查看 Weekly View | 本周工时统计更新，显示总工时、天数、日均 |
| 8 | 切换 Week 为 "Last Week" | 显示上周演示数据 |
| 9 | 尝试输入 Hours = 0 或 25 | 提示校验错误 |

#### 3.4 权限隔离验证

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 查看左侧菜单 | 没有 Admin、Team Dashboard 入口 |
| 2 | My Tasks 中 | 仅看到 `assigned_to = sp_li` 的任务 |
| 3 | Timesheet 中 | 仅能记录自己任务的工时 |

---

### 四、SA 统计师角色测试

> 登出，登录 `sa_zhang / sa123`

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 查看 My Dashboard | KPI 数据反映 sa_zhang 的个人任务 |
| 2 | 进入 My Tasks | 显示自己的任务 + 被分配为 reviewer 的任务（即 sp_li 提交审核的） |
| 3 | 确认能看到 sp_li 的任务 | SA 的 rank 25 具备 Reviewer 权限 |
| 4 | 对 Awaiting QC 的任务点击 **→ QC In Review** | SA 可以执行 QC 流转 |
| 5 | 左侧菜单 | 没有 Create Task 入口（仅 LSP/Admin 可创建） |
| 6 | 左侧菜单 | 有 QC Review 入口（Phase 2 开发中） |

---

### 五、LSP 编程Leader 角色测试

> 登出，登录 `lsp_wang / lsp123`

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 查看左侧菜单 | 有 Team Dashboard 入口 |
| 2 | 进入 My Tasks | 能看到项目内所有成员的任务 |
| 3 | 点击 Create New Task | 展开创建表单 |
| 4 | Task Category 选择 **SDTM** | Task Subtype 自动联动显示所有 SDTM domain |
| 5 | 切换 Category 为 **ADaM** | Subtype 自动切换为 ADaM domain 列表 |
| 6 | 切换 Category 为 **TFL** | Subtype 显示 T-POP / T-BASE / T-EFF / T-SAFE |
| 7 | 选择 Subtype: `DM — 人口学` | |
| 8 | Assign To 选 sp_li，Reviewer 选 sa_zhang，Priority 选 High | |
| 9 | 填写 Title、Due Date、Estimated Hours | |
| 10 | 点击 Create Task | 提示创建成功 |
| 11 | 用 sp_li 登录验证 | 新任务出现在 sp_li 的任务列表中 |
| 12 | 登录 lsp_wang，查看 My Dashboard | KPI 为项目全局数据 |

---

## 状态机说明

任务在以下状态之间流转，由 `services/task_service.py` 强制执行：

```
                    ┌─ Revision Needed ←──┐
                    ↓                      │
Not Started → In Progress → Awaiting QC → QC In Review → Complete
```

- **SP**：Not Started → In Progress → Awaiting QC
- **SA / LSP**：Awaiting QC → QC In Review → Complete 或 Revision Needed
- 不合法的流转会被拦截并提示错误

---

## 数据库说明

- 数据库文件：`data/ctms.db`（SQLite，WAL 模式）
- 首次启动自动创建表并注入演示数据
- 代码更新后启动会自动执行 schema migration（无需手动删库）
- 要重置数据：Admin → Database 标签 → Re-initialize Seed Data
- 或手动删除 `data/ctms.db`，重启应用

---

## 常见问题

**Q: 启动报 "port 8501 is not available"？**
A: 指定其他端口：`streamlit run app.py --server.port=8502`

**Q: Windows PowerShell 无法激活虚拟环境？**
A: 改用 CMD（`Win+R` → `cmd`），或在 PowerShell 以管理员运行：`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Q: 提示 "git 无法识别"？**
A: 安装 Git（https://git-scm.com/download/win），或直接下载 GitHub 页面 ZIP 包解压。

**Q: 代码更新后报 "no such column"？**
A: 系统已自动迁移 schema，若仍报错，删除 `data/ctms.db` 重启即可。

**Q: 登录后看不到任何任务？**
A: SP 和 SA 仅看到分配给自己的任务。用 LSP 或 Admin 登录创���任务。

**Q: 如何添加自定义角色？**
A: Admin → Roles → Create New Role。rank 值决定权限：10=SP 级，25=SA 级，35=LSP 级，40=Admin 级。

**Q: 如何重置演示数据？**
A: Admin → Database → Re-initialize Seed Data。

---

## 技术栈

| 组件 | 技术 |
|---|---|
| 前端框架 | Streamlit |
| 数据库 | SQLite (WAL mode) |
| 密码加密 | bcrypt |
| 图表 | Plotly |
| 数据处理 | pandas |
