# CTMS STAT — 临床研究统计编程项目管理系统

## 系统简介

CTMS STAT 是一个面向临床研究统计编程团队的项目管理系统，支持以下功能：

- **任务管理**：TFL（Table/Figure/Listing）任务分配、状态流转、QC 审核流程
- **工时记录**：按天记录每项任务的工时，自动生成周报汇总
- **权限控制**：四级角色（Programmer / Reviewer / Manager / Admin），数据按角色隔离
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
source venv/bin/activate      # macOS / Linux
# 或
venv\Scripts\activate         # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动应用

```bash
streamlit run app.py
```

启动后在浏览器中访问：**http://localhost:8501**

> 如果 8501 端口被占用，可以指定其他端口：
> ```bash
> streamlit run app.py --server.port=8502
> ```

### 5. 首次启动

系统会自动：
- 创建 SQLite 数据库（`data/ctms.db`）
- 注入演示数据（4 个用户、1 个项目、4 个任务、5 条工时记录）

---

## 测试账号

| 账号 | 密码 | 角色 | 可见权限 |
|---|---|---|---|
| `admin` | `admin123` | 系统管理员 | 全部功能，含用户/角色/项目管理 |
| `manager` | `manager123` | 项目经理 | 项目内全部任务和工时，可创建任务 |
| `programmer1` | `dev123` | 统计程序员 | 仅自己的任务和工时 |
| `reviewer1` | `reviewer123` | QC 审核员 | 自己的任务 + 被分配审核的任务 |

> 首次登录后，建议在左侧边栏 → **Change Password** 中修改密码。

---

## 功能测试指南

以下按角色分别列出测试步骤，建议按顺序逐一验证。

---

### 一、基础功能（所有角色通用）

#### 1.1 登录与修改密码

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 打开 http://localhost:8501 | 显示登录页面 |
| 2 | 输入错误密码，点击 Login | 提示 "Invalid username or password." |
| 3 | 用 `admin / admin123` 登录 | 进入 My Dashboard 页面 |
| 4 | 点击左侧栏 Change Password | 展开修改密码表单 |
| 5 | 输入当前密码 + 新密码（至少6位）+ 确认密码，提交 | 提示修改成功 |
| 6 | 登出后用新密码重新登录 | 登录成功 |
| 7 | 将密码改回 `admin123` | 恢复测试账号 |

#### 1.2 侧边栏

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 查看侧边栏顶部 | 显示 "Welcome, System Admin"，Role: Admin |
| 2 | 切换 Active Project 下拉框 | 可筛选项目（目前仅有 1 个演示项目） |
| 3 | 点击 Logout | 返回登录页 |

---

### 二、Admin 角色测试

> 登录账号：`admin / admin123`

#### 2.1 Admin 面板 — 用户管理

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 点击左侧 **Admin** 菜单 | 进入 Admin Panel，默认选中 Users 标签 |
| 2 | 查看用户列表 | 显示 4 个用户，含 ID、用户名、全名、角色、状态 |
| 3 | 点击 Create New User | 展开新建用户表单 |
| 4 | 输入 Username: `testuser`，Password: `test123`，全名: `Test User`，选择角色 Programmer | |
| 5 | 点击 Create User | 提示创建成功，用户列表出现新用户 |
| 6 | 在下方下拉框选择 Test User，切换角色为 Manager，点击 Update Role | 提示 "Role updated." |
| 7 | 点击 Deactivate User | 提示 "User 'Test User' deactivated." |
| 8 | 用 `testuser / test123` 登录 | 无法登录（已停用） |
| 9 | 回到 admin，选择 Test User，点击 Reactivate User | 提示恢复成功 |
| 10 | 再次用 `testuser / test123` 登录 | 登录成功，角色为 Manager |

#### 2.2 Admin 面板 — 项目管理

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 切换到 **Projects** 标签 | 显示现有项目列表 |
| 2 | 点击 Create New Project | 展开表单 |
| 3 | 输入 Protocol: `XYZ-456-002`，Study: `Phase II Diabetes Study`，Sponsor: `XYZ Pharma` | |
| 4 | 点击 Create Project | 项目创建成功 |
| 5 | 展开新项目，点击 Add Member 添加 testuser | 成员列表中出现 Test User |
| 6 | 修改项目状态为 On Hold，点击 Update Status | 状态变更 |

#### 2.3 Admin 面板 — 角色管理

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 切换到 **Roles** 标签 | 显示 4 个默认角色及其 rank 值 |
| 2 | 点击 Create New Role | 展开表单 |
| 3 | 输入 Name: `Lead Programmer`，Rank: `15`，Description: `高级统计程序员` | |
| 4 | 点击 Create Role | 角色创建成功 |
| 5 | 在 Edit/Delete Role 下拉框中选择 Lead Programmer | |
| 6 | 修改 Description，点击 Save Changes | 更新成功 |
| 7 | 点击 Delete Role | 删除成功（该角色无用户） |

> **Rank 说明**：10=Programmer, 20=Reviewer, 30=Manager, 40=Admin。Rank 值越高权限越大。

#### 2.4 Admin 面板 — 数据库信息

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 切换到 **Database** 标签 | 显示每个表的行数 |
| 2 | 点击 Re-initialize Seed Data | 警告：会重置演示数据 |

---

### 三、Programmer 角色测试

> 登出 admin，登录 `programmer1 / dev123`

