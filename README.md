# GitHub Desktop Localizer

这是一个针对 GitHub Desktop 的本地汉化脚本，用于：

- 自动查找 GitHub Desktop 安装目录
- 备份原始文件
- 扫描常见资源文件和文本内容
- 把英文菜单/界面文本替换成中文
- 支持恢复原始版本

注意：
- 这是一个本地实验性工具，不是 GitHub 官方汉化补丁。
- 不同版本的 GitHub Desktop 文件组织结构可能略有不同。
- 该脚本主要适合作为“资源文本替换”的基础工具，便于你按版本自行扩展词库。

## 目录结构

- `localizer.py`：主脚本
- `translations.json`：翻译词典
- `README.md`：使用说明

## 用法

### 1) 关闭 GitHub Desktop

先退出 GitHub Desktop，避免文件被占用。

### 2) 运行汉化脚本

Windows：

```powershell
py localizer.py --dry-run
```

macOS / Linux：

```bash
python3 localizer.py --dry-run
```

`--dry-run` 会预览将被修改的文件，但不会实际写入。

### 3) 执行实际汉化

Windows：

```powershell
py localizer.py
```

macOS / Linux：

```bash
python3 localizer.py
```

脚本会：

- 自动查找 GitHub Desktop 安装目录
- 创建备份目录
- 替换常见文本内容
- 提示你重启应用查看效果

### 4) 恢复原始文件

```bash
python3 localizer.py --restore
```

或 Windows：

```powershell
py localizer.py --restore
```

## 高级用法

### 指定安装目录

```bash
python3 localizer.py --app-dir "/Applications/GitHub Desktop.app"
```

### 使用自定义翻译表

```bash
python3 localizer.py --translations ./translations.json
```

## 常见问题

### 1. 提示未找到 GitHub Desktop

说明软件没有安装在标准目录，或者是自定义安装位置。使用：

```bash
python3 localizer.py --app-dir /path/to/GitHubDesktop
```

### 2. 脚本运行成功但界面没变化

常见原因：

- 你的 GitHub Desktop 版本与字典不匹配
- 文本位于 Electron 的 `.asar` 资源包内
- 菜单文本被打包成二进制资源

此时需要进一步扩展脚本逻辑，定位具体资源文件。该脚本适合作为初版基础工具。

### 3. 想恢复原始版本

执行：

```bash
python3 localizer.py --restore
```

## 说明

如果你希望，我下一步可以继续为你完善成：

- 适配 GitHub Desktop 更高版本的精确资源路径
- 处理 Electron `.asar` 文件的直接替换逻辑
- 增加更完整的中文菜单翻译词库
- 生成一个完整的 GitHub 仓库项目结构和说明

