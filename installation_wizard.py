"""
Distool 安装向导模块 / Distool Installation Wizard Module
提供用户友好的安装向导界面
Provides user-friendly installation wizard interface
"""

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty
from bpy.types import Operator, Panel
import threading
import time

class DISTOOL_OT_InstallationWizard(Operator):
    """Distool安装向导 / Distool Installation Wizard"""
    bl_idname = "distool.installation_wizard"
    bl_label = "安装向导 / Installation Wizard"
    bl_options = {'REGISTER', 'UNDO'}
    
    # 向导步骤
    wizard_steps = [
        "welcome",
        "check_system", 
        "check_dependencies",
        "install_dependencies",
        "complete"
    ]
    
    current_step: IntProperty(default=0, min=0, max=4)
    
    def execute(self, context):
        return self.invoke(context, None)
    
    def invoke(self, context, event):
        self.current_step = 0
        return context.window_manager.invoke_props_dialog(self, width=600)
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # 标题
        box = layout.box()
        box.label(text="🔧 Distool 安装向导 / Installation Wizard", icon='SETTINGS')
        
        # 进度指示器
        progress_box = layout.box()
        progress_box.label(text=f"步骤 {self.current_step + 1} / {len(self.wizard_steps)}")
        progress_box.progress(factor=(self.current_step) / len(self.wizard_steps))
        
        # 当前步骤内容
        if self.current_step == 0:  # 欢迎
            self.draw_welcome_step(layout)
        elif self.current_step == 1:  # 系统检查
            self.draw_system_check_step(layout, context)
        elif self.current_step == 2:  # 依赖检查
            self.draw_dependency_check_step(layout, context)
        elif self.current_step == 3:  # 依赖安装
            self.draw_install_step(layout, context)
        elif self.current_step == 4:  # 完成
            self.draw_complete_step(layout)
        
        # 导航按钮
        layout.separator()
        nav_box = layout.box()
        
        row = nav_box.row()
        
        if self.current_step > 0:
            row.operator("distool.wizard_previous", text="上一步 / Previous")
        
        if self.current_step < len(self.wizard_steps) - 1:
            row.operator("distool.wizard_next", text="下一步 / Next")
        else:
            row.operator("distool.wizard_finish", text="完成 / Finish", icon='CHECKMARK')
    
    def draw_welcome_step(self, layout):
        """绘制欢迎步骤 / Draw welcome step"""
        box = layout.box()
        box.label(text="欢迎使用 Distool！/ Welcome to Distool!", icon='HELP')
        
        col = box.column(align=True)
        col.label(text="本向导将帮助您：/ This wizard will help you:")
        col.label(text="• 检查系统兼容性 / Check system compatibility")
        col.label(text="• 安装必要的依赖库 / Install required dependencies")
        col.label(text="• 配置插件环境 / Configure plugin environment")
        
        col.separator()
        col.label(text="Distool 是一个强大的法线贴图和位移贴图生成工具")
        col.label(text="Distool is a powerful normal map and displacement map generation tool")
        
        col.separator()
        col.label(text="点击"下一步"开始 / Click 'Next' to begin", icon='FORWARD')
    
    def draw_system_check_step(self, layout, context):
        """绘制系统检查步骤 / Draw system check step"""
        box = layout.box()
        box.label(text="系统检查 / System Check", icon='SYSTEM')
        
        # 获取系统信息
        from .dependency_manager import dependency_manager
        py_info = dependency_manager.get_blender_python_info()
        
        col = box.column(align=True)
        
        # Blender版本检查
        blender_version = bpy.app.version
        if blender_version >= (4, 0, 0):
            col.label(text=f"✅ Blender版本: {'.'.join(map(str, blender_version))} (兼容 / Compatible)")
        else:
            col.label(text=f"⚠️ Blender版本: {'.'.join(map(str, blender_version))} (建议升级 / Recommended upgrade)")
        
        # Python版本检查
        py_version = py_info['version'].split()[0]
        if py_version.startswith('3.10') or py_version.startswith('3.9'):
            col.label(text=f"✅ Python版本: {py_version} (兼容 / Compatible)")
        else:
            col.label(text=f"⚠️ Python版本: {py_version} (可能不兼容 / May not be compatible)")
        
        # 平台检查
        platform = py_info['platform']
        if 'win' in platform:
            col.label(text=f"✅ 平台: {platform} (支持 / Supported)")
        else:
            col.label(text=f"⚠️ 平台: {platform} (可能需要额外配置 / May need extra configuration)")
        
        col.separator()
        col.label(text="系统检查完成 / System check completed", icon='CHECKMARK')
    
    def draw_dependency_check_step(self, layout, context):
        """绘制依赖检查步骤 / Draw dependency check step"""
        box = layout.box()
        box.label(text="依赖库检查 / Dependency Check", icon='LIBRARY_DATA_DIRECT')
        
        from .dependency_manager import dependency_manager
        status = dependency_manager.check_all_dependencies()
        
        col = box.column(align=True)
        
        all_available = True
        for dep_name, dep_status in status.items():
            if dep_status["available"]:
                col.label(text=f"✅ {dep_name}: 已安装 / Installed")
            else:
                col.label(text=f"❌ {dep_name}: 未安装 / Not Installed")
                all_available = False
        
        col.separator()
        
        if all_available:
            col.label(text="所有依赖已就绪！/ All dependencies ready!", icon='CHECKMARK')
        else:
            col.label(text="需要安装缺失的依赖库 / Need to install missing dependencies")
            col.label(text="点击"下一步"开始安装 / Click 'Next' to start installation", icon='FORWARD')
    
    def draw_install_step(self, layout, context):
        """绘制安装步骤 / Draw installation step"""
        box = layout.box()
        box.label(text="安装依赖库 / Installing Dependencies", icon='IMPORT')
        
        # 检查是否正在安装
        if context.scene.get("distool_wizard_installing", False):
            col = box.column(align=True)
            progress_text = context.scene.get("distool_wizard_progress", "准备安装...")
            progress_value = context.scene.get("distool_wizard_progress_value", 0.0)
            
            col.label(text=progress_text)
            col.progress(factor=progress_value)
            
            col.label(text="请稍候，安装正在进行中.../ Please wait, installation in progress...")
            
        else:
            col = box.column(align=True)
            col.label(text="准备安装必要的依赖库 / Ready to install necessary dependencies")
            col.label(text="这将包括：/ This will include:")
            col.label(text="• NumPy - 数值计算库 / Numerical Computing Library")
            col.label(text="• SciPy - 科学计算库 / Scientific Computing Library") 
            col.label(text="• OpenCV - 计算机视觉库 / Computer Vision Library")
            
            col.separator()
            col.label(text="注意：安装过程需要网络连接 / Note: Installation requires internet connection")
            
            # 安装按钮
            install_op = col.operator("distool.wizard_install", text="开始安装 / Start Installation", icon='PLAY')
    
    def draw_complete_step(self, layout):
        """绘制完成步骤 / Draw complete step"""
        box = layout.box()
        box.label(text="安装完成！/ Installation Complete!", icon='CHECKMARK')
        
        col = box.column(align=True)
        col.label(text="🎉 恭喜！Distool 已成功安装完成！")
        col.label(text="🎉 Congratulations! Distool has been successfully installed!")
        
        col.separator()
        col.label(text="现在您可以：/ Now you can:")
        col.label(text="• 在 Shader Editor 中找到 Distool 面板")
        col.label(text="• 使用法线贴图和位移贴图生成功能")
        col.label(text="• 享受高质量的贴图生成体验")
        
        col.separator()
        col.label(text="Find Distool panel in Shader Editor")
        col.label(text="Use normal map and displacement map generation features")
        col.label(text="Enjoy high-quality texture generation experience")
        
        col.separator()
        col.label(text="感谢使用 Distool！/ Thank you for using Distool!", icon='HEART')

