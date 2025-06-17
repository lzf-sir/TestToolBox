from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget
from loguru import logger
from src.ui.main_window import setup_main_window


class TestToolBoxApp(QMainWindow):
    """TestToolBox主应用窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TestToolBox")
        # 设置更合适的默认窗口大小
        self.setGeometry(100, 100, 1000, 700)  # 宽度增加到1000px，高度增加到700px

        # 创建 Tab Widget
        self.tabs = QTabWidget()
        
        # 设置中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 添加初始标签
        layout.addWidget(QLabel("欢迎使用TestToolBox - 测试工具集合"))

        # 初始化UI
        setup_main_window(self, self.tabs)

        # 保存 tabs 的引用以防止过早销毁
        self._tabs = self.tabs

        logger.info("TestToolBox应用已启动")
