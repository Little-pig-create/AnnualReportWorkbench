# Annual Report Workbench

一个用于年报公告链接抓取、PDF 下载和文本提取的桌面工具。

## 项目简介

Annual Report Workbench 基于 Python、Vue 和 pywebview 构建，面向年报数据的批量处理场景，提供从公告链接抓取到 PDF 下载、文本提取的一体化工作流。

相比命令行脚本，它更适合需要持续观察进度、查看日志、保留历史记录和反复调整配置的桌面使用方式。

![Annual Report Workbench 预览图](assets/gpt-image-4.png)

## 主要功能

- 公告链接抓取
- PDF 批量下载
- PDF 文本提取
- 单阶段执行与完整流程执行
- 任务暂停、继续与终止
- 实时日志、阶段进度和图表展示
- 历史任务记录与统计信息查看

## 当前版本

- 版本号：`1.0.3`

## 快速开始

1. 安装 Python 依赖：`pip install -r requirements.txt`
2. 安装前端依赖：`cd webui && npm install`
3. 构建前端：`npm run build`
4. 类型检查：`npm run typecheck`
5. 启动桌面程序：`python -m webview_console`

## 常用命令

- 同步版本到更新清单：`python .\scripts\sync_update_manifest.py 1.0.3`
- 构建 GUI：`powershell -ExecutionPolicy Bypass -File .\scripts\build_gui.ps1 -Mode onedir`
- 构建安装包：`powershell -ExecutionPolicy Bypass -File .\scripts\build_installer.ps1 -Mode onedir`
- 运行发布元数据测试：`python -m unittest .\tests\test_release_metadata.py`

## 1.0.3 更新说明

- 重构桌面端工作台布局，按钮区升级为可折叠侧边栏，并补充日出 / 深夜模式一体化切换
- 新增吸顶任务进度栏，压缩空闲态体积，优化执行中状态、阶段进度和关键指标的一眼可读性
- 统一工作区、任务总览、日志、历史记录和关于页的字号、卡片密度与留白节奏，减少多余滚动
- 深度优化深夜模式、分页器、侧边栏折叠动画和关于页版本更新区的层级与对齐表现

## 仓库地址

- GitHub: [Little-pig-create/AnnualReportWorkbench](https://github.com/Little-pig-create/AnnualReportWorkbench)
- Gitee: [xiaozhusir/AnnualReportWorkbench](https://gitee.com/xiaozhusir/AnnualReportWorkbench)