#### 3.1 My Dashboard（个人看板）

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 查看顶部 4 个 KPI 卡片 | 显示 In Progress 数量、In QC 数量、Overdue 数量、本周工时 |
| 2 | 查看 My Projects 区域 | 显示项目卡片及任务完成进度条 |
| 3 | 查看 Active Tasks 列表 | 仅显示自己的任务 |
| 4 | 查看 Task Status 饼图 | 显示任务状态分布 |
| 5 | 查看 Hours This Week 柱状图 | 显示每日工时 |
| 6 | 查看 Recent Time Entries | 显示最近工时记录 |

#### 3.2 My Tasks（任务管理）

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 点击 **My Tasks** 页面 | 仅显示分配给 programmer1 的 4 个任务 |
| 2 | 使用 Status Filter 筛选 "In Progress" | 仅显示 1 个任务 |
| 3 | 使用 Priority Filter 筛选 "High" | 仅显示高优先级任务 |
| 4 | 点击某个任务下的 **→ In Progress** 按钮 | 状态更新 |
| 5 | 继续点击 **→ Awaiting QC** | 任务进入待审核状态 |
| 6 | 现在再点 **→ QC In Review** | 报错：不能从 Awaiting QC 直接转换到此状态（状态机控制） |
| 7 | 点击 **View** 按钮 | 展开任务详情 |
| 8 | 点击 **Close Detail** | 关闭详情 |

> **状态流转规则**：
> `Not Started → In Progress → Awaiting QC → QC In Review → Complete`
> `QC In Review → Revision Needed → In Progress`

> programmer1 看不到 **Create New Task** 按钮（仅 Manager/Admin 可见）

#### 3.3 Timesheet（工时记录）

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 点击 **Timesheet** 页面 | 显示工时录入表单 |
| 2 | 选择 Date（默认今天） | |
| 3 | 选择 Task（从自己的任务中选） | |
| 4 | 输入描述："编写了 SAS 程序" | |
| 5 | Hours 设为 4.0 | |
| 6 | 点击 **Save Entry** | 提示 "Logged 4.0h on YYYY-MM-DD." |
| 7 | 查看 Weekly View 区域 | 本周工时统计更新 |
| 8 | 切换 Week 下拉框为 "Last Week" | 显示上周的演示数据 |

> 不能在 Hours 输入 0 或大于 24 的值，系统会提示错误。

#### 3.4 权限隔离验证

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 查看左侧菜单栏 | 没有 Admin 入口 |
| 2 | 在 My Tasks 中 | 只能看到 `assigned_to = programmer1` 的任务 |
| 3 | 在 Timesheet 中 | 工时记录仅关联自己的任务 |

---

### 四、Reviewer 角色测试

> 登出，登录 `reviewer1 / reviewer123`

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 查看 My Tasks 页面 | 显示自己的任务 + 被分配为 reviewer 的任务 |
| 2 | 在任务列表中确认 | 能看到 programmer1 的任务（reviewer1 被设为其 Reviewer） |
| 3 | 左侧菜单 | 有 QC Review 入口（功能在 Phase 2 开发中） |

---

### 五、Manager 角色测试

> 登出，登录 `manager / manager123`

| 步骤 | 操作 | 预期结果 |
|---|---|---|
| 1 | 查看左侧菜单 | 有 Team Dashboard 入口 |
| 2 | 进入 My Tasks | 能看到项目中所有成员的任务 |
| 3 | 点击 Create New Task | 可为任意项目成员创建任务 |
| 4 | 在 Assign To 中选择 programmer1，Reviewer 选 reviewer1 | |
| 5 | 填入 Title、Type、Priority、Due Date | |
| 6 | 点击 Create Task | 任务创建成功 |
| 7 | 查看 My Dashboard | KPI 数据反映项目整体情况 |

---

## 状态机说明

任务在以下状态之间流转，流转由 `services/task_service.py` 强制执行：

```
                    ┌─ Revision Needed ←──┐
                    ↓                      │
Not Started → In Progress → Awaiting QC → QC In Review → Complete
```

- **Programmer** 可以从 Not Started → In Progress，再从 In Progress → Awaiting QC
- **Reviewer** 从 Awaiting QC → QC In Review，然后决定 Complete 或 Revision Needed
- 不合法的流转会被拦截并提示错误

---

## 数据库说明

- 数据库文件：`data/ctms.db`（SQLite，WAL 模式）
- 首次启动自动创建，含演示数据
- 要重置数据：删除 `data/ctms.db`，重新启动应用
- 或在 Admin → Database 标签中点击 Re-initialize Seed Data

---

## 常见问题

**Q: 启动报 "port 8501 is not available"？**
A: 指定其他端口 `streamlit run app.py --server.port=8502`

**Q: 登录后看不到任何任务？**
A: 检查是否为 Programmer 账号，该账号创建时可能未被分配任务。用 manager 或 admin 登录，给该用户分配任务即可。

**Q: 如何重置演示数据？**
A: Admin 登录 → Admin Panel → Database 标签 → 点击 "Re-initialize Seed Data"

**Q: 如何添加新角色？**
A: Admin 登录 → Admin Panel → Roles 标签 → Create New Role，设置 Name 和 Rank 值。

---

## 技术栈

| 组件 | 技术 |
|---|---|
| 前端框架 | Streamlit |
| 数据库 | SQLite (WAL mode) |
| 密码加密 | bcrypt |
| 图表 | Plotly |
| 数据处理 | pandas |