class DISTOOL_OT_WizardNext(Operator):
    """向导下一步 / Wizard Next Step"""
    bl_idname = "distool.wizard_next"
    bl_label = "下一步 / Next"
    
    def execute(self, context):
        wizard = context.window_manager.operator_properties_last("distool.installation_wizard")
        if wizard:
            wizard.current_step = min(wizard.current_step + 1, 4)
        return {'FINISHED'}

class DISTOOL_OT_WizardPrevious(Operator):
    """向导上一步 / Wizard Previous Step"""
    bl_idname = "distool.wizard_previous"
    bl_label = "上一步 / Previous"
    
    def execute(self, context):
        wizard = context.window_manager.operator_properties_last("distool.installation_wizard")
        if wizard:
            wizard.current_step = max(wizard.current_step - 1, 0)
        return {'FINISHED'}

class DISTOOL_OT_WizardInstall(Operator):
    """向导安装依赖 / Wizard Install Dependencies"""
    bl_idname = "distool.wizard_install"
    bl_label = "开始安装 / Start Installation"
    
    def execute(self, context):
        # 设置安装状态
        context.scene.distool_wizard_installing = True
        context.scene.distool_wizard_progress = "正在初始化安装..."
        context.scene.distool_wizard_progress_value = 0.0
        
        # 在后台线程中执行安装
        def install_thread():
            try:
                from .dependency_manager import dependency_manager
                
                def progress_callback(message, progress):
                    context.scene.distool_wizard_progress = message
                    context.scene.distool_wizard_progress_value = progress
                
                # 安装所有依赖
                results = dependency_manager.install_all_dependencies(progress_callback)
                
                # 检查结果
                all_success = all(result["success"] for result in results.values())
                
                if all_success:
                    context.scene.distool_wizard_progress = "安装完成！/ Installation Complete!"
                    context.scene.distool_wizard_progress_value = 1.0
                else:
                    failed_deps = [name for name, result in results.items() if not result["success"]]
                    context.scene.distool_wizard_progress = f"部分安装失败: {', '.join(failed_deps)}"
                
            except Exception as e:
                context.scene.distool_wizard_progress = f"安装错误: {str(e)}"
            
            finally:
                context.scene.distool_wizard_installing = False
        
        # 启动安装线程
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
        
        return {'FINISHED'}

