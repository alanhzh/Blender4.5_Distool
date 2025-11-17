bl_info = {
    "name": "Distool: Displacement & Normal Generator",
    "author": "wsmnb12-Alan+AI",
    "version": (2, 1, 0),
    "blender": (4, 5, 0),
    "location": "Shader Editor > Sidebar > Distool",
    "description": "Advanced normal/displacement map generator with multiple gradient operators and detail enhancement. Includes automatic dependency management and installation wizard.",
    "category": "Node",
}

import bpy
import os
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter

def convert_image_to_grayscale(image_path, scene):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    
    contrast = scene.distool_disp_contrast
    gray = (gray - 127.5) * (1 + contrast) + 127.5
    gray = np.clip(gray, 0, 255)
    
    blur_strength = scene.distool_disp_blur
    if blur_strength != 0:
        sigma = abs(blur_strength)
        if blur_strength > 0:
            gray = gaussian_filter(gray, sigma=sigma)
        else:
            blurred = gaussian_filter(gray, sigma=sigma)
            gray = np.clip(2 * gray - blurred, 0, 255)
    
    if scene.distool_invert_disp:
        gray = 255 - gray
        
    return gray.astype(np.uint8)
def sobel_operator(height_map):
    """使用Sobel算子计算梯度 - 修复Y轴方向"""
    kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    kernel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
    
    # 使用cv2.filter2D进行卷积
    grad_x = cv2.filter2D(height_map, -1, kernel_x, borderType=cv2.BORDER_REPLICATE)
    grad_y = cv2.filter2D(height_map, -1, kernel_y, borderType=cv2.BORDER_REPLICATE)
    
    # 修复：反转Y轴梯度以匹配OpenGL纹理坐标系
    grad_y = -grad_y
    
    return grad_x, grad_y

def prewitt_operator(height_map):
    """使用Prewitt算子计算梯度 - 修复Y轴方向"""
    kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
    
    grad_x = cv2.filter2D(height_map, -1, kernel_x, borderType=cv2.BORDER_REPLICATE)
    grad_y = cv2.filter2D(height_map, -1, kernel_y, borderType=cv2.BORDER_REPLICATE)
    
    # 修复：反转Y轴梯度以匹配OpenGL纹理坐标系
    grad_y = -grad_y
    
    return grad_x, grad_y

def scharr_operator(height_map):
    """使用Scharr算子计算梯度（更好的旋转对称性）- 修复Y轴方向"""
    kernel_x = np.array([[-3, 0, 3], [-10, 0, 10], [-3, 0, 3]], dtype=np.float32)
    kernel_y = np.array([[-3, -10, -3], [0, 0, 0], [3, 10, 3]], dtype=np.float32)
    
    grad_x = cv2.filter2D(height_map, -1, kernel_x, borderType=cv2.BORDER_REPLICATE)
    grad_y = cv2.filter2D(height_map, -1, kernel_y, borderType=cv2.BORDER_REPLICATE)
    
    # 修复：反转Y轴梯度以匹配OpenGL纹理坐标系
    grad_y = -grad_y
    
    return grad_x, grad_y

def enhance_details(height_map, detail_level, scene):
    """多尺度细节增强"""
    if detail_level <= 6.0:
        return height_map
    
    # 创建多尺度金字塔
    levels = int(detail_level - 5.0)
    enhanced = height_map.copy()
    
    for i in range(levels):
        # 计算当前尺度的细节
        sigma = 2 ** i
        blurred = gaussian_filter(height_map, sigma=sigma)
        detail = height_map - blurred
        
        # 增强细节
        detail_strength = scene.distool_normal_detail_strength if hasattr(scene, 'distool_normal_detail_strength') else 0.5
        enhanced += detail * detail_strength * (1.0 / (i + 1))
    
    return np.clip(enhanced, 0, 1)

