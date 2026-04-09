import sys
import os
import re
import subprocess
import json
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
                             QLabel, QLineEdit, QComboBox, QCheckBox, QDialog,
                             QFormLayout, QMessageBox, QFileDialog, QTableWidget,
                             QTableWidgetItem, QHeaderView, QGroupBox, QSplitter,
                             QTextEdit, QProgressDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette


class CreateVenvThread(QThread):
    """在后台线程中创建虚拟环境"""
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)

    def __init__(self, python_path, env_path, make_kernel, kernel_name):
        super().__init__()
        self.python_path = python_path
        self.env_path = env_path
        self.make_kernel = make_kernel
        self.kernel_name = kernel_name

    def run(self):
        try:
            # 创建虚拟环境
            self.progress.emit(f"正在创建虚拟环境: {self.env_path}")
            result = subprocess.run(
                [self.python_path, "-m", "venv", self.env_path],
                capture_output=True,
                text=True,
                check=True
            )

            # 获取虚拟环境的 Python 路径
            if sys.platform == "win32":
                venv_python = os.path.join(self.env_path, "Scripts", "python.exe")
            else:
                venv_python = os.path.join(self.env_path, "bin", "python")

            # 升级 pip
            self.progress.emit("正在升级 pip...")
            subprocess.run(
                [venv_python, "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                check=True
            )

            # 安装 ipykernel
            if self.make_kernel:
                self.progress.emit("正在安装 ipykernel...")
                subprocess.run(
                    [venv_python, "-m", "pip", "install", "ipykernel"],
                    capture_output=True,
                    check=True
                )

                # 注册内核
                self.progress.emit(f"正在注册 Jupyter 内核: {self.kernel_name}")
                subprocess.run(
                    [venv_python, "-m", "ipykernel", "install", 
                     "--user", "--name", self.kernel_name, 
                     "--display-name", f"Python ({self.kernel_name})"],
                    capture_output=True,
                    check=True
                )

            self.finished.emit(True, "虚拟环境创建成功！")

        except subprocess.CalledProcessError as e:
            self.finished.emit(False, f"创建失败: {e.stderr}")
        except Exception as e:
            self.finished.emit(False, f"错误: {str(e)}")


class GetPackagesThread(QThread):
    """在后台线程中获取已安装包列表"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, env_path):
        super().__init__()
        self.env_path = env_path

    def run(self):
        try:
            if sys.platform == "win32":
                python_exe = os.path.join(self.env_path, "Scripts", "python.exe")
            else:
                python_exe = os.path.join(self.env_path, "bin", "python")

            result = subprocess.run(
                [python_exe, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )

            import json
            packages = json.loads(result.stdout)
            self.finished.emit(packages)

        except Exception as e:
            self.error.emit(str(e))


class CreateEnvDialog(QDialog):
    """创建虚拟环境对话框"""
    def __init__(self, parent=None, python_versions=None):
        super().__init__(parent)
        self.setWindowTitle("创建虚拟环境")
        self.setMinimumWidth(500)
        self.python_versions = python_versions or []
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        # Python 版本选择
        self.python_combo = QComboBox()
        for name, path in self.python_versions:
            self.python_combo.addItem(f"{name} ({path})", path)
        layout.addRow("Python 版本:", self.python_combo)

        # 基础路径选择
        base_path_layout = QHBoxLayout()
        self.base_path_edit = QLineEdit()
        self.base_path_edit.setPlaceholderText("选择虚拟环境储存文件夹...")
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_base_path)
        base_path_layout.addWidget(self.base_path_edit)
        base_path_layout.addWidget(browse_btn)
        layout.addRow("储存文件夹:", base_path_layout)

        # 环境名称
        self.env_name_edit = QLineEdit()
        self.env_name_edit.setPlaceholderText("myenv")
        layout.addRow("环境名称:", self.env_name_edit)

        # 完整路径预览
        self.full_path_label = QLabel("完整路径: ")
        self.full_path_label.setStyleSheet("color: gray;")
        layout.addRow("", self.full_path_label)

        # 连接信号更新完整路径
        self.base_path_edit.textChanged.connect(self.update_full_path)
        self.env_name_edit.textChanged.connect(self.update_full_path)

        # 制作 ipykernel
        self.kernel_checkbox = QCheckBox("为此环境制作 ipykernel")
        self.kernel_checkbox.stateChanged.connect(self.toggle_kernel_name)
        layout.addRow("", self.kernel_checkbox)

        # Kernel 名称
        self.kernel_name_edit = QLineEdit()
        self.kernel_name_edit.setPlaceholderText("myenv-kernel")
        self.kernel_name_edit.setEnabled(False)
        layout.addRow("Kernel 名称:", self.kernel_name_edit)

        # 按钮
        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton("创建")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.create_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.create_btn)
        layout.addRow("", btn_layout)

    def browse_base_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择虚拟环境储存文件夹")
        if path:
            self.base_path_edit.setText(path)

    def update_full_path(self):
        base = self.base_path_edit.text()
        name = self.env_name_edit.text()
        if base and name:
            full = os.path.join(base, name)
            self.full_path_label.setText(f"完整路径: {full}")
        else:
            self.full_path_label.setText("完整路径: ")

    def toggle_kernel_name(self, state):
        self.kernel_name_edit.setEnabled(state == Qt.CheckState.Checked.value)
        if state == Qt.CheckState.Checked.value:
            self.kernel_name_edit.setText(self.env_name_edit.text() + "-kernel")

    def get_data(self):
        return {
            'python_path': self.python_combo.currentData(),
            'base_path': self.base_path_edit.text(),
            'env_name': self.env_name_edit.text(),
            'make_kernel': self.kernel_checkbox.isChecked(),
            'kernel_name': self.kernel_name_edit.text() if self.kernel_checkbox.isChecked() else None
        }


import re  # 在文件顶部导入正则表达式模块

class PackagesDialog(QDialog):
    """显示已安装包的对话框"""
    def __init__(self, env_path, env_name, parent=None):
        super().__init__(parent)
        self.env_path = env_path
        self.env_name = env_name
        self.original_packages = []  # 存储原始包列表
        self.setWindowTitle(f"已安装包 - {env_name}")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        self.load_packages()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 标题
        title = QLabel(f"环境: {self.env_path}")
        title.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(title)

        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入包名称进行模糊搜索...")
        self.search_edit.textChanged.connect(self.filter_packages)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)

        # 包列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["包名称", "版本"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # 关闭按钮
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def load_packages(self):
        self.thread = GetPackagesThread(self.env_path)
        self.thread.finished.connect(self.on_packages_loaded)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def on_packages_loaded(self, packages):
        self.original_packages = packages  # 保存原始数据
        self.populate_table(packages)

    def populate_table(self, packages):
        """填充表格数据"""
        self.table.setRowCount(len(packages))
        for i, pkg in enumerate(packages):
            self.table.setItem(i, 0, QTableWidgetItem(pkg.get('name', '')))
            self.table.setItem(i, 1, QTableWidgetItem(pkg.get('version', '')))

    def filter_packages(self, text):
        """根据输入文本过滤包列表"""
        if not text:
            # 如果搜索框为空，显示全部包
            self.populate_table(self.original_packages)
        else:
            # 模糊搜索：检查包名是否包含搜索词（不区分大小写）
            filtered_packages = []
            text_lower = text.lower()
            
            for pkg in self.original_packages:
                package_name = pkg.get('name', '').lower()
                # 使用 in 操作符实现模糊匹配
                if text_lower in package_name:
                    filtered_packages.append(pkg)
            
            # 更新表格显示
            self.populate_table(filtered_packages)

    def on_error(self, error_msg):
        QMessageBox.critical(self, "错误", f"获取包列表失败: {error_msg}")


class VenvManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python 虚拟环境管理器")
        self.setMinimumSize(900, 600)

        # 配置文件路径
        self.config_file = os.path.join(
            os.path.expanduser("~"), ".venv_manager_config.json"
        )

        # 数据存储
        self.python_versions = []  # [(name, path), ...]
        self.base_folder = ""      # 虚拟环境储存文件夹
        self.environments = []     # 扫描到的虚拟环境列表

        self.load_config()
        self.setup_ui()
        self.refresh_environments()

    def setup_ui(self):
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 左侧控制面板
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)

        # === Python 版本管理 ===
        python_group = QGroupBox("Python 版本管理")
        python_layout = QVBoxLayout(python_group)

        # Python 版本列表
        self.python_list = QListWidget()
        self.python_list.setMaximumHeight(120)
        self.refresh_python_list()
        python_layout.addWidget(self.python_list)

        # Python 版本按钮
        python_btn_layout = QHBoxLayout()
        add_python_btn = QPushButton("添加 Python")
        add_python_btn.clicked.connect(self.add_python_version)
        remove_python_btn = QPushButton("删除")
        remove_python_btn.clicked.connect(self.remove_python_version)
        python_btn_layout.addWidget(add_python_btn)
        python_btn_layout.addWidget(remove_python_btn)
        python_layout.addLayout(python_btn_layout)

        left_layout.addWidget(python_group)

        # === 储存文件夹设置 ===
        folder_group = QGroupBox("虚拟环境储存文件夹")
        folder_layout = QVBoxLayout(folder_group)

        folder_input_layout = QHBoxLayout()
        self.folder_edit = QLineEdit(self.base_folder)
        self.folder_edit.setPlaceholderText("选择文件夹...")
        folder_browse_btn = QPushButton("浏览...")
        folder_browse_btn.clicked.connect(self.browse_base_folder)
        folder_input_layout.addWidget(self.folder_edit)
        folder_input_layout.addWidget(folder_browse_btn)
        folder_layout.addLayout(folder_input_layout)

        set_folder_btn = QPushButton("设置为此文件夹")
        set_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 5px;
                border: none;
                border-radius: 3px;
            }
        """)
        set_folder_btn.clicked.connect(self.set_base_folder)
        folder_layout.addWidget(set_folder_btn)

        left_layout.addWidget(folder_group)

        # === 创建环境按钮 ===
        create_btn = QPushButton("➕ 创建新虚拟环境")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        create_btn.clicked.connect(self.create_environment)
        left_layout.addWidget(create_btn)

        left_layout.addStretch()

        # 右侧环境列表
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # 标题
        title_layout = QHBoxLayout()
        title = QLabel("虚拟环境列表")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title)

        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.refresh_environments)
        title_layout.addWidget(refresh_btn)
        title_layout.addStretch()
        right_layout.addLayout(title_layout)

        # 环境列表
        self.env_list = QListWidget()
        self.env_list.setSpacing(5)
        self.env_list.itemClicked.connect(self.on_env_selected)
        right_layout.addWidget(self.env_list)

        # 选中环境的操作按钮
        self.action_group = QGroupBox("环境操作")
        self.action_group.setEnabled(False)
        action_layout = QHBoxLayout(self.action_group)

        launch_btn = QPushButton("🚀 启动命令窗口")
        launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
        """)
        launch_btn.clicked.connect(self.launch_environment)
        action_layout.addWidget(launch_btn)

        packages_btn = QPushButton("📦 已安装依赖")
        packages_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
        """)
        packages_btn.clicked.connect(self.show_packages)
        action_layout.addWidget(packages_btn)

        delete_btn = QPushButton("🗑️ 删除环境")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
        """)
        delete_btn.clicked.connect(self.delete_environment)
        action_layout.addWidget(delete_btn)

        right_layout.addWidget(self.action_group)

        # 添加到主布局
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)

        # 状态栏
        self.statusBar().showMessage("就绪")

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.python_versions = config.get('python_versions', [])
                    self.base_folder = config.get('base_folder', '')
            except Exception as e:
                print(f"加载配置失败: {e}")

    def save_config(self):
        """保存配置文件"""
        config = {
            'python_versions': self.python_versions,
            'base_folder': self.base_folder
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def refresh_python_list(self):
        """刷新 Python 版本列表显示"""
        self.python_list.clear()
        for name, path in self.python_versions:
            item = QListWidgetItem(f"{name}\n  {path}")
            self.python_list.addItem(item)

    def add_python_version(self):
        """添加 Python 版本"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Python 解释器",
            "", "Python 可执行文件 (python.exe python);;所有文件 (*.*)"
        )
        if file_path:
            # 获取版本信息
            try:
                result = subprocess.run(
                    [file_path, "--version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                version = result.stdout.strip() or result.stderr.strip()
                name = version.replace("Python ", "Python ")
            except:
                name = f"Python ({os.path.basename(file_path)})"

            self.python_versions.append((name, file_path))
            self.refresh_python_list()
            self.save_config()

    def remove_python_version(self):
        """删除选中的 Python 版本"""
        current_row = self.python_list.currentRow()
        if current_row >= 0:
            self.python_versions.pop(current_row)
            self.refresh_python_list()
            self.save_config()

    def browse_base_folder(self):
        """浏览选择基础文件夹"""
        path = QFileDialog.getExistingDirectory(self, "选择虚拟环境储存文件夹")
        if path:
            self.folder_edit.setText(path)

    def set_base_folder(self):
        """设置基础文件夹"""
        path = self.folder_edit.text()
        if path and os.path.isdir(path):
            self.base_folder = path
            self.save_config()
            self.refresh_environments()
            QMessageBox.information(self, "成功", f"已设置储存文件夹: {path}")
        else:
            QMessageBox.warning(self, "错误", "请选择有效的文件夹")

    def refresh_environments(self):
        """刷新虚拟环境列表"""
        self.env_list.clear()
        self.environments = []

        if not self.base_folder or not os.path.isdir(self.base_folder):
            item = QListWidgetItem("请先设置有效的虚拟环境储存文件夹")
            item.setForeground(QColor("gray"))
            self.env_list.addItem(item)
            return

        # 扫描文件夹下的所有子文件夹
        try:
            for item_name in os.listdir(self.base_folder):
                item_path = os.path.join(self.base_folder, item_name)
                if os.path.isdir(item_path):
                    # 检查是否有 activate.bat (Windows) 或 activate (Linux/Mac)
                    activate_bat = os.path.join(item_path, "Scripts", "activate.bat")
                    activate_sh = os.path.join(item_path, "bin", "activate")

                    if os.path.exists(activate_bat) or os.path.exists(activate_sh):
                        self.environments.append((item_name, item_path))

                        # 创建列表项
                        list_item = QListWidgetItem()
                        list_item.setText(f"📁 {item_name}\n   {item_path}")
                        list_item.setData(Qt.ItemDataRole.UserRole, item_path)
                        self.env_list.addItem(list_item)
        except Exception as e:
            item = QListWidgetItem(f"扫描失败: {str(e)}")
            item.setForeground(QColor("red"))
            self.env_list.addItem(item)

        if not self.environments:
            item = QListWidgetItem("未发现虚拟环境")
            item.setForeground(QColor("gray"))
            self.env_list.addItem(item)

        self.statusBar().showMessage(f"发现 {len(self.environments)} 个虚拟环境")

    def on_env_selected(self):
        """当选择环境时启用操作按钮"""
        self.action_group.setEnabled(True)

    def create_environment(self):
        """创建新的虚拟环境"""
        if not self.python_versions:
            QMessageBox.warning(self, "错误", "请先添加至少一个 Python 版本")
            return

        if not self.base_folder:
            QMessageBox.warning(self, "错误", "请先设置虚拟环境储存文件夹")
            return

        dialog = CreateEnvDialog(self, self.python_versions)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()

            # 验证输入
            if not data['env_name']:
                QMessageBox.warning(self, "错误", "请输入环境名称")
                return

            env_path = os.path.join(data['base_path'], data['env_name'])
            if os.path.exists(env_path):
                QMessageBox.warning(self, "错误", "该环境已存在")
                return

            # 创建进度对话框
            self.progress_dialog = QProgressDialog("正在创建虚拟环境...", None, 0, 0, self)
            self.progress_dialog.setWindowTitle("请稍候")
            self.progress_dialog.setModal(True)
            self.progress_dialog.show()

            # 启动创建线程
            self.create_thread = CreateVenvThread(
                data['python_path'],
                env_path,
                data['make_kernel'],
                data['kernel_name']
            )
            self.create_thread.progress.connect(self.on_create_progress)
            self.create_thread.finished.connect(self.on_create_finished)
            self.create_thread.start()

    def on_create_progress(self, message):
        """更新创建进度"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.setLabelText(message)

    def on_create_finished(self, success, message):
        """创建完成回调"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()

        if success:
            QMessageBox.information(self, "成功", message)
            self.refresh_environments()
        else:
            QMessageBox.critical(self, "失败", message)

    def launch_environment(self):
        """启动选中环境的命令窗口"""
        item = self.env_list.currentItem()
        if not item:
            return

        env_path = item.data(Qt.ItemDataRole.UserRole)
        if not env_path:
            return

        try:
            if sys.platform == "win32":
                # Windows: 启动 cmd 并激活环境
                activate_script = os.path.join(env_path, "Scripts", "activate.bat")
                subprocess.Popen(
                    f'start cmd /k "{activate_script}"',
                    shell=True,
                    cwd=env_path
                )
            else:
                # Linux/Mac: 启动终端
                activate_script = os.path.join(env_path, "bin", "activate")
                # 尝试不同的终端
                terminals = [
                    f'gnome-terminal -- bash -c "source {activate_script}; exec bash"',
                    f'xterm -e bash -c "source {activate_script}; exec bash"',
                    f'osascript -e \'tell app "Terminal" to do script "source {activate_script}"\''
                ]
                for cmd in terminals:
                    try:
                        subprocess.Popen(cmd, shell=True)
                        break
                    except:
                        continue

            self.statusBar().showMessage(f"已启动环境: {os.path.basename(env_path)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动失败: {str(e)}")

    def show_packages(self):
        """显示已安装包"""
        item = self.env_list.currentItem()
        if not item:
            return

        env_path = item.data(Qt.ItemDataRole.UserRole)
        env_name = os.path.basename(env_path)

        dialog = PackagesDialog(env_path, env_name, self)
        dialog.exec()

    def delete_environment(self):
        """删除选中的环境"""
        item = self.env_list.currentItem()
        if not item:
            return

        env_path = item.data(Qt.ItemDataRole.UserRole)
        env_name = os.path.basename(env_path)

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除虚拟环境 \"{env_name}\" 吗？\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                import shutil
                shutil.rmtree(env_path)
                QMessageBox.information(self, "成功", "虚拟环境已删除")
                self.refresh_environments()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除失败: {str(e)}")


def main():
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle("Fusion")

    # 设置字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 设置调色板（浅色主题）
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(33, 33, 33))
    app.setPalette(palette)

    window = VenvManager()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
