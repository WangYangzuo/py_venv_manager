"""
Dialog for displaying installed packages
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QMessageBox)
from ..core.threads import GetPackagesThread


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
