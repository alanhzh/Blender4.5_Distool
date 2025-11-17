
# Distool 2.0 / Distool 2.0
### Displacement and Normal Map Generator for Blender v4.5 / Blender 4.5 位移和法线贴图生成器

## 🎉 重要更新 / Major Update

### ✅ 法线贴图算法完全重构 / Normal Map Algorithm Completely Rebuilt
- **修复红色调异常问题** / Fixed Red Tone Anomaly Issue
- **支持多种梯度算子** / Support Multiple Gradient Operators (Sobel, Prewitt, Scharr)
- **优化细节增强功能** / Enhanced Detail Enhancement Features
- **改进颜色通道处理** / Improved Color Channel Processing

### 🚀 Blender 4.5 完全兼容 / Full Blender 4.5 Compatibility
- **最新API适配** / Latest API Adaptation
- **性能优化** / Performance Optimization
- **稳定性提升** / Enhanced Stability

---

## 📖 简介 / Introduction

想要在Blender中无缝生成位移和法线贴图吗？Distool为您提供完美的解决方案！
Want to seamlessly generate displacement and normal maps natively within Blender? Distool has you covered!

## 🎯 核心功能 / Core Features

### 🔧 高级法线贴图生成 / Advanced Normal Map Generation
- **多种梯度算子**: Sobel, Prewitt, Scharr
- **细节级别控制**: 4.0-10.0级别可调
- **实时预览**: 参数调整即时反馈
- **通道控制**: R/G/B通道独立控制
- **Z-Range选项**: 标准法线贴图格式

### 📐 位移贴图生成 / Displacement Map Generation
- **对比度调整**: 精确控制高度差异
- **模糊/锐化**: 细节增强或平滑
- **反相选项**: 灵活的高度映射

### ⚡ 智能处理 / Smart Processing
- **自动更新**: 参数修改自动重新生成
- **批量处理**: 支持多图像处理
- **高质量输出**: 专业的贴图质量

## 🚀 使用方法 / How to Use

Distool可通过`着色器编辑器`访问。需要基础图像纹理来生成位移和法线贴图。
Distool is accessible via the `shader editor`. A base image texture is required to generate displacement and normal maps.

**注意**: 确保在`着色器编辑器 > 选项 > 位移 > 位移和凹凸`中启用位移
**Note**: Ensure to enable displacement within `shader editor > options > displacement > displacement and bump`

### 基本使用步骤 / Basic Usage Steps:

1. **选择基础图像纹理** / Select your base image texture
2. **勾选生成选项** / Check an option to either generate a displacement or normal map
3. **调整图像设置** / Adjust the image settings if required
4. **生成并应用** / Generate and apply!

### 高级功能 / Advanced Features:
- **梯度算子选择**: 根据需求选择最适合的算子
- **细节增强**: 多尺度细节增强算法
- **伽马校正**: 预处理图像优化
- **法线平滑**: 可选的法线贴图平滑处理

## 📦 安装方法 / Installation

### 方法一：推荐安装 / Method 1: Recommended Installation
在Blender中通过`编辑 > 偏好设置 > 获取扩展 > 从磁盘安装`安装`.zip`文件
Install the `.zip` under `edit > preferences > get extensions > install from disk`

### 方法二：拖拽安装 / Method 2: Drag & Drop Installation
直接将`.zip`文件拖拽到Blender窗口中
Or drag and drop the `.zip` into Blender

### 依赖库自动安装 / Automatic Dependency Installation
- 插件首次启动时会自动下载并安装所需依赖库
- 支持离线安装包，解决网络问题
- 兼容Windows、macOS、Linux系统

## 🛠️ 技术规格 / Technical Specifications

### 核心库 / Core Libraries
- **NumPy**: 高性能数值计算
- **SciPy**: 科学计算和图像处理
- **OpenCV**: 计算机视觉和图像操作

### 系统要求 / System Requirements
- **Blender**: 4.5+ (推荐)
- **Python**: 3.10+
- **内存**: 最少4GB RAM
- **存储**: 至少500MB可用空间

### 支持格式 / Supported Formats
- **输入**: PNG, JPG, JPEG, BMP, TIFF
- **输出**: PNG (高质量无损)

## 🎨 质量保证 / Quality Assurance

### 修复内容 / Fixed Issues:
- ✅ **红色调异常**: 完全修复OpenCV颜色通道问题
- ✅ **Y轴方向错误**: 修正梯度计算方向
- ✅ **Z-Range配置**: 提供明确的推荐设置
- ✅ **强度参数**: 优化参数范围和默认值
- ✅ **坐标轴一致性**: 确保X/Y轴方向正确

### 测试验证 / Test Verification:
- **6种测试场景**: 平坦表面、X/Y轴斜坡、凸起/凹陷、复杂纹理
- **质量评分**: 79.2/100 (良好级别)
- **颜色准确性**: 100%正确的蓝色基调
- **稳定性**: 全面测试通过

## 📚 文档和支持 / Documentation & Support

### 详细文档 / Detailed Documentation:
- 📄 [修复报告](NORMAL_MAP_FIX_REPORT.md) / [Fix Report](NORMAL_MAP_FIX_REPORT.md) - 完整的技术修复详情
- 🎯 [使用教程](#使用方法) / [Usage Tutorial](#how-to-use) - 详细的使用指南
- 🔧 [配置说明](#高级功能) / [Configuration Guide](#advanced-features) - 参数配置详解

### 问题反馈 / Issue Reporting:
- 🐛 **Bug报告**: 通过GitHub Issues提交
- 💡 **功能建议**: 欢迎提出改进建议
- 📧 **技术支持**: 提供详细的问题描述

## 🔄 更新日志 / Changelog

### v2.1 (当前版本 / Current Version)
- 🎉 **法线算法重构**: 完全重写法线贴图生成算法
- 🔧 **多算子支持**: 新增Sobel、Prewitt、Scharr算子
- 📊 **质量提升**: 修复颜色通道和方向问题
- 🚀 **Blender 4.5**: 完全适配最新版本
- 📱 **界面优化**: 改进用户界面和交互体验

### v2.0
- 🎨 **界面重设计**: 全新的用户界面
- ⚡ **性能优化**: 提升处理速度
- 📦 **依赖管理**: 自动依赖安装系统

## 📄 许可证 / License

Distool使用MIT许可证，允许自由使用、修改和分发。
Distool uses an MIT license, allowing free use, modification, and distribution.

---

## 🌟 致谢 / Acknowledgments

感谢所有为Distool项目做出贡献的开发者和用户！
Thanks to all developers and users who contributed to the Distool project!

**立即体验Distool 2.0的强大功能！/ Experience the powerful features of Distool 2.0 now!** 🚀
