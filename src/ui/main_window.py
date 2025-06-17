from PyQt5.QtWidgets import (QSplitter, QListWidget, QTabWidget, QHBoxLayout, QMenuBar, QMenu, QAction)
from PyQt5.QtCore import Qt
from loguru import logger
from . import json_formatter
import weakref
import src.ui.home_page as home_page

def setup_main_window(main_window, tabs):
    # 设置全局样式
    main_window.setStyleSheet("""
        /* 菜单栏样式 */
        QMenuBar {
            background-color: #f0f0f0;
            padding: 5px;
            border-bottom: 1px solid #e0e0e0;
        }
        QMenuBar::item {
            padding: 5px 10px;
            border-radius: 4px;
        }
        QMenuBar::item:selected {
            background-color: #e6f0fb;
            color: #2d7dcc;
        }
        QMenu {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 5px;
        }
        QMenu::item {
            padding: 5px 20px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #e6f0fb;
            color: #2d7dcc;
        }

        /* 状态栏样式 */
        QStatusBar {
            background-color: #f0f0f0;
            color: #555555;
            border-top: 1px solid #e0e0e0;
            padding: 5px 10px;
        }
    """)

    # 创建主分割器（左右布局）
    splitter = QSplitter()
    main_window.setCentralWidget(splitter)

    # 左侧菜单列表
    menu_list = QListWidget()
    menu_list.setStyleSheet("""
        QListWidget {
            font-size: 16px;
            background-color: #f5f5f5; /* 淡灰色背景 */
            color: #333333; /* 深灰色字体 */
            border: none; /* 移除边框 */
            outline: 0; /* 移除选中时的虚线边框 */
        }
        QListWidget::item {
            padding: 10px 20px; /* 增加内边距 */
            border-bottom: 1px solid #e0e0e0; /* 底部边框 */
        }
        QListWidget::item:selected {
            background-color: #e6f0fb; /* 选中时的淡蓝色背景 */
            color: #2d7dcc; /* 选中时的蓝色字体 */
        }
        QListWidget::item:hover {
            background-color: #e0e0e0; /* 鼠标悬停时的浅灰色背景 */
        }
    """)
    menu_list.addItems(['首页', 'JSON格式化'])

    # 右侧内容标签窗口
    tabs.addTab(home_page.HomePage(), '首页')
    tabs.addTab(json_formatter.JsonFormatterPage(), 'JSON格式化')

    # 将菜单列表和标签页添加到分割器中
    splitter.addWidget(menu_list)
    splitter.addWidget(tabs)
    
    # 设置初始大小比例为20:80
    splitter.setSizes([200, 800])
    
    # 添加窗口大小改变事件处理
    def on_resize(event):
        total_width = splitter.width()
        if total_width > 0:
            menu_width = int(total_width * 0.2)  # 菜单占20%宽度
            content_width = total_width - menu_width
            splitter.setSizes([menu_width, content_width])
            
    # 重写主窗口的resizeEvent方法
    main_window.resizeEvent = lambda event: on_resize(event)

    # 使用弱引用避免循环引用
    main_window_ref = weakref.ref(main_window)
    tabs_ref = weakref.ref(tabs)
    menu_list_ref = weakref.ref(menu_list)
    
    # 添加双向信号绑定
    def on_tab_changed(index):
        logger.debug(f"标签页切换到索引: {index}")
        try:
            # 获取弱引用对象并验证
            main_window = main_window_ref()
            if main_window is None:
                logger.debug("主窗口引用已失效")
                return
                
            if not hasattr(main_window, '_tabs'):
                logger.warning("主窗口缺少_tabs属性")
                return
            
            menu_list = menu_list_ref()
            if menu_list is None or not isinstance(menu_list, QListWidget):
                logger.debug("菜单列表引用已失效或类型错误")
                return
            
            # 确保索引有效
            if 0 <= index < menu_list.count():
                menu_list.setCurrentRow(index)
            else:
                logger.warning(f"无效的菜单索引: {index}")
                
        except Exception as e:
            logger.error(f"更新菜单项时发生错误: {e}", exc_info=True)
    
    def on_menu_changed(index):
        logger.debug(f"菜单项切换到索引: {index}")
        try:
            # 获取弱引用对象并验证
            main_window = main_window_ref()
            if main_window is None:
                logger.debug("主窗口引用已失效")
                return
                
            if not hasattr(main_window, '_tabs'):
                logger.warning("主窗口缺少_tabs属性")
                return
            
            tabs = tabs_ref()
            if tabs is None or not isinstance(tabs, QTabWidget):
                logger.debug("标签页引用已失效或类型错误")
                return
            
            # 确保索引有效
            if 0 <= index < tabs.count():
                tabs.setCurrentIndex(index)
            else:
                logger.warning(f"无效的标签页索引: {index}")
                
        except Exception as e:
            logger.error(f"更新标签页时发生错误: {e}", exc_info=True)
    
    # 连接信号
    tabs.currentChanged.connect(on_tab_changed)
    menu_list.currentRowChanged.connect(on_menu_changed)
    
    # 设置默认选中项
    menu_list.setCurrentRow(0)
    tabs.setCurrentIndex(0)
    logger.debug("currentRowChanged信号连接后")

    # 保存引用以防止提前销毁
    main_window._menu_list = menu_list
    main_window._tabs = tabs
    main_window._splitter = splitter
    
    # 添加清理方法
    def cleanup():
        logger.debug("执行清理操作")
        try:
            tabs = tabs_ref()
            if tabs is not None:
                tabs.currentChanged.disconnect(on_tab_changed)
            menu_list = menu_list_ref()
            if menu_list is not None:
                menu_list.currentRowChanged.disconnect(on_menu_changed)
        except Exception as e:
            logger.error(f"清理过程中发生错误: {e}")
    
    # 将清理方法与窗口关闭事件关联
    main_window.destroyed.connect(cleanup)

    # 添加菜单栏
    menubar = main_window.menuBar()
    file_menu = menubar.addMenu('文件')
    help_menu = menubar.addMenu('帮助')

    # 添加状态栏
    status_bar = main_window.statusBar()
    status_bar.showMessage('就绪')
