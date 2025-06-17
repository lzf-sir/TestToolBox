import sys
import os
from PyQt5 import QtWidgets

from src.app import TestToolBoxApp
from src.logger import setup_logger

# 自动获取PyQt5安装路径
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(
    os.path.dirname(QtWidgets.__file__), 'Qt5', 'plugins'
)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TestToolBoxApp()
    window.show()
    sys.exit(app.exec_())