class DISTOOL_OT_WizardFinish(Operator):
    """向导完成 / Wizard Finish"""
    bl_idname = "distool.wizard_finish"
    bl_label = "完成 / Finish"
    
    def execute(self, context):
        self.report({'INFO'}, "安装向导完成！/ Installation wizard completed!")
        return {'FINISHED'}

class DISTOOL_PT_QuickInstallPanel(Panel):
    """快速安装面板 / Quick Install Panel"""
    bl_label = "快速安装 / Quick Install"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Distool"
    
    def draw(self, context):
        layout = self.layout
        
        # 快速安装按钮
        box = layout.box()
        box.label(text="🚀 快速安装 / Quick Install", icon='MODIFIER')
        
        col = box.column(align=True)
        col.label(text="新用户？使用安装向导 / New user? Use installation wizard")
        col.operator("distool.installation_wizard", text="启动安装向导 / Start Wizard", icon='HELP')
        
        col.separator()
        col.label(text="或手动检查依赖 / Or manually check dependencies")
        col.operator("distool.check_dependencies", text="检查依赖 / Check Dependencies", icon='VIEWZOOM')

def register_installation_wizard():
    """注册安装向导 / Register installation wizard"""
    bpy.utils.register_class(DISTOOL_OT_InstallationWizard)
    bpy.utils.register_class(DISTOOL_OT_WizardNext)
    bpy.utils.register_class(DISTOOL_OT_WizardPrevious)
    bpy.utils.register_class(DISTOOL_OT_WizardInstall)
    bpy.utils.register_class(DISTOOL_OT_WizardFinish)
    bpy.utils.register_class(DISTOOL_PT_QuickInstallPanel)
    
    # 添加属性
    bpy.types.Scene.distool_wizard_installing = BoolProperty(default=False)
    bpy.types.Scene.distool_wizard_progress = StringProperty(default="")
    bpy.types.Scene.distool_wizard_progress_value = bpy.props.FloatProperty(default=0.0, min=0.0, max=1.0)

def unregister_installation_wizard():
    """注销安装向导 / Unregister installation wizard"""
    bpy.utils.unregister_class(DISTOOL_OT_InstallationWizard)
    bpy.utils.unregister_class(DISTOOL_OT_WizardNext)
    bpy.utils.unregister_class(DISTOOL_OT_WizardPrevious)
    bpy.utils.unregister_class(DISTOOL_OT_WizardInstall)
    bpy.utils.unregister_class(DISTOOL_OT_WizardFinish)
    bpy.utils.unregister_class(DISTOOL_PT_QuickInstallPanel)
    
    # 删除属性
    del bpy.types.Scene.distool_wizard_installing
    del bpy.types.Scene.distool_wizard_progress
    del bpy.types.Scene.distool_wizard_progress_value