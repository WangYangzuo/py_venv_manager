"""
Thread classes for background operations
"""
import sys
import os
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal


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
