"""
Environment manager for handling virtual environments
"""
import os
import sys
import json
import subprocess
import shutil
from pathlib import Path


class EnvironmentManager:
    """虚拟环境管理器，处理环境的扫描、创建和删除"""
    
    def __init__(self, base_folder=""):
        self.base_folder = base_folder
    
    def scan_environments(self):
        """扫描基础文件夹下的所有虚拟环境"""
        environments = []
        
        if not self.base_folder or not os.path.isdir(self.base_folder):
            return environments
        
        try:
            for item_name in os.listdir(self.base_folder):
                item_path = os.path.join(self.base_folder, item_name)
                if os.path.isdir(item_path):
                    # 检查是否有 activate.bat (Windows) 或 activate (Linux/Mac)
                    activate_bat = os.path.join(item_path, "Scripts", "activate.bat")
                    activate_sh = os.path.join(item_path, "bin", "activate")
                    
                    if os.path.exists(activate_bat) or os.path.exists(activate_sh):
                        environments.append((item_name, item_path))
        except Exception as e:
            print(f"扫描失败: {str(e)}")
        
        return environments
    
    def delete_environment(self, env_path):
        """删除指定的虚拟环境"""
        try:
            shutil.rmtree(env_path)
            return True, "虚拟环境已删除"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def launch_environment(self, env_path):
        """启动虚拟环境的命令窗口"""
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
            
            return True, f"已启动环境: {os.path.basename(env_path)}"
        except Exception as e:
            return False, f"启动失败: {str(e)}"
    
    @staticmethod
    def get_python_version(python_path):
        """获取Python解释器的版本信息"""
        try:
            result = subprocess.run(
                [python_path, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip() or result.stderr.strip()
            name = version.replace("Python ", "Python ")
            return name
        except:
            return f"Python ({os.path.basename(python_path)})"
