# ModelScope Manager

一个简洁美观的 ModelScope 模型管理工具，支持多账号切换、模型收藏与自定义模型管理。

## ✨ 功能特性

### 1. 模型浏览与管理
- **实时搜索**：支持按模型 ID 快速过滤。
- **自定义模型**：支持添加 API 列表中未包含的自定义模型 ID。
- **合并显示**：自动去重合并 API 模型和自定义模型。
- **快捷操作**：
  - 📋 一键复制模型 ID
  - ⭐ 添加/取消收藏
  - 🔍 仅查看收藏模型

### 2. 多账号管理
- **账号切换**：支持添加多个 API Key 账号并一键切换。
- **默认账号**：自动读取 `.env` 中的 `API_KEY` 作为默认账号（不可删除）。
- **安全存储**：新添加的 API Key 以 `.env` 文件形式存储，不硬编码。
- **快捷复制**：一键复制当前账号的 API Key。

### 3. 额度监控
- **用户额度**：显示当前账号的请求限流状态（剩余/上限）。
- **模型额度**：支持针对特定模型检查剩余调用额度（Chat 接口）。

### 4. 现代化 GUI
- **标签页设计**：清晰分离模型列表与账号管理。
- **状态记忆**：自动保存窗口位置和大小。

## 🛠️ 安装与运行

推荐使用 [uv](https://github.com/astral-sh/uv) 进行环境管理。

### 1. 安装依赖

```bash
uv pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件（可选，也可以在 GUI 中添加）：

```env
API_KEY=your_default_api_key
```

### 3. 启动应用

```bash
python gui/main.py
```

## � 打包发布

本项目支持使用 `PyInstaller` 跨平台打包 (macOS / Windows / Linux)。

### 1. 确保安装 PyInstaller

```bash
uv pip install pyinstaller
```

### 2. 执行打包

使用项目根目录下的 `build.spec` 配置文件进行打包：

```bash
# 清理旧构建并打包
pyinstaller build.spec --clean --noconfirm
```

打包完成后，可执行文件将生成在 `dist/` 目录下：
- **macOS**: `dist/ModelScope_Manager.app`
- **Windows**: `dist/ModelScope_Manager.exe` (或文件夹)

### 3. 数据存储说明
打包后的应用会自动将配置文件存储在用户主目录，确保跨平台读写权限：

**macOS / Linux:**
- **配置文件**: `~/.modelscope_manager/config.toml`
- **环境变量**: `~/.modelscope_manager/.env`

**Windows:**
- **配置文件**: `%USERPROFILE%\.modelscope_manager\config.toml`
- **环境变量**: `%USERPROFILE%\.modelscope_manager\.env`

## �📂 项目结构

```
gui/
├── main.py              # 程序入口
├── ui/                  # UI 界面定义
│   ├── ui_mainwindow.py
│   ├── ui_model_list.py
│   └── ui_account_manage.py
├── func/                # 业务逻辑实现
│   ├── func_mainwindow.py
│   ├── func_model_list.py
│   └── func_account_manage.py
├── utils/               # 工具类
│   ├── app_paths.py     # 统一路径管理
│   ├── config_manager.py
│   └── workers.py
└── icon/                # 资源图标
```
