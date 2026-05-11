# Annual Report Workbench

年报公告抓取、PDF 下载与文本提取的一体化桌面工作台。

## 仓库

- GitHub: https://github.com/Little-pig-create/AnnualReportWorkbench
- Gitee: https://gitee.com/xiaozhusir/AnnualReportWorkbench

## 版本

- 当前版本：`1.0.0`
- 发布资产：`AnnualReportWorkbench.exe`
- 安装包：`AnnualReportWorkbench-Setup-<version>-onedir.exe`

## 功能

- 公告链接抓取
- PDF 批量下载
- PDF 文本提取
- 单阶段运行与全流程串联
- 任务暂停、继续与终止
- 实时日志、进度与图表展示
- 历史任务记录与配置同步

## 快速开始

1. 安装 Python 依赖：`pip install -r requirements.txt`
2. 安装前端依赖：`cd webui && npm install`
3. 构建前端：`npm run build`
4. 类型检查：`npm run typecheck`
5. 启动桌面程序：`python -m webview_console`

## 常用命令

- 同步版本到更新清单：`python .\scripts\sync_update_manifest.py 1.0.0`
- 构建 GUI：`powershell -ExecutionPolicy Bypass -File .\scripts\build_gui.ps1 -Mode onedir`
- 构建安装包：`powershell -ExecutionPolicy Bypass -File .\scripts\build_installer.ps1 -Mode onedir`
- 运行测试：`python -m unittest .\tests\test_release_metadata.py`

## 说明

- 当前仓库已统一为 `Annual Report Workbench` 命名。
- 更新链路已同步到新仓库地址与新发布文件名。
- `config/update.json.example` 可作为更新清单模板。
