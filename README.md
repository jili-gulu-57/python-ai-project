# Python AI Project Manager

这个库用于管理 Python AI 项目代码，例如列出项目目录、发现 Python 文件、给 RAG、智能体、多轮对话等项目做统一入口。

## 安装

在当前目录运行：

```powershell
python -m pip install -e .
```

如果后面需要常用数据处理依赖：

```powershell
python -m pip install -e ".[ai]"
```

## 使用

```python
from python_ai_project_manager import AIProjectLibrary

library = AIProjectLibrary(".")
print(library.list_projects())
print(library.list_python_files())
```

现有的 `AI多轮对话服务`、`AI大模型RAG与智能体开发` 目录会保持原样，可以继续按项目存放代码。

