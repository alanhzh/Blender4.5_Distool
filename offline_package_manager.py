"""
Distool 离线安装包管理模块 / Distool Offline Package Management Module
提供离线安装包创建和管理功能
Provides offline package creation and management functionality
"""

import os
import sys
import zipfile
import json
import shutil
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator, Panel

class DistoolOfflinePackageManager:
    """Distool离线包管理器 / Distool Offline Package Manager"""
    
    def __init__(self):
        self.addon_dir = os.path.dirname(os.path.abspath(__file__))
        self.offline_dir = os.path.join(self.addon_dir, "offline_packages")
        self.cache_dir = os.path.join(self.addon_dir, "cache")
        
        # 确保目录存在
        os.makedirs(self.offline_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 离线包配置
        self.package_config = {
            "numpy": {
                "wheel_url": "https://files.pythonhosted.org/packages/py3/n/numpy/numpy-1.26.4-cp310-cp310-win_amd64.whl",
                "filename": "numpy-1.26.4-cp310-cp310-win_amd64.whl",
                "description": "NumPy数值计算库 / NumPy Numerical Computing Library"
            },
            "scipy": {
                "wheel_url": "https://files.pythonhosted.org/packages/py3/s/scipy/scipy-1.11.4-cp310-cp310-win_amd64.whl",
                "filename": "scipy-1.11.4-cp310-cp310-win_amd64.whl",
                "description": "SciPy科学计算库 / SciPy Scientific Computing Library"
            },
            "opencv-python": {
                "wheel_url": "https://files.pythonhosted.org/packages/py3/o/opencv-python/opencv_python-4.8.1.78-cp310-cp310-win_amd64.whl",
                "filename": "opencv_python-4.8.1.78-cp310-cp310-win_amd64.whl",
                "description": "OpenCV计算机视觉库 / OpenCV Computer Vision Library"
            }
        }
    
    def create_offline_package(self, package_name="distool_offline_deps"):
        """创建离线安装包 / Create offline installation package"""
        try:
            package_path = os.path.join(self.offline_dir, f"{package_name}.zip")
            
            # 如果包已存在，先删除
            if os.path.exists(package_path):
                os.remove(package_path)
            
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # 添加wheel文件
                for dep_name, config in self.package_config.items():
                    wheel_path = os.path.join(self.cache_dir, config["filename"])
                    
                    if os.path.exists(wheel_path):
                        zip_file.write(wheel_path, f"wheels/{config['filename']}")
                    else:
                        print(f"Warning: {config['filename']} not found in cache")
                
                # 添加离线安装脚本
                install_script = self._generate_offline_install_script()
                zip_file.writestr("offline_install.py", install_script)
                
                # 添加配置文件
                config_json = json.dumps(self.package_config, indent=2, ensure_ascii=False)
                zip_file.writestr("package_config.json", config_json)
                
                # 添加说明文档
                readme = self._generate_offline_readme()
                zip_file.writestr("README_OFFLINE.txt", readme)
            
            return True, f"离线包创建成功: {package_path}"
            
        except Exception as e:
            return False, f"创建离线包失败: {str(e)}"
    
    def download_wheels_for_offline(self):
        """为离线包下载wheel文件 / Download wheel files for offline package"""
        import urllib.request
        
        results = {}
        
        for dep_name, config in self.package_config.items():
            try:
                wheel_path = os.path.join(self.cache_dir, config["filename"])
                
                if not os.path.exists(wheel_path):
                    print(f"正在下载 {config['filename']}...")
                    urllib.request.urlretrieve(config["wheel_url"], wheel_path)
                    results[dep_name] = {"success": True, "message": "下载成功"}
                else:
                    results[dep_name] = {"success": True, "message": "文件已存在"}
                    
            except Exception as e:
                results[dep_name] = {"success": False, "message": f"下载失败: {str(e)}"}
        
        return results
    
    def install_from_offline_package(self, package_path):
        """从离线包安装 / Install from offline package"""
        try:
            addon_dir = os.path.dirname(os.path.abspath(__file__))
            lib_dir = os.path.join(addon_dir, "libs")
            
            # 确保libs目录存在
            os.makedirs(lib_dir, exist_ok=True)
            
            with zipfile.ZipFile(package_path, 'r') as zip_file:
                # 解压wheel文件到libs目录
                for file_info in zip_file.filelist:
                    if file_info.filename.startswith("wheels/"):
                        wheel_data = zip_file.read(file_info.filename)
                        wheel_filename = os.path.basename(file_info.filename)
                        wheel_path = os.path.join(lib_dir, wheel_filename)
                        
                        with open(wheel_path, 'wb') as f:
                            f.write(wheel_data)
                        
                        # 解压wheel文件
                        with zipfile.ZipFile(wheel_path, 'r') as wheel_zip:
                            wheel_zip.extractall(lib_dir)
                        
                        # 删除wheel文件
                        os.remove(wheel_path)
            
            return True, "离线包安装成功"
            
        except Exception as e:
            return False, f"离线包安装失败: {str(e)}"
    
    def _generate_offline_install_script(self):
        """生成离线安装脚本 / Generate offline installation script"""
        script_content = '''
"""
Distool 离线安装脚本 / Distool Offline Installation Script
"""

import os
import sys
import zipfile
import json

def install_offline_dependencies():
    """安装离线依赖 / Install offline dependencies"""
    try:
        # 获取当前脚本目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 读取配置文件
        config_path = os.path.join(script_dir, "package_config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 获取插件目录
        addon_dir = os.path.dirname(script_dir)
        lib_dir = os.path.join(addon_dir, "libs")
        
        # 确保libs目录存在
        os.makedirs(lib_dir, exist_ok=True)
        
        # 安装每个依赖
        for dep_name, dep_config in config.items():
            print(f"正在安装 {dep_name}...")
            
            wheel_filename = dep_config["filename"]
            wheel_path = os.path.join(script_dir, "wheels", wheel_filename)
            
            if os.path.exists(wheel_path):
                # 解压wheel文件
                with zipfile.ZipFile(wheel_path, 'r') as wheel_zip:
                    wheel_zip.extractall(lib_dir)
                
                print(f"{dep_name} 安装成功")
            else:
                print(f"错误: {wheel_filename} 不存在")
        
        print("离线依赖安装完成！")
        return True
        
    except Exception as e:
        print(f"离线安装失败: {str(e)}")
        return False

if __name__ == "__main__":
    install_offline_dependencies()
'''
        return script_content
    
    def _generate_offline_readme(self):
        """生成离线包说明文档 / Generate offline package readme"""
        readme_content = '''
Distool 离线安装包说明 / Distool Offline Package Installation Guide
========================================================================

简介 / Introduction
-------------------
此离线安装包包含Distool插件所需的所有Python依赖库，适用于网络受限环境。
This offline package contains all Python dependencies required by Distool plugin,
suitable for network-restricted environments.

包含的库 / Included Libraries
----------------------------
- NumPy 1.26.4: 数值计算库 / Numerical Computing Library
- SciPy 1.11.4: 科学计算库 / Scientific Computing Library  
- OpenCV 4.8.1.78: 计算机视觉库 / Computer Vision Library

安装方法 / Installation Method
-------------------------------
1. 将此ZIP文件解压到Distool插件目录中
2. 重启Blender
3. 插件将自动检测并安装离线依赖

1. Extract this ZIP file to the Distool plugin directory
2. Restart Blender
3. The plugin will automatically detect and install offline dependencies

手动安装 / Manual Installation
------------------------------
如果自动安装失败，可以手动运行：
If automatic installation fails, you can manually run:
python offline_install.py

注意事项 / Important Notes
-------------------------
- 此离线包仅适用于Windows系统Python 3.10环境
- This offline package is only suitable for Windows system with Python 3.10
- 确保有足够的磁盘空间进行安装
- Ensure sufficient disk space for installation

技术支持 / Technical Support
---------------------------
如有问题，请访问：/ For issues, please visit:
https://github.com/alanhzh/Blender4.5_Distool

版本信息 / Version Information
------------------------------
Distool v2.1.0
Created: 2025
'''
        return readme_content

# Blender UI组件
class DISTOOL_OT_CreateOfflinePackage(Operator):
    """创建离线安装包 / Create Offline Package"""
    bl_idname = "distool.create_offline_package"
    bl_label = "创建离线包 / Create Offline Package"
    
    def execute(self, context):
        # 显示下载进度
        def show_download_progress():
            def draw_progress(self, context):
                layout = self.layout
                layout.label(text="正在下载依赖文件.../ Downloading dependency files...", icon='INFO')
                layout.label(text="请稍候.../ Please wait...")
            
            bpy.context.window_manager.popup_menu(draw_progress, title="准备离线包 / Preparing Package")
        
        # 在后台执行下载和创建
        def create_package_thread():
            try:
                from .dependency_manager import dependency_manager
                offline_manager = DistoolOfflinePackageManager()
                
                # 下载wheel文件
                results = offline_manager.download_wheels_for_offline()
                
                # 创建离线包
                success, message = offline_manager.create_offline_package()
                
                if success:
                    self.report({'INFO'}, f"离线包创建成功！/ Offline package created successfully!")
                else:
                    self.report({'ERROR'}, f"离线包创建失败：/ Offline package creation failed: {message}")
                    
            except Exception as e:
                self.report({'ERROR'}, f"创建离线包时出错：/ Error creating offline package: {str(e)}")
        
        # 显示进度并启动线程
        show_download_progress()
        import threading
        thread = threading.Thread(target=create_package_thread)
        thread.daemon = True
        thread.start()
        
        return {'FINISHED'}

class DISTOOL_OT_InstallOfflinePackage(Operator):
    """安装离线包 / Install Offline Package"""
    bl_idname = "distool.install_offline_package"
    bl_label = "安装离线包 / Install Offline Package"
    
    filepath: StringProperty(
        name="File Path",
        description="选择离线包文件 / Select offline package file",
        subtype='FILE_PATH'
    )
    
    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "请选择离线包文件 / Please select offline package file")
            return {'CANCELLED'}
        
        try:
            offline_manager = DistoolOfflinePackageManager()
            success, message = offline_manager.install_from_offline_package(self.filepath)
            
            if success:
                self.report({'INFO'}, f"离线包安装成功！/ Offline package installed successfully!")
            else:
                self.report({'ERROR'}, f"离线包安装失败：/ Offline package installation failed: {message}")
                
        except Exception as e:
            self.report({'ERROR'}, f"安装离线包时出错：/ Error installing offline package: {str(e)}")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class DISTOOL_PT_OfflinePackagePanel(Panel):
    """离线包管理面板 / Offline Package Management Panel"""
    bl_label = "离线包管理 / Offline Package"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Distool"
    
    def draw(self, context):
        layout = self.layout
        
        # 说明
        box = layout.box()
        box.label(text="📦 离线安装包 / Offline Package", icon='PACKAGE')
        
        col = box.column(align=True)
        col.label(text="适用于网络受限环境 / For network-restricted environments")
        col.label(text="包含所有必需依赖库 / Contains all required dependencies")
        
        layout.separator()
        
        # 创建离线包
        col = layout.column(align=True)
        col.label(text="创建离线包 / Create Offline Package:", icon='FILE_NEW')
        col.operator("distool.create_offline_package", text="创建离线安装包 / Create Package", icon='EXPORT')
        
        layout.separator()
        
        # 安装离线包
        col = layout.column(align=True)
        col.label(text="安装离线包 / Install Offline Package:", icon='IMPORT')
        col.operator("distool.install_offline_package", text="选择并安装离线包 / Select & Install Package", icon='FILE_FOLDER')
        
        layout.separator()
        
        # 使用说明
        box = layout.box()
        box.label(text="使用说明 / Usage Instructions:", icon='HELP')
        col = box.column(align=True)
        col.label(text="1. 创建离线包（需要网络）")
        col.label(text="2. 将离线包复制到目标机器")
        col.label(text="3. 在目标机器上安装离线包")
        col.label(text="1. Create package (requires network)")
        col.label(text="2. Copy package to target machine")
        col.label(text="3. Install package on target machine")

def register_offline_package():
    """注册离线包管理 / Register offline package management"""
    bpy.utils.register_class(DISTOOL_OT_CreateOfflinePackage)
    bpy.utils.register_class(DISTOOL_OT_InstallOfflinePackage)
    bpy.utils.register_class(DISTOOL_PT_OfflinePackagePanel)

def unregister_offline_package():
    """注销离线包管理 / Unregister offline package management"""
    bpy.utils.unregister_class(DISTOOL_OT_CreateOfflinePackage)
    bpy.utils.unregister_class(DISTOOL_OT_InstallOfflinePackage)
    bpy.utils.unregister_class(DISTOOL_PT_OfflinePackagePanel)