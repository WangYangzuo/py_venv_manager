"""
Main application window
"""
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QListWidgetItem, QLabel, 
                             QLineEdit, QGroupBox, QMessageBox, QFileDialog,
                             QProgressDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from .dialogs import CreateEnvDialog
from .packages_dialog import PackagesDialog
from ..core.threads import CreateVenvThread
from ..core.environment import EnvironmentManager
from ..utils.config import ConfigManager


class VenvManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python 虚拟环境管理器")
        self.setMinimumSize(900, 600)

        # 配置管理器
        self.config = ConfigManager()
        
        # 数据存储
        self.python_versions = self.config.get_python_versions()
        self.base_folder = self.config.get_base_folder()
        self.environments = []  # 扫描到的虚拟环境列表
        
        # 环境管理器
        self.env_manager = EnvironmentManager(self.base_folder)

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
            from ..core.environment import EnvironmentManager
            name = EnvironmentManager.get_python_version(file_path)
            
            self.python_versions.append((name, file_path))
            self.config.set_python_versions(self.python_versions)
            self.refresh_python_list()

    def remove_python_version(self):
        """删除选中的 Python 版本"""
        current_row = self.python_list.currentRow()
        if current_row >= 0:
            self.python_versions.pop(current_row)
            self.config.set_python_versions(self.python_versions)
            self.refresh_python_list()

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
            self.env_manager.base_folder = path
            self.config.set_base_folder(path)
            self.refresh_environments()
            QMessageBox.information(self, "成功", f"已设置储存文件夹: {path}")
        else:
            QMessageBox.warning(self, "错误", "请选择有效的文件夹")

    def refresh_environments(self):
        """刷新虚拟环境列表"""
        self.env_list.clear()
        self.environments = self.env_manager.scan_environments()

        if not self.base_folder or not os.path.isdir(self.base_folder):
            item = QListWidgetItem("请先设置有效的虚拟环境储存文件夹")
            item.setForeground(QColor("gray"))
            self.env_list.addItem(item)
            return

        # 显示扫描结果
        for env_name, env_path in self.environments:
            list_item = QListWidgetItem()
            list_item.setText(f"📁 {env_name}\n   {env_path}")
            list_item.setData(Qt.ItemDataRole.UserRole, env_path)
            self.env_list.addItem(list_item)

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

        success, message = self.env_manager.launch_environment(env_path)
        if success:
            self.statusBar().showMessage(message)
        else:
            QMessageBox.critical(self, "错误", message)

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
            success, message = self.env_manager.delete_environment(env_path)
            if success:
                QMessageBox.information(self, "成功", message)
                self.refresh_environments()
            else:
                QMessageBox.critical(self, "错误", message)
