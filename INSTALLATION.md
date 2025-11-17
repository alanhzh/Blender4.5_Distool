# Distool 2.1 安装指南

## 📋 目录
- [系统要求](#系统要求)
- [快速安装](#快速安装)
- [详细安装步骤](#详细安装步骤)
- [依赖管理](#依赖管理)
- [离线安装](#离线安装)
- [常见问题](#常见问题)
- [技术支持](#技术支持)

---

## 🖥️ 系统要求

### 最低配置
- **Blender**: 4.5.0 或更高版本
- **操作系统**: Windows 10/11, macOS 10.15+, Linux
- **内存**: 4GB RAM (推荐 8GB+)
- **存储空间**: 500MB 可用空间

### Python环境
- **Python版本**: 3.10+ (Blender内置)
- **必需库**: numpy, scipy, opencv-python

---

## 🚀 快速安装

### 方法一：Blender插件商店安装（推荐）
1. 打开Blender 4.5+
2. 进入 `编辑` > `偏好设置` > `插件`
3. 搜索 "Distool"
4. 点击安装并启用

### 方法二：手动安装
1. 下载 `Distool_v2.1.zip`
2. 在Blender中：`编辑` > `偏好设置` > `插件` > `安装`
3. 选择下载的zip文件
4. 启用Distool插件

---

## 📖 详细安装步骤

### 步骤1：安装插件
1. **下载插件**
   ```
   访问 GitHub: https://github.com/alanhzh/Blender4.5_Distool
   下载最新版本: Distool_v2.1.zip
   ```

2. **在Blender中安装**
   - 打开Blender
   - 进入 `编辑` > `偏好设置`
   - 选择 `插件` 选项卡
   - 点击 `安装` 按钮
   - 选择下载的zip文件
   - 勾选启用Distool插件

### 步骤2：运行安装向导
1. **启动安装向导**
   - 在Shader Editor中，打开侧边栏 (`N`键)
   - 找到 `Distool` 标签
   - 点击 `快速安装` 按钮
   - 或在插件设置中找到 `Distool Installation Wizard`

2. **跟随向导步骤**
   - **欢迎页面**: 了解插件功能
   - **系统检查**: 验证Blender版本和系统环境
   - **依赖检查**: 检查必需的Python库
   - **依赖安装**: 自动安装缺失的库
   - **完成**: 确认安装成功

---

## 🔧 依赖管理

### 自动依赖管理（推荐）
Distool 2.1 提供智能依赖管理系统：

#### 功能特性
- ✅ **自动检测**: 启动时自动检查依赖状态
- ✅ **一键安装**: 点击按钮自动安装缺失库
- ✅ **版本兼容**: 确保库版本与Blender兼容
- ✅ **错误处理**: 智能处理安装过程中的错误

#### 使用方法
1. **检查依赖状态**
   ```
   插件设置 > Distool Dependency Manager
   查看各库的安装状态（✅已安装 / ❌缺失）
   ```

2. **安装依赖**
   ```
   点击 "Install Missing Dependencies" 按钮
   等待后台安装完成
   重启Blender以生效
   ```

### 手动依赖安装
如果自动安装失败，可以手动安装：

#### 方法1：使用pip
```bash
# 在Blender的Python环境中
import subprocess
import sys

# 安装numpy
subprocess.run([sys.executable, "-m", "pip", "install", "numpy"])

# 安装scipy
subprocess.run([sys.executable, "-m", "pip", "install", "scipy"])

# 安装opencv-python
subprocess.run([sys.executable, "-m", "pip", "install", "opencv-python"])
```

#### 方法2：使用Blender控制台
```
# 打开Blender Python控制台
import bpy
import sys
import subprocess

# 执行安装命令
subprocess.run([sys.executable, "-m", "pip", "install", "numpy scipy opencv-python"])
```

---

## 📦 离线安装

### 离线安装包创建
1. **创建离线包**
   ```
   插件设置 > Distool Offline Package Manager
   点击 "Create Offline Package"
   选择保存位置
   等待下载完成
   ```

2. **离线包内容**
   - 所有必需的Python库（.whl文件）
   - 安装脚本
   - 版本信息文件

### 离线安装步骤
1. **准备离线包**
   - 在有网络的机器上创建离线包
   - 将离线包复制到目标机器

2. **执行离线安装**
   ```
   插件设置 > Distool Offline Package Manager
   点击 "Install from Offline Package"
   选择离线包文件
   等待安装完成
   ```

---

## ❓ 常见问题

### Q1: 插件安装后无法启用？
**A**: 检查以下几点：
- Blender版本是否为4.5+
- 插件文件是否完整
- 控制台是否有错误信息

### Q2: 依赖安装失败？
**A**: 尝试以下解决方案：
- 检查网络连接
- 使用管理员权限运行Blender
- 手动安装依赖库
- 使用离线安装包

### Q3: 找不到Distool面板？
**A**: 确认以下设置：
- 插件已启用
- 在Shader Editor中工作
- 按N键打开侧边栏
- 查找Distool标签

### Q4: 生成的法线贴图颜色异常？
**A**: 检查以下设置：
- 输入图片格式是否正确
- 法线强度设置是否合适
- 通道反转选项是否正确

### Q5: 性能问题或卡顿？
**A**: 优化建议：
- 降低图片分辨率
- 调整法线级别设置
- 关闭不必要的实时预览

---

## 🛠️ 技术支持

### 获取帮助
- **GitHub Issues**: https://github.com/alanhzh/Blender4.5_Distool/issues
- **文档**: 查看README.md了解更多功能
- **社区**: Blender Artists论坛

### 错误报告
提交错误时请包含：
1. Blender版本信息
2. 操作系统信息
3. 错误截图或日志
4. 重现步骤

### 系统信息收集
```
在Blender中：
帮助 > 系统信息 > 复制
```

---

## 📝 更新日志

### v2.1.0 (当前版本)
- ✨ 新增自动依赖管理系统
- ✨ 新增安装向导界面
- ✨ 新增离线安装包支持
- 🐛 修复法线贴图红色调异常
- 🔧 优化Blender 4.5兼容性
- 📚 完善文档和用户指南

### v2.0.0
- 🎉 重大版本更新
- 🔧 重构法线贴图算法
- ✨ 支持多种梯度算子
- 🎨 改进用户界面

---

## 🎯 使用提示

### 最佳实践
1. **图片准备**: 使用高对比度的灰度图
2. **参数调整**: 从默认值开始，逐步调整
3. **预览**: 使用小尺寸图片快速预览效果
4. **批量处理**: 保存常用参数设置

### 性能优化
- 使用适当的图片分辨率（建议不超过4K）
- 合理设置法线级别（6-12为最佳范围）
- 关闭不必要的实时预览功能

---

**🎉 感谢使用Distool 2.1！如有问题，请随时联系技术支持。**