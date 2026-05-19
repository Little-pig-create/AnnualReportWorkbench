# Annual Report Workbench

Annual Report Workbench 是一个面向年报数据处理的桌面工具，基于 Python、Vue 和 pywebview 构建，用于公告链接抓取、PDF 下载、文本提取、任务执行与结果查看。

## 项目简介

这个工具适合需要持续观察进度、查看日志、保留历史记录并反复调整配置的年报工作场景。相比纯命令行脚本，它把常用流程整合到一个桌面界面里，便于批量处理与结果核对。

## 核心功能

- 公告链接抓取
- PDF 批量下载
- PDF 文本提取
- 单阶段执行与完整流程执行
- 任务暂停、继续与终止
- 实时日志、阶段进度和图表展示
- 历史任务记录与统计信息查看

## 当前版本

- `1.0.4`

## 快速开始

1. 安装 Python 依赖：`pip install -r requirements.txt`
2. 安装前端依赖：`cd webui && npm install`
3. 构建前端：`npm run build`
4. 类型检查：`npm run typecheck`
5. 启动桌面程序：`python -m webview_console`

## 常用命令

- 同步版本与更新清单：`python .\scripts\sync_update_manifest.py 1.0.4`
- 构建 GUI：`powershell -ExecutionPolicy Bypass -File .\scripts\build_gui.ps1 -Mode onedir`
- 构建安装包：`powershell -ExecutionPolicy Bypass -File .\scripts\build_installer.ps1 -Mode onedir`
- 运行发布元数据测试：`python -m unittest .\tests\test_release_metadata.py`

## 发布产物

- GitHub：<https://github.com/Little-pig-create/AnnualReportWorkbench>
- Gitee：<https://gitee.com/xiaozhusir/AnnualReportWorkbench>

## 更新说明

当前版本重点包括：

- 重构桌面端窗口布局，去除自定义顶栏，保留原生窗体体验
- 优化深色模式、页面切换与动画过渡
- 调整任务面板、图表和日志区域的展示方式
- 修正前端与桥接层在重建后可能出现的接口不一致问题