def generate_normal_map_from_texture(image_path, scene):
    """改进的法线贴图生成算法"""
    # 转换为灰度图并归一化
    gray = convert_image_to_grayscale(image_path, scene).astype(np.float32) / 255.0
    
    # 预处理：增强对比度
    if hasattr(scene, 'distool_normal_gamma_correct') and scene.distool_normal_gamma_correct:
        gamma = getattr(scene, 'distool_normal_gamma', 0.5)
        gray = np.power(gray, gamma)
    
    # 应用高斯模糊控制细节级别
    blur_sigma = max(0.1, abs(scene.distool_normal_blur) * 0.5 if scene.distool_normal_blur != 0 else 0.1)
    height = gaussian_filter(gray, sigma=blur_sigma)
    
    # 多尺度细节增强
    height = enhance_details(height, scene.distool_normal_level, scene)
    
    # 选择梯度算子
    gradient_type = getattr(scene, 'distool_gradient_type', 'SOBEL')
    if gradient_type == 'SOBEL':
        grad_x, grad_y = sobel_operator(height)
    elif gradient_type == 'PREWITT':
        grad_x, grad_y = prewitt_operator(height)
    elif gradient_type == 'SCHARR':
        grad_x, grad_y = scharr_operator(height)
    else:
        grad_x, grad_y = sobel_operator(height)  # 默认使用Sobel
    
    # 法线强度控制 - 修复：增加缩放因子
    scale = scene.distool_normal_strength * 1.0  # 从0.1改为1.0
    dx = grad_x * scale
    dy = grad_y * scale
    
    # 构建法线向量 - 修复：正确的切线空间法线计算
    # X轴：向右为正，Y轴：向下为正（OpenGL纹理坐标），Z轴：向外为正
    dz = np.ones_like(dx)
    
    # 构建法线向量 - 修复Y轴方向（移除了错误的负号）
    normal = np.stack((dx, dy, dz), axis=-1)
    
    # 归一化
    length = np.linalg.norm(normal, axis=2, keepdims=True)
    length = np.maximum(length, 1e-8)
    normal = normal / length
    
    # 可选的法线平滑
    if hasattr(scene, 'distool_normal_smooth') and scene.distool_normal_smooth > 0:
        smooth_sigma = scene.distool_normal_smooth * 0.1
        for i in range(3):  # 对每个通道进行平滑
            normal[..., i] = gaussian_filter(normal[..., i], sigma=smooth_sigma)
        # 重新归一化
        length = np.linalg.norm(normal, axis=2, keepdims=True)
        length = np.maximum(length, 1e-8)
        normal = normal / length
    
    # 转换为RGB颜色空间 (切线空间标准)
    normal_rgb = np.zeros_like(normal, dtype=np.float32)
    normal_rgb[..., 0] = (normal[..., 0] * 0.5 + 0.5) * 255  # R: X轴
    normal_rgb[..., 1] = (normal[..., 1] * 0.5 + 0.5) * 255  # G: Y轴  
    normal_rgb[..., 2] = (normal[..., 2] * 0.5 + 0.5) * 255  # B: Z轴
    
    # 应用通道反转选项
    if scene.distool_invert_r:
        normal_rgb[..., 0] = 255 - normal_rgb[..., 0]
    if scene.distool_invert_g:
        normal_rgb[..., 1] = 255 - normal_rgb[..., 1]
    if scene.distool_invert_height:
        normal_rgb[..., 2] = 255 - normal_rgb[..., 2]
    
    # Z-Range选项 - 推荐：使用True获得标准法线贴图
    if not scene.distool_zrange:
        normal_rgb[..., 2] = height * 255
    
    # 关键修复：OpenCV使用BGR格式，需要将RGB转换为BGR
    normal_rgb = cv2.cvtColor(normal_rgb.astype(np.uint8), cv2.COLOR_RGB2BGR)
    
    return np.clip(normal_rgb, 0, 255).astype(np.uint8)


