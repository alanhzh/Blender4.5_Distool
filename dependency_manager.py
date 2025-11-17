"""
Distool 依赖管理模块 / Distool Dependency Management Module
自动检测、安装和管理Blender插件所需的Python库
Automatic detection, installation and management of Python libraries required by Blender addon
"""

import sys
import os
import subprocess
import threading
import urllib.request
import zipfile
import json
import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty
from bpy.types import Operator, Panel

class DistoolDependencyManager:
    """Distool依赖管理器 / Distool Dependency Manager"""
    
    def __init__(self):
        self.addon_dir = os.path.dirname(os.path.abspath(__file__))
        self.lib_dir = os.path.join(self.addon_dir, "libs")
        self.cache_dir = os.path.join(self.addon_dir, "cache")
        
        # 确保目录存在
        os.makedirs(self.lib_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 依赖库配置
        self.dependencies = {
            "numpy": {
                "version": ">=1.21.0",
                "import_name": "numpy",
                "wheel_url": "https://files.pythonhosted.org/packages/py3/n/numpy/numpy-1.26.4-cp310-cp310-win_amd64.whl",
                "description": "数值计算库 / Numerical Computing Library"
            },
            "scipy": {
                "version": ">=1.7.0",
                "import_name": "scipy",
                "wheel_url": "https://files.pythonhosted.org/packages/py3/s/scipy/scipy-1.11.4-cp310-cp310-win_amd64.whl",
                "description": "科学计算库 / Scientific Computing Library"
            },
            "opencv-python": {
                "version": ">=4.5.0",
                "import_name": "cv2",
                "wheel_url": "https://files.pythonhosted.org/packages/py3/o/opencv-python/opencv_python-4.8.1.78-cp310-cp310-win_amd64.whl",
                "description": "计算机视觉库 / Computer Vision Library"
            }
        }
        
        # 添加lib目录到Python路径
        if self.lib_dir not in sys.path:
            sys.path.insert(0, self.lib_dir)
    
    def check_dependency(self, dep_name):
        """检查单个依赖是否可用 / Check if single dependency is available"""
        dep_config = self.dependencies.get(dep_name)
        if not dep_config:
            return False, f"Unknown dependency: {dep_name}"
        
        try:
            __import__(dep_config["import_name"])
            return True, f"{dep_name} is available"
        except ImportError as e:
            return False, f"{dep_name} not available: {str(e)}"
    
    def check_all_dependencies(self):
        """检查所有依赖状态 / Check all dependencies status"""
        status = {}
        for dep_name in self.dependencies.keys():
            available, message = self.check_dependency(dep_name)
            status[dep_name] = {
                "available": available,
                "message": message,
                "config": self.dependencies[dep_name]
            }
        return status
    
    def install_dependency(self, dep_name, progress_callback=None):
        """安装单个依赖 / Install single dependency"""
        dep_config = self.dependencies.get(dep_name)
        if not dep_config:
            return False, f"Unknown dependency: {dep_name}"
        
        try:
            if progress_callback:
                progress_callback(f"正在下载 {dep_name}...", 0.2)
            
            # 下载wheel文件
            wheel_url = dep_config["wheel_url"]
            wheel_filename = os.path.basename(wheel_url)
            wheel_path = os.path.join(self.cache_dir, wheel_filename)
            
            if not os.path.exists(wheel_path):
                urllib.request.urlretrieve(wheel_url, wheel_path)
            
            if progress_callback:
                progress_callback(f"正在安装 {dep_name}...", 0.6)
            
            # 解压wheel文件
            with zipfile.ZipFile(wheel_path, 'r') as zip_ref:
                zip_ref.extractall(self.lib_dir)
            
            if progress_callback:
                progress_callback(f"正在配置 {dep_name}...", 0.9)
            
            # 验证安装
            available, message = self.check_dependency(dep_name)
            if available:
                if progress_callback:
                    progress_callback(f"{dep_name} 安装成功！", 1.0)
                return True, f"{dep_name} installed successfully"
            else:
                return False, f"{dep_name} installation failed: {message}"
                
        except Exception as e:
            return False, f"Error installing {dep_name}: {str(e)}"
    
    def install_all_dependencies(self, progress_callback=None):
        """安装所有依赖 / Install all dependencies"""
        results = {}
        for dep_name in self.dependencies.keys():
            success, message = self.install_dependency(dep_name, progress_callback)
            results[dep_name] = {
                "success": success,
                "message": message
            }
        return results
    
    def get_blender_python_info(self):
        """获取Blender Python信息 / Get Blender Python information"""
        return {
            "version": sys.version,
            "executable": sys.executable,
            "path": sys.path[:5],  # 只显示前5个路径
            "platform": sys.platform
        }

# 全局依赖管理器实例
dependency_manager = DistoolDependencyManager()

# Blender UI组件
class DISTOOL_OT_CheckDependencies(Operator):
    """检查依赖状态 / Check Dependencies Status"""
    bl_idname = "distool.check_dependencies"
    bl_label = "检查依赖 / Check Dependencies"
    
    def execute(self, context):
        status = dependency_manager.check_all_dependencies()
        
        # 显示状态信息
        message = "依赖状态 / Dependencies Status:\n"
        for dep_name, dep_status in status.items():
            status_icon = "✅" if dep_status["available"] else "❌"
            message += f"\n{status_icon} {dep_name}: {dep_status['message']}"
        
        self.report({'INFO'}, message)
        return {'FINISHED'}

class DISTOOL_OT_InstallDependencies(Operator):
    """安装依赖库 / Install Dependencies"""
    bl_idname = "distool.install_dependencies"
    bl_label = "安装依赖 / Install Dependencies"
    
    def execute(self, context):
        def progress_callback(message, progress):
            # 更新进度显示
            context.scene.distool_install_progress = f"{message} ({int(progress*100)}%)"
            context.scene.distool_install_progress_value = progress
        
        # 开始安装
        context.scene.distool_installing = True
        context.scene.distool_install_progress = "开始安装依赖..."
        
        try:
            results = dependency_manager.install_all_dependencies(progress_callback)
            
            # 检查结果
            all_success = all(result["success"] for result in results.values())
            
            if all_success:
                self.report({'INFO'}, "所有依赖安装成功！/ All dependencies installed successfully!")
            else:
                failed_deps = [name for name, result in results.items() if not result["success"]]
                self.report({'WARNING'}, f"部分依赖安装失败: {', '.join(failed_deps)}")
            
        except Exception as e:
            self.report({'ERROR'}, f"安装过程中出现错误: {str(e)}")
        
        finally:
            context.scene.distool_installing = False
            context.scene.distool_install_progress = ""
        
        return {'FINISHED'}

class DISTOOL_OT_InstallSingleDependency(Operator):
    """安装单个依赖 / Install Single Dependency"""
    bl_idname = "distool.install_single_dependency"
    bl_label = "安装 / Install"
    
    dependency_name: StringProperty(
        name="Dependency Name",
        description="要安装的依赖名称 / Name of dependency to install"
    )
    
    def execute(self, context):
        def progress_callback(message, progress):
            context.scene.distool_install_progress = f"{message} ({int(progress*100)}%)"
        
        context.scene.distool_installing = True
        context.scene.distool_install_progress = f"正在安装 {self.dependency_name}..."
        
        try:
            success, message = dependency_manager.install_dependency(
                self.dependency_name, progress_callback
            )
            
            if success:
                self.report({'INFO'}, f"{self.dependency_name} 安装成功！")
            else:
                self.report({'ERROR'}, f"{self.dependency_name} 安装失败: {message}")
                
        except Exception as e:
            self.report({'ERROR'}, f"安装错误: {str(e)}")
        
        finally:
            context.scene.distool_installing = False
            context.scene.distool_install_progress = ""
        
        return {'FINISHED'}

class DISTOOL_PT_DependencyPanel(Panel):
    """依赖管理面板 / Dependency Management Panel"""
    bl_label = "依赖管理 / Dependency Management"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Distool"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # 检查依赖状态
        status = dependency_manager.check_all_dependencies()
        
        # 总体状态
        all_available = all(dep_status["available"] for dep_status in status.values())
        
        if all_available:
            box = layout.box()
            box.label(text="✅ 所有依赖已安装 / All Dependencies Installed", icon='CHECKMARK')
        else:
            box = layout.box()
            box.label(text="⚠️ 需要安装依赖 / Dependencies Required", icon='ERROR')
        
        layout.separator()
        
        # 依赖列表
        for dep_name, dep_status in status.items():
            dep_config = dep_status["config"]
            
            row = layout.row()
            
            # 状态图标
            if dep_status["available"]:
                row.label(text="", icon='CHECKMARK')
                row.label(text=f"{dep_name} (已安装 / Installed)")
            else:
                row.label(text="", icon='ERROR')
                row.label(text=f"{dep_name} (未安装 / Not Installed)")
                
                # 安装按钮
                row.operator("distool.install_single_dependency", text="安装").dependency_name = dep_name
            
            # 描述
            row = layout.row()
            row.label(text=f"  {dep_config['description']}", icon='INFO')
        
        layout.separator()
        
        # 批量操作
        if not all_available:
            layout.operator("distool.install_dependencies", icon='IMPORT')
        
        layout.operator("distool.check_dependencies", icon='VIEWZOOM')
        
        # 安装进度
        if scene.get("distool_installing", False):
            box = layout.box()
            box.label(text="安装进度 / Installation Progress:")
            progress_text = scene.get("distool_install_progress", "")
            progress_value = scene.get("distool_install_progress_value", 0.0)
            
            if progress_text:
                box.label(text=progress_text)
                box.progress(factor=progress_value)
        
        layout.separator()
        
        # 系统信息
        box = layout.box()
        box.label(text="系统信息 / System Info:", icon='SETTINGS')
        py_info = dependency_manager.get_blender_python_info()
        
        col = box.column(align=True)
        col.label(text=f"Python版本 / Python Version: {py_info['version'].split()[0]}")
        col.label(text=f"平台 / Platform: {py_info['platform']}")
        col.label(text=f"可执行文件 / Executable: {os.path.basename(py_info['executable'])}")

def register_dependency_management():
    """注册依赖管理功能 / Register dependency management"""
    bpy.utils.register_class(DISTOOL_OT_CheckDependencies)
    bpy.utils.register_class(DISTOOL_OT_InstallDependencies)
    bpy.utils.register_class(DISTOOL_OT_InstallSingleDependency)
    bpy.utils.register_class(DISTOOL_PT_DependencyPanel)
    
    # 添加属性
    bpy.types.Scene.distool_installing = BoolProperty(default=False)
    bpy.types.Scene.distool_install_progress = StringProperty(default="")
    bpy.types.Scene.distool_install_progress_value = bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)

def unregister_dependency_management():
    """注销依赖管理功能 / Unregister dependency management"""
    bpy.utils.unregister_class(DISTOOL_OT_CheckDependencies)
    bpy.utils.unregister_class(DISTOOL_OT_InstallDependencies)
    bpy.utils.unregister_class(DISTOOL_OT_InstallSingleDependency)
    bpy.utils.unregister_class(DISTOOL_PT_DependencyPanel)
    
    # 删除属性
    del bpy.types.Scene.distool_installing
    del bpy.types.Scene.distool_install_progress
    del bpy.types.Scene.distool_install_progress_value