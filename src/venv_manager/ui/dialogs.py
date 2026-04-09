"""
Dialog for creating new virtual environments
"""
import os
from PyQt6.QtWidgets import (QDialog, QFormLayout, QHBoxLayout, QVBoxLayout,
                             QPushButton, QLineEdit, QComboBox, QCheckBox,
                             QLabel, QFileDialog)
from PyQt6.QtCore import Qt


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