def process_image(image_path, scene):
    base_name = os.path.splitext(os.path.basename(image_path))[0]

   
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(addon_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    normal_path = os.path.join(output_dir, base_name + "_normal.png")
    disp_path = os.path.join(output_dir, base_name + "_disp.png")

    if scene.distool_generate_normal:
        normal_img = generate_normal_map_from_texture(image_path, scene)
        cv2.imwrite(normal_path, normal_img)

    if scene.distool_generate_displacement:
        disp_img = convert_image_to_grayscale(image_path, scene)
        cv2.imwrite(disp_path, disp_img)

    return normal_path if scene.distool_generate_normal else "", disp_path if scene.distool_generate_displacement else ""


def apply_maps_to_material(context, normal_path, disp_path, strength):
    mat = context.object.active_material
    if not mat or not mat.use_nodes:
        return

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    if normal_path:
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(normal_path)
        tex.image.colorspace_settings.name = 'Non-Color'
        tex.label = "Distool Normal Map"
        norm = nodes.new("ShaderNodeNormalMap")
        norm.inputs["Strength"].default_value = strength
        links.new(tex.outputs["Color"], norm.inputs["Color"])
        bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            links.new(norm.outputs["Normal"], bsdf.inputs["Normal"])

    if disp_path:
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(disp_path)
        tex.image.colorspace_settings.name = 'Non-Color'
        tex.label = "Distool Displacement Map"
        disp = nodes.new("ShaderNodeDisplacement")
        disp.inputs["Scale"].default_value = 0.1
        links.new(tex.outputs["Color"], disp.inputs["Height"])
        out = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
        if out:
            links.new(disp.outputs["Displacement"], out.inputs["Displacement"])

    context.scene.distool_preview_normal = None
    context.scene.distool_preview_disp = None

class DISTOOL_OT_GenerateSingle(bpy.types.Operator):
    bl_idname = "distool.generate_single"
    bl_label = "Generate Maps from Selected Node"

    def execute(self, context):
        node = context.active_node
        scene = context.scene
        if node and node.type == 'TEX_IMAGE' and node.image:
            img_path = bpy.path.abspath(node.image.filepath_raw)
            normal_path, disp_path = process_image(img_path, scene)
            scene.distool_generated_normal = normal_path or ""
            scene.distool_generated_disp = disp_path or ""

            if normal_path:
                scene.distool_preview_normal = bpy.data.images.load(normal_path)
            if disp_path:
                scene.distool_preview_disp = bpy.data.images.load(disp_path)

            scene.distool_applied = False

            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Select an image texture node with a valid image.")
            return {'CANCELLED'}

class DISTOOL_OT_ApplyMaps(bpy.types.Operator):
    bl_idname = "distool.apply_maps"
    bl_label = "Apply Maps to Material"

    def execute(self, context):
        scene = context.scene
        apply_maps_to_material(context, scene.distool_generated_normal, scene.distool_generated_disp, scene.distool_normal_strength)
        scene.distool_applied = True
        return {'FINISHED'}

class DISTOOL_PT_Panel(bpy.types.Panel):
    bl_label = "Distool"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Distool"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "distool_generate_normal")
        layout.prop(scene, "distool_generate_displacement")
        
        if scene.distool_generate_displacement:  
            box = layout.box()
            box.label(text="Displacement Map Settings:")
            box.prop(scene, "distool_disp_contrast")
            box.prop(scene, "distool_disp_blur")
            box.prop(scene, "distool_invert_disp")

        layout.prop(scene, "distool_use_subfolder")

        if scene.distool_generate_normal:
            box = layout.box()
            box.label(text="Normal Map Settings:")
            
            # 基础设置
            col = box.column(align=True)
            col.prop(scene, "distool_normal_strength")
            col.prop(scene, "distool_normal_level")
            col.prop(scene, "distool_normal_blur")
            
            # 高级设置
            advanced_box = box.box()
            advanced_box.label(text="Advanced Options:")
            
            # 梯度算子选择
            advanced_box.prop(scene, "distool_gradient_type")
            
            # 预处理选项
            preprocess_box = advanced_box.box()
            preprocess_box.label(text="Preprocessing:")
            preprocess_box.prop(scene, "distool_normal_gamma_correct")
            if scene.distool_normal_gamma_correct:
                preprocess_box.prop(scene, "distool_normal_gamma")
            
            # 细节增强
            detail_box = advanced_box.box()
            detail_box.label(text="Detail Enhancement:")
            detail_box.prop(scene, "distool_normal_detail_strength")
            detail_box.prop(scene, "distool_normal_smooth")
            
            # 通道控制
            channel_box = advanced_box.box()
            channel_box.label(text="Channel Control:")
            row = channel_box.row()
            row.prop(scene, "distool_invert_r")
            row.prop(scene, "distool_invert_g")
            channel_box.prop(scene, "distool_invert_height")
            channel_box.prop(scene, "distool_zrange")

        layout.separator()

        node = context.active_node
        if(scene.distool_generate_normal or scene.distool_generate_displacement):
            if node and node.type == 'TEX_IMAGE' and node.image:
                layout.operator("distool.generate_single")
            else:
                layout.label(text="(Select an Image Texture Node)", icon='INFO')
            
            layout.operator("distool.reset_defaults", icon='FILE_REFRESH')

        layout.separator()

        if scene.distool_generate_normal and scene.distool_preview_normal:
            layout.label(text="Normal Map Preview:")
            layout.template_ID_preview(scene, "distool_preview_normal", new="image.new", open="image.open")
        if scene.distool_generate_displacement and scene.distool_preview_disp:
            layout.label(text="Displacement Map Preview:")
            layout.template_ID_preview(scene, "distool_preview_disp", new="image.new", open="image.open")

        if (scene.distool_preview_normal or scene.distool_preview_disp) and not scene.get("distool_applied", False):
            layout.operator("distool.apply_maps", icon='NODE_MATERIAL')
        
        layout.separator()
        

def auto_update_maps(self, context):
    node = context.active_node
    scene = context.scene
    
    if not scene.distool_generated_normal and not scene.distool_generated_disp:
        return

    if node and node.type == 'TEX_IMAGE' and node.image:
        img_path = bpy.path.abspath(node.image.filepath_raw)
        normal_path, disp_path = process_image(img_path, scene)
        scene.distool_generated_normal = normal_path or ""
        scene.distool_generated_disp = disp_path or ""

        if normal_path:
            scene.distool_preview_normal = bpy.data.images.load(normal_path)
        if disp_path:
            scene.distool_preview_disp = bpy.data.images.load(disp_path)

        scene.distool_applied = False

        
class DISTOOL_OT_ResetDefaults(bpy.types.Operator):
    bl_idname = "distool.reset_defaults"
    bl_label = "Reset to Default Settings"

    def execute(self, context):
        scene = context.scene

        # Normal Map Settings
        scene.distool_normal_strength = 2.5
        scene.distool_normal_level = 7.0
        scene.distool_normal_blur = 0
        
        # Advanced Settings
        scene.distool_gradient_type = 'SOBEL'
        scene.distool_normal_gamma_correct = True
        scene.distool_normal_gamma = 0.5
        scene.distool_normal_detail_strength = 0.5
        scene.distool_normal_smooth = 0.0
        
        # Channel Control
        scene.distool_invert_r = False
        scene.distool_invert_g = False
        scene.distool_invert_height = False
        scene.distool_zrange = True

        # Displacement Map Settings
        scene.distool_disp_contrast = -0.5
        scene.distool_disp_blur = 0
        scene.distool_invert_disp = False

        return {'FINISHED'}

def register():
    bpy.utils.register_class(DISTOOL_OT_GenerateSingle)
    bpy.utils.register_class(DISTOOL_OT_ApplyMaps)
    bpy.utils.register_class(DISTOOL_PT_Panel)
    bpy.utils.register_class(DISTOOL_OT_ResetDefaults)
    
    # Distool Settings
    bpy.types.Scene.distool_generate_normal = bpy.props.BoolProperty(name="Generate Normal Map", default=False)
    bpy.types.Scene.distool_generate_displacement = bpy.props.BoolProperty(name="Generate Displacement Map", default=False)
    bpy.types.Scene.distool_use_subfolder = bpy.props.BoolProperty(name="Save in Subfolder", default=True)
    
    # Normal Map Settings
    bpy.types.Scene.distool_normal_strength = bpy.props.FloatProperty(name="Strength", min=0.01, max=10.0, default=2.5, update=auto_update_maps)
    bpy.types.Scene.distool_normal_level = bpy.props.FloatProperty(name="Detail Level", min=4.0, max=10.0, default=7.0, update=auto_update_maps)
    bpy.types.Scene.distool_normal_blur = bpy.props.IntProperty(name="Blur/Sharpen", min=-32, max=32, default=0, update=auto_update_maps)
    
    # Advanced Normal Map Settings
    bpy.types.Scene.distool_gradient_type = bpy.props.EnumProperty(
        name="Gradient Operator",
        description="Select gradient calculation method",
        items=[
            ('SOBEL', 'Sobel', 'Standard Sobel operator (balanced)'),
            ('PREWITT', 'Prewitt', 'Prewitt operator (faster)'),
            ('SCHARR', 'Scharr', 'Scharr operator (better rotation symmetry)')
        ],
        default='SOBEL',
        update=auto_update_maps
    )
    
    # Preprocessing
    bpy.types.Scene.distool_normal_gamma_correct = bpy.props.BoolProperty(name="Gamma Correction", default=True, update=auto_update_maps)
    bpy.types.Scene.distool_normal_gamma = bpy.props.FloatProperty(name="Gamma", min=0.1, max=3.0, default=0.5, update=auto_update_maps)
    
    # Detail Enhancement
    bpy.types.Scene.distool_normal_detail_strength = bpy.props.FloatProperty(name="Detail Strength", min=0.0, max=2.0, default=0.5, update=auto_update_maps)
    bpy.types.Scene.distool_normal_smooth = bpy.props.FloatProperty(name="Normal Smoothing", min=0.0, max=5.0, default=0.0, update=auto_update_maps)
    
    # Channel Control
    bpy.types.Scene.distool_invert_r = bpy.props.BoolProperty(name="Invert R", default=False, update=auto_update_maps)
    bpy.types.Scene.distool_invert_g = bpy.props.BoolProperty(name="Invert G", default=False, update=auto_update_maps)
    bpy.types.Scene.distool_invert_height = bpy.props.BoolProperty(name="Invert Height", default=False, update=auto_update_maps)
    bpy.types.Scene.distool_zrange = bpy.props.BoolProperty(name="Z-Range (0 to +1)", default=True, update=auto_update_maps)
    
    # Image Previews
    bpy.types.Scene.distool_generated_normal = bpy.props.StringProperty()
    bpy.types.Scene.distool_generated_disp = bpy.props.StringProperty()
    bpy.types.Scene.distool_preview_normal = bpy.props.PointerProperty(type=bpy.types.Image)
    bpy.types.Scene.distool_preview_disp = bpy.props.PointerProperty(type=bpy.types.Image)
    bpy.types.Scene.distool_applied = bpy.props.BoolProperty(default=False)
    
    # Displacement Map Settings
    bpy.types.Scene.distool_disp_contrast = bpy.props.FloatProperty(name="Contrast", min=-1.0, max=1.0, default=-0.5, update=auto_update_maps)
    bpy.types.Scene.distool_disp_blur = bpy.props.IntProperty(name="Blur/Sharpen", min=-32, max=32, default=0, update=auto_update_maps)
    bpy.types.Scene.distool_invert_disp = bpy.props.BoolProperty(name="Invert", default=False, update=auto_update_maps)
    
    
def unregister():
    bpy.utils.unregister_class(DISTOOL_OT_GenerateSingle)
    bpy.utils.unregister_class(DISTOOL_OT_ApplyMaps)
    bpy.utils.unregister_class(DISTOOL_PT_Panel)
    bpy.utils.unregister_class(DISTOOL_OT_ResetDefaults)

    del bpy.types.Scene.distool_generate_normal
    del bpy.types.Scene.distool_generate_displacement
    del bpy.types.Scene.distool_use_subfolder
    
    # Normal Map Settings
    del bpy.types.Scene.distool_normal_strength
    del bpy.types.Scene.distool_normal_level
    del bpy.types.Scene.distool_normal_blur
    
    # Advanced Settings
    del bpy.types.Scene.distool_gradient_type
    del bpy.types.Scene.distool_normal_gamma_correct
    del bpy.types.Scene.distool_normal_gamma
    del bpy.types.Scene.distool_normal_detail_strength
    del bpy.types.Scene.distool_normal_smooth
    
    # Channel Control
    del bpy.types.Scene.distool_invert_r
    del bpy.types.Scene.distool_invert_g
    del bpy.types.Scene.distool_invert_height
    del bpy.types.Scene.distool_zrange
    
    # Image Previews
    del bpy.types.Scene.distool_generated_normal
    del bpy.types.Scene.distool_generated_disp
    del bpy.types.Scene.distool_preview_normal
    del bpy.types.Scene.distool_preview_disp
    del bpy.types.Scene.distool_applied
    
    # Displacement Map Settings
    del bpy.types.Scene.distool_disp_contrast
    del bpy.types.Scene.distool_disp_blur
    del bpy.types.Scene.distool_invert_disp

if __name__ == "__main__":
    register()