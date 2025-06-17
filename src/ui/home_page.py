from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 14px;
                background-color: #f5f7fa;
                color: #333333;
            }
            QLabel {
                color: #333333;
            }
            QLabel[style*="font-weight:bold"] {
                color: #2d7dcc;
                font-size: 16px;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()
        title_label = QLabel("TestToolBox 工具箱")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        
        desc_label = QLabel("欢迎使用TestToolBox测试工具集合\n\n请从左侧菜单选择需要使用的工具：\n- JSON格式化：格式化和验证JSON数据\n- 更多工具即将上线...")
        desc_label.setStyleSheet("font-size: 16px; line-height: 1.6;")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        self.setLayout(layout)