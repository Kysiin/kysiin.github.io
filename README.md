# KYSIIN.ARCHIVE

个人资料仓库：一门课一个入口，课内再分 **章节 / 专题 / 实验**。首页是课程索引（`index.html`），
每门课有自己的索引页，按分区列出文章，并附完整文件表（名称、类型、体积、修改时间）。

## 结构

```
index.html                 首页（课程索引）
collections/<课程>/index.html   每门课一个索引页（含 章节 / 专题 / 实验 三个分区）
collections/<课程>/files/       这门课的文件与文章
assets/                    endfield-ui 套件与自托管字体
files/                     单独提供的下载件（动画 PDF / DOCX）
```

## 收录范围

课程资料按课程归档在 `collections/` 下；一门课可以由多份来源合成（例如「计算机动画」
= 复习资料 + ClothLab 源码/产出），页面由构建脚本聚合，物理目录保持分开。

**不发布**：课程作业的源码（.cpp / .h / .cc / .hh / .sh）与所有压缩包只在本地保留，
站上只放报告、笔记与 PDF；ClothLab 是自制项目，源码照常发布。

**未收录**（约 117 MB）：部分实验产出文件体积较大，未放入仓库，
只在所属课程页的文件表里登记。

## 本地查看

请用一个静态服务器打开，不要直接双击 `index.html`：页面用的是 ES module 与
`fetch('assets/search.json')`，在 `file://` 下会被浏览器拦掉，主题切换和搜索会失效。

```bash
python -m http.server 8000
# 打开 http://127.0.0.1:8000/
```

## 发布到 GitHub Pages

1. 新建仓库，把本目录推上去（`git init && git add . && git commit -m "init"`）；
2. Settings → Pages → Source 选 `Deploy from a branch`，分支 `main`、目录 `/ (root)`；
3. 稍等片刻，访问 `https://<用户名>.github.io/<仓库名>/`。

仓库根的 `.nojekyll` 让 Pages 原样发布，不走 Jekyll（否则下划线开头的路径会被吞掉）。

## 更新索引

本站不是手改的，而是由上一层工作区里的 `tools/build_site.py` 生成的；`tools/` 下这几份
脚本只是随站点一起发布的副本，仅供查看，不要在 `site/` 里运行它们。要更新，回到工作区根目录：

```bash
python tools/build_site.py
```

它会清空并重建整个 `site/`（首页、各课程索引页、文章页都在内），`site/` 里的手工改动不会保留。

统计：16 门课 · 353 个文件入库 · 108.8 MB · 另有 67 个文件未入库。
