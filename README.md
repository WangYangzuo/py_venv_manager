# Python Virtual Environment Manager

一个基于 PyQt6 的图形化 Python 虚拟环境管理工具，让您轻松管理多个 Python 虚拟环境。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 功能特性

- 🎯 **多 Python 版本管理**: 支持添加和管理多个 Python 解释器版本
- 📁 **虚拟环境管理**: 可视化浏览、创建和删除虚拟环境
- 🚀 **一键启动**: 快速激活并启动虚拟环境的命令行窗口
- 📦 **依赖查看**: 查看已安装的 Python 包，支持模糊搜索
- 🔧 **Jupyter 内核集成**: 自动为虚拟环境创建和注册 Jupyter Kernel
- 💾 **配置持久化**: 自动保存设置，下次启动时恢复
- 🎨 **现代化界面**: 清爽的 UI 设计，良好的用户体验


## 🚀 快速开始

### 前置要求

- Python 3.8 或更高版本
- PyQt6

### 安装方法

#### 方法一：从源码运行

1. 克隆仓库
```bash
git clone https://github.com/yourusername/venv-manager.git
cd venv-manager
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行应用
```bash
python run.py
```

#### 方法二：使用 pip 安装（开发模式）

```bash
git clone https://github.com/yourusername/venv-manager.git
cd venv-manager
pip install -e .
venv-manager
```

## 📖 使用指南

### 1. 添加 Python 版本

1. 点击左侧面板的 **"添加 Python"** 按钮
2. 选择 Python 解释器可执行文件（如 `python.exe`）
3. 程序会自动检测并显示版本信息

### 2. 设置虚拟环境储存文件夹

1. 在左侧面板点击 **"浏览..."** 选择文件夹
2. 点击 **"设置为此文件夹"** 确认
3. 所有新创建的虚拟环境将保存在此目录下

### 3. 创建虚拟环境

1. 点击绿色的 **"➕ 创建新虚拟环境"** 按钮
2. 选择 Python 版本
3. 输入环境名称
4. （可选）勾选"为此环境制作 ipykernel"以支持 Jupyter
5. 点击 **"创建"** 开始创建

### 4. 管理虚拟环境

在右侧环境列表中选择一个环境后，可以使用以下功能：

- **🚀 启动命令窗口**: 打开已激活该环境的终端
- **📦 已安装依赖**: 查看环境中安装的所有 Python 包
- **🗑️ 删除环境**: 永久删除选中的虚拟环境

### 5. 查看已安装包

1. 选择一个虚拟环境
2. 点击 **"📦 已安装依赖"**
3. 在弹出的窗口中可以：
   - 查看所有已安装的包及其版本
   - 使用搜索框进行模糊搜索

### 代码结构说明

- **core/**: 包含核心业务逻辑
  - `threads.py`: 异步线程类，处理耗时操作
  - `environment.py`: 环境管理功能封装
  
- **ui/**: 包含所有用户界面组件
  - `main_window.py`: 主应用程序窗口
  - `dialogs.py`: 各种对话框组件
  - `packages_dialog.py`: 包列表显示对话框
  
- **utils/**: 工具模块
  - `config.py`: 配置文件读写管理

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - 优秀的 Python GUI 框架
- 所有贡献者和使用者

## 📮 联系方式

wyzv5wd@gmail.com

如有问题或建议，请提交 Issue 或联系维护者。

---

