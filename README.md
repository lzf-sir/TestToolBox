# TestToolBox

## 项目概述
TestToolBox是基于PyQt5框架开发的模块化测试工具箱，采用MVC架构设计，提供可扩展的插件式工具管理。本项目旨在为测试工程师提供一个统一的、可扩展的测试工具平台。

## 系统架构
### MVC架构
- Model: 数据模型层，处理业务逻辑和数据操作
- View: 视图层，基于PyQt5实现的用户界面
- Controller: 控制层，处理用户输入和业务逻辑协调

### 目录结构
```
TestToolBox/
├── main.py              # 应用程序入口
├── requirements.txt     # 项目依赖
├── README.md           # 项目文档
├── logs/               # 日志文件目录
└── src/                # 源代码目录
    ├── app.py          # 主应用程序
    ├── logger.py       # 日志模块
    └── tools/          # 工具插件目录
```

## 核心功能
### 日志系统
- 使用loguru实现多线程安全日志
- 每日自动滚动日志文件（保留7天）
- 控制台彩色日志输出
- 支持DEBUG/INFO/WARNING/ERROR多级别日志

```python
# 日志初始化代码示例
from src.logger import setup_logger
logger = setup_logger()
logger.info('系统初始化完成')
```

### 插件系统
- 支持动态加载和卸载工具插件
- 插件接口标准化
- 插件配置管理
- 插件依赖管理

## 快速开始
### 环境要求
- Python 3.8+
- PyQt5 5.15.7
- loguru 0.6.0
- pytest 7.3.1

### 安装步骤
1. 克隆项目
```bash
git clone https://github.com/yourrepo/TestToolBox.git
cd TestToolBox
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行应用
```bash
python main.py
```

## 开发者指南
### 日志配置参数
| 参数 | 类型 | 默认值 | 说明 |
|------|------|-------|-----|
| rotation | str | 00:00 | 每日午夜滚动日志 |
| retention | str | 7 days | 日志保留时长 |
| encoding | str | utf-8 | 文件编码格式 |

### 开发规范
1. 代码风格
   - 遵循PEP 8规范
   - 使用类型注解
   - 编写完整的文档字符串

2. 日志使用
   - 使用loguru进行日志记录
   - 合理使用日志级别
   - 记录关键操作和错误信息

3. 测试要求
   - 编写单元测试
   - 保持测试覆盖率
   - 使用pytest进行测试

### 插件开发
1. 插件结构
```python
class ToolPlugin:
    def __init__(self):
        self.name = "插件名称"
        self.version = "1.0.0"
        
    def initialize(self):
        """插件初始化"""
        pass
        
    def execute(self, *args, **kwargs):
        """插件执行"""
        pass
```

2. 插件注册
```python
from src.plugin_manager import register_plugin

@register_plugin
class MyTool(ToolPlugin):
    pass
```

## 问题反馈
请提交issue至[项目仓库](https://github.com/yourrepo)

## 版本历史
- v1.0.0 (2024-03-21)
  - 初始版本发布
  - 实现基础框架
  - 集成日志系统
