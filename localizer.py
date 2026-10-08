#!/usr/bin/env python3
"""GitHub Desktop localizer.

A lightweight utility to back up a GitHub Desktop installation, replace common
English UI labels with Chinese translations, and restore the original files later.

This is intended for local experimentation and is not an official GitHub Desktop
translation patch.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable


DEFAULT_TRANSLATIONS = {
    "Sign In": "登录",
    "Sign out": "退出登录",
    "Settings": "设置",
    "Preferences": "偏好设置",
    "File": "文件",
    "Edit": "编辑",
    "View": "查看",
    "Repository": "仓库",
    "Branch": "分支",
    "Help": "帮助",
    "About GitHub Desktop": "关于 GitHub Desktop",
    "Exit": "退出",
    "New Repository": "新建仓库",
    "Add Local Repository": "添加本地仓库",
    "Clone Repository": "克隆仓库",
    "Open in Terminal": "在终端中打开",
    "Open in Explorer": "在资源管理器中打开",
    "Open in Finder": "在访达中打开",
    "Open in VS Code": "在 VS Code 中打开",
    "Open in External Editor": "在外部编辑器中打开",
    "Publish Repository": "发布仓库",
    "Create Pull Request": "创建拉取请求",
    "Open Pull Request": "打开拉取请求",
    "History": "历史记录",
    "Changes": "更改",
    "Commit": "提交",
    "Push": "推送",
    "Pull": "拉取",
    "Fetch": "获取",
    "Summary": "摘要",
    "Current Branch": "当前分支",
    "Default Branch": "默认分支",
    "Remote": "远程",
    "Remotes": "远程",
    "Add Remote": "添加远程",
    "Remove Remote": "移除远程",
    "Ignore": "忽略",
    "Untrack": "取消跟踪",
    "Discard changes": "放弃更改",
    "Open Repository": "打开仓库",
    "Close Repository": "关闭仓库",
    "Rename": "重命名",
    "Delete": "删除",
    "Show in Finder": "在访达中显示",
    "Copy": "复制",
    "Paste": "粘贴",
    "Cut": "剪切",
    "Select All": "全选",
    "Open": "打开",
    "Save": "保存",
    "Cancel": "取消",
    "Close": "关闭",
    "OK": "确定",
    "Apply": "应用",
    "Reset": "重置",
    "Reload": "重新加载",
    "Refresh": "刷新",
    "Check for Updates": "检查更新",
    "Install Update": "安装更新",
    "Download": "下载",
    "Authentication": "身份验证",
    "Account": "账户",
    "Accounts": "账户",
    "Email": "电子邮件",
    "Password": "密码",
    "Username": "用户名",
    "Repositories": "仓库",
    "Repository Name": "仓库名称",
    "Description": "描述",
    "Public": "公开",
    "Private": "私有",
    "Local Path": "本地路径",
    "Clone Path": "克隆路径",
    "Folder": "文件夹",
    "Home": "主页",
    "Welcome": "欢迎",
    "Continue": "继续",
    "Back": "返回",
    "Next": "下一步",
    "Finish": "完成",
    "Error": "错误",
    "Warning": "警告",
    "Success": "成功",
    "Information": "信息",
    "Loading": "加载中",
    "Search": "搜索",
    "Filter": "筛选",
}


class GitHubDesktopLocalizer:
    """Backup and replace common GitHub Desktop text with Chinese."""

    def __init__(self, app_dir: str | None = None, backup_dir: str | None = None) -> None:
        self.app_dir = self._resolve_app_dir(app_dir)
        self.backup_dir = Path(backup_dir) if backup_dir else self.app_dir.parent / "GitHubDesktopBackup"

    def _resolve_app_dir(self, app_dir: str | None) -> Path:
        if app_dir:
            p = Path(app_dir).expanduser().resolve()
            if p.exists():
                return p
            raise FileNotFoundError(f"App directory {p} does not exist.")

        candidates = []
        home = Path.home()

        if sys.platform.startswith("win"):
            candidates.extend([
                Path.home() / "AppData/Local/GitHubDesktop",
                Path("C:/Program Files/GitHub Desktop"),
                Path("C:/Program Files (x86)/GitHub Desktop"),
            ])
        elif sys.platform == "darwin":
            candidates.extend([
                Path("/Applications/GitHub Desktop.app"),
                home / "Applications/GitHub Desktop.app",
                home / "Library/Application Support/GitHub Desktop",
            ])
        else:
            candidates.extend([
                home / ".local/share/GitHubDesktop",
                home / ".config/GitHub Desktop",
                Path("/opt/GitHub Desktop"),
            ])

        for candidate in candidates:
            if candidate.exists():
                return candidate

        raise FileNotFoundError(
            "Could not find GitHub Desktop automatically. Please pass --app-dir manually."
        )

    def backup(self) -> Path:
        if self.backup_dir.exists():
            print(f"Backup already exists: {self.backup_dir}")
            return self.backup_dir

        shutil.copytree(self.app_dir, self.backup_dir)
        print(f"Backup created: {self.backup_dir}")
        return self.backup_dir

    def restore(self) -> None:
        if not self.backup_dir.exists():
            raise FileNotFoundError(f"Backup directory not found: {self.backup_dir}")

        if self.app_dir.exists():
            shutil.rmtree(self.app_dir)
        shutil.copytree(self.backup_dir, self.app_dir)
        print(f"Restored original app files from {self.backup_dir}")

    def iter_files(self, root: Path) -> Iterable[Path]:
        include_ext = {".json", ".js", ".html", ".htm", ".xml", ".txt", ".yml", ".yaml"}
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in include_ext:
                yield path

    def _translate_text(self, text: str, mapping: dict[str, str]) -> str:
        result = text
        for source, target in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
            result = result.replace(source, target)
        return result

    def _translate_json_value(self, value: Any, mapping: dict[str, str]) -> Any:
        if isinstance(value, str):
            return self._translate_text(value, mapping)
        if isinstance(value, dict):
            return {key: self._translate_json_value(v, mapping) for key, v in value.items()}
        if isinstance(value, list):
            return [self._translate_json_value(item, mapping) for item in value]
        return value

    def apply_translations(self, translations: dict[str, str], dry_run: bool = False) -> int:
        modified_count = 0
        for file_path in self.iter_files(self.app_dir):
            try:
                suffix = file_path.suffix.lower()
                original = file_path.read_text(encoding="utf-8", errors="ignore")
                translated = self._translate_text(original, translations)

                if suffix == ".json":
                    try:
                        data = json.loads(original)
                        translated_data = self._translate_json_value(data, translations)
                        updated = json.dumps(translated_data, ensure_ascii=False, indent=2)
                    except Exception:
                        updated = translated
                else:
                    updated = translated

                if updated != original:
                    if not dry_run:
                        file_path.write_text(updated, encoding="utf-8")
                    modified_count += 1
                    print(f"Will modify: {file_path}" if dry_run else f"Modified: {file_path}")
            except Exception as exc:  # pragma: no cover - best effort for unsupported files
                print(f"Skipped {file_path}: {exc}", file=sys.stderr)
        return modified_count


def load_translations(path: str | None = None) -> dict[str, str]:
    if path:
        p = Path(path).expanduser()
        with p.open("r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        if not isinstance(loaded, dict):
            raise ValueError("Translation file must contain a JSON object.")
        return {str(k): str(v) for k, v in loaded.items()}
    return DEFAULT_TRANSLATIONS


def main() -> int:
    parser = argparse.ArgumentParser(description="Localize GitHub Desktop menu text to Chinese.")
    parser.add_argument("--app-dir", help="Path to the GitHub Desktop installation directory")
    parser.add_argument("--backup-dir", help="Optional backup directory")
    parser.add_argument("--restore", action="store_true", help="Restore the original app directory from backup")
    parser.add_argument("--translations", help="Path to a JSON translation dictionary")
    parser.add_argument("--dry-run", action="store_true", help="Preview files that would be modified")
    args = parser.parse_args()

    try:
        localizer = GitHubDesktopLocalizer(app_dir=args.app_dir, backup_dir=args.backup_dir)

        if args.restore:
            localizer.restore()
            return 0

        translations = load_translations(args.translations)
        localizer.backup()
        changed = localizer.apply_translations(translations, dry_run=args.dry_run)
        print(f"Files changed: {changed}")
        if args.dry_run:
            print("Dry run complete; no files were modified.")
        else:
            print("Localization complete. Restart GitHub Desktop to apply the changes.")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

