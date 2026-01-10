# 🖱️ 剪贴板历史管理器

一个智能的Windows剪贴板历史管理工具，支持在输入框中通过右键快速访问和粘贴历史复制内容。

## ✨ 核心功能

- 📋 **自动记录复制历史** - 监控剪贴板变化，自动保存复制历史（最多20条）
- 🖱️ **智能右键触发** - 在输入框中单击右键调出菜单，选中文字时不干扰正常复制
- 💾 **持久化存储** - 历史记录保存到本地，重启后依然可用
- 🎯 **快速粘贴** - 单击选择历史内容即可粘贴到当前位置
- 🎨 **友好界面** - 简洁直观的图形界面，支持鼠标滚轮
- 🔍 **广泛支持** - 支持记事本、VSCode、Word、浏览器等各类软件
- 📦 **便携免安装** - 单个exe文件，可直接运行
- 🚀 **开箱即用** - 无需Python环境，复制到任何Windows电脑即可使用

## 🎮 使用方法

### 启动程序

**使用便携版（推荐）:**
1. 下载 `ClipboardManager_Portable` 文件夹
2. 双击 `ClipboardManager.exe` 或 `启动程序.bat`

**或从源码运行:**
```bash
python clipboard_manager.py
```

### 基本操作

1. **正常复制文本** - 使用 Ctrl+C 或右键复制，内容会自动记录
2. **在输入框中单击右键** - 光标在输入框时，单击鼠标右键调出历史菜单
3. **选择内容** - 单击鼠标左键选择要粘贴的内容
4. **自动粘贴** - 选中的内容会自动粘贴到光标位置

### 智能识别

- ✅ **未选中文字** + 右键 → 弹出粘贴菜单
- ✅ **选中文字** + 右键 → 不弹菜单，允许正常复制
- ✅ **非输入框** + 右键 → 显示系统右键菜单

## 📝 示例场景

**场景1: 填写重复表单**
- 复制姓名 -> 填写姓名字段
- 复制地址 -> 填写地址字段
- 复制电话 -> 填写电话字段
- 需要再次填写姓名时,双击右键选择之前复制的姓名,无需重新复制!

**场景2: 代码开发**
- 复制函数名A -> 使用
- 复制函数名B -> 使用
- 需要再次使用函数名A时,双击右键选择历史记录中的A

**场景3: 文档编辑**
- 复制多个段落或引用
- 在不同位置需要粘贴之前复制的内容
- 双击右键选择任意历史内容粘贴

## ⚙️ 配置说明

程序会在运行目录创建 `clipboard_config.json` 文件,保存历史记录。

你可以修改 `clipboard_manager.py` 中的参数:

```python
manager = ClipboardManager(max_history=20)  # 修改最大历史记录数
```

双击间隔时间调整:
```python
self.double_click_interval = 0.5  # 修改双击间隔时间(秒)
```

## 🔧 技术栈

- **pyperclip** - 剪贴板操作
- **pynput** - 全局鼠标监听和键盘模拟
- **tkinter** - 图形界面

## 📌 注意事项

1. 程序需要在后台持续运行才能监控剪贴板
2. 首次运行需要安装依赖包
3. 只记录文本内容,不支持图片等其他格式
4. 菜单会在失去焦点或按ESC时自动关闭

## 🎯 快捷键

- **双击右键** - 打开历史菜单
- **ESC** - 关闭菜单
- **鼠标点击** - 选择并粘贴
- **Ctrl+C** - 退出程序(在命令行窗口)

## 🐛 常见问题

**Q: 双击右键没有反应?**
A: 确保两次点击间隔在0.5秒内,可以调整 `double_click_interval` 参数

**Q: 粘贴没有反应?**
A: 确保目标位置是可输入的文本框,且光标已聚焦

**Q: 程序崩溃或报错?**
A: 检查是否正确安装了所有依赖包,尝试重新安装 requirements.txt

## 🔨 开发者指南

### 从源码打包成可执行文件

如果你想自己打包程序，按以下步骤操作：

#### 1. 安装打包工具

```bash
pip install -r requirements.txt
```

这会安装包括PyInstaller在内的所有依赖。

#### 2. 打包程序

**方法1: 使用自动脚本（推荐）**
```bash
build.bat
```

这会自动清理、打包并生成 `dist\ClipboardManager.exe`

**方法2: 手动打包**
```bash
pyinstaller clipboard_manager.spec --clean
```

#### 3. 创建便携版发布包

```bash
create_portable.bat
```

这会创建一个完整的 `ClipboardManager_Portable` 文件夹，包含：
- ClipboardManager.exe（主程序）
- 使用说明.txt
- 添加到开机启动.bat
- 取消开机启动.bat
- 启动程序.bat

#### 4. 分发到其他电脑

将 `ClipboardManager_Portable` 整个文件夹复制到其他Windows电脑即可使用，无需任何配置！

### 项目结构

```
rightclick/
├── clipboard_manager.py      # 主程序源码
├── requirements.txt           # Python依赖列表
├── clipboard_manager.spec     # PyInstaller配置文件
├── build.bat                  # 自动打包脚本
├── create_portable.bat        # 创建便携版脚本
├── start.bat                  # Python版启动脚本
├── README.md                  # 项目文档
├── clipboard_config.json      # 历史记录存储（运行后生成）
├── dist/                      # 打包输出目录
│   └── ClipboardManager.exe
└── ClipboardManager_Portable/ # 便携版发布包
    ├── ClipboardManager.exe
    ├── 使用说明.txt
    ├── 添加到开机启动.bat
    ├── 取消开机启动.bat
    └── 启动程序.bat
```

## 📄 许可证

MIT License - 自由使用和修改

---

💡 **使用提示**:
- 建议将程序添加到开机自启动,这样就能一直享受便捷的剪贴板历史功能
- 如需在多台电脑使用,直接复制整个便携版文件夹即可
- 历史记录保存在程序所在目录的 `clipboard_config.json` 文件中
