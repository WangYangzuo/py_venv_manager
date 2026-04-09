"""
Configuration manager for handling application settings
"""
import os
import json


class ConfigManager:
    """配置管理器，处理应用配置的读写"""
    
    def __init__(self):
        self.config_file = os.path.join(
            os.path.expanduser("~"), ".venv_manager_config.json"
        )
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
        
        return {'python_versions': [], 'base_folder': ''}
    
    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get_python_versions(self):
        """获取Python版本列表"""
        return self.config.get('python_versions', [])
    
    def set_python_versions(self, versions):
        """设置Python版本列表"""
        self.config['python_versions'] = versions
        self._save_config()
    
    def get_base_folder(self):
        """获取基础文件夹路径"""
        return self.config.get('base_folder', '')
    
    def set_base_folder(self, folder):
        """设置基础文件夹路径"""
        self.config['base_folder'] = folder
        self._save_config()
