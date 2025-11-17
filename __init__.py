bl_info = {
    "name": "Distool: Displacement & Normal Generator",
    "author": "wsmnb12-Alan+AI",
    "version": (2, 1, 0),
    "blender": (4, 5, 0),
    "location": "Shader Editor > Sidebar > Distool",
    "description": "Advanced normal/displacement map generator with multiple gradient operators and detail enhancement. Includes automatic dependency management and installation wizard.",
    "category": "Node",
    "warning": "",
    "wiki_url": "",
    "tracker_url": ""
}

import sys
import os

# 插件目录设置 / Addon directory setup
addon_dir = os.path.dirname(__file__)
lib_dir = os.path.join(addon_dir, "libs")

# 确保lib路径在Python路径中 / Ensure lib path is in Python path
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

# 导入依赖管理模块 / Import dependency management modules
try:
    from . import dependency_manager
    from . import installation_wizard
    from . import offline_package_manager
    DEPENDENCY_MANAGEMENT_AVAILABLE = True
except ImportError as e:
    print(f"[Distool] Warning: Dependency management modules not available: {e}")
    DEPENDENCY_MANAGEMENT_AVAILABLE = False

# 传统依赖安装方法（备用） / Legacy dependency installation (fallback)
def legacy_dependency_install():
    """传统依赖安装方法 / Legacy dependency installation method"""
    if os.path.exists(lib_dir):
        return  # already exists

    import urllib.request
    import zipfile
    
    zip_url = "https://github.com/wsmnb12/Distool-/releases/download/libs/libs.zip" 
    tmp_zip = os.path.join(addon_dir, "libs.zip")

    try:
        print(f"[Distool] Downloading dependencies from {zip_url} ...")
        urllib.request.urlretrieve(zip_url, tmp_zip)
        with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
            zip_ref.extractall(addon_dir)
        os.remove(tmp_zip)
        print("[Distool] Dependencies installed successfully.")
    except Exception as e:
        print(f"[Distool] Failed to download/extract libs.zip: {e}")

# 检查依赖是否可用 / Check if dependencies are available
def check_dependencies():
    """检查所需依赖是否可用 / Check if required dependencies are available"""
    try:
        import numpy
        import scipy
        import cv2
        print("[Distool] All dependencies are available.")
        return True
    except ImportError as e:
        print(f"[Distool] Missing dependencies: {e}")
        return False

# 尝试使用传统方法安装依赖 / Try to install dependencies using legacy method
if not DEPENDENCY_MANAGEMENT_AVAILABLE:
    legacy_dependency_install()

# 检查依赖状态 / Check dependency status
dependencies_available = check_dependencies()

# 导入主模块 / Import main module
if dependencies_available:
    try:
        from . import distool_main
        MAIN_MODULE_AVAILABLE = True
    except ImportError as e:
        print(f"[Distool] Error importing main module: {e}")
        MAIN_MODULE_AVAILABLE = False
else:
    print("[Distool] Main module not imported due to missing dependencies.")
    MAIN_MODULE_AVAILABLE = False

def register():
    """注册插件 / Register addon"""
    # 注册依赖管理功能 / Register dependency management
    if DEPENDENCY_MANAGEMENT_AVAILABLE:
        try:
            dependency_manager.register_dependency_management()
            installation_wizard.register_installation_wizard()
            offline_package_manager.register_offline_package()
            print("[Distool] Dependency management registered successfully.")
        except Exception as e:
            print(f"[Distool] Error registering dependency management: {e}")
    
    # 注册主模块 / Register main module
    if MAIN_MODULE_AVAILABLE:
        try:
            distool_main.register()
            print("[Distool] Main module registered successfully.")
        except Exception as e:
            print(f"[Distool] Error registering main module: {e}")
    else:
        print("[Distool] Main module not registered due to missing dependencies.")
        # 显示用户友好的错误信息 / Show user-friendly error message
        def show_error_message():
            import bpy
            def draw_error(self, context):
                layout = self.layout
                layout.label(text="⚠️ Distool 依赖缺失 / Dependencies Missing", icon='ERROR')
                layout.separator()
                layout.label(text="请使用安装向导安装依赖 / Please use installation wizard")
                layout.label(text="Please use installation wizard to install dependencies")
                layout.separator()
                if DEPENDENCY_MANAGEMENT_AVAILABLE:
                    layout.operator("distool.installation_wizard", text="启动安装向导 / Start Wizard", icon='HELP')
                else:
                    layout.label(text="请手动安装依赖库 / Please install dependencies manually")
            
            bpy.context.window_manager.popup_menu(draw_error, title="Distool 错误 / Error", icon='ERROR')
        
        # 延迟显示错误信息 / Delay showing error message
        import bpy
        bpy.app.timers.register(show_error_message, first_interval=1.0)

def unregister():
    """注销插件 / Unregister addon"""
    # 注销主模块 / Unregister main module
    if MAIN_MODULE_AVAILABLE:
        try:
            distool_main.unregister()
        except Exception as e:
            print(f"[Distool] Error unregistering main module: {e}")
    
    # 注销依赖管理功能 / Unregister dependency management
    if DEPENDENCY_MANAGEMENT_AVAILABLE:
        try:
            installation_wizard.unregister_installation_wizard()
            dependency_manager.unregister_dependency_management()
            offline_package_manager.unregister_offline_package()
        except Exception as e:
            print(f"[Distool] Error unregistering dependency management: {e}")
