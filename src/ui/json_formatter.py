from PyQt5.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QComboBox, QTreeView, QStyledItemDelegate, QGroupBox
from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QFontMetrics,
                        QPainter, QPen, QBrush, QPixmap, QSyntaxHighlighter,
                        QTextCharFormat, QColor, QFont)
from PyQt5.QtCore import Qt, QTimer, QRect, QRegularExpression
import json
import pprint
from loguru import logger
import yaml
from dicttoxml import dicttoxml
from PyQt5.QtGui import QFont

class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlight_rules = []
        
        # 关键字格式
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor('#569CD6'))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = ['true', 'false', 'null']
        for word in keywords:
            pattern = fr'\b{word}\b'
            self.highlight_rules.append((QRegularExpression(pattern), keyword_format))
        
        # 字符串格式
        string_format = QTextCharFormat()
        string_format.setForeground(QColor('#CE9178'))
        self.highlight_rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        
        # 数字格式
        number_format = QTextCharFormat()
        number_format.setForeground(QColor('#B5CEA8'))
        self.highlight_rules.append((QRegularExpression(r'\b[0-9]+\b'), number_format))
        
        # 标点符号格式
        punctuation_format = QTextCharFormat()
        punctuation_format.setForeground(QColor('#D4D4D4'))
        self.highlight_rules.append((QRegularExpression(r'[{}[\],:]'), punctuation_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlight_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class JsonFormatterPage(QWidget):
    BUTTON_STYLE = """
        QPushButton {
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            min-height: 32px;
            font-weight: 500;
            background-color: #f0f0f0;
            border: none;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 14px;
                background-color: #f5f5f5;
                color: #333333;
            }
            QGroupBox {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                min-height: 32px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QTextEdit, QTreeView {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
            }
            QLabel {
                font-size: 16px;
                font-weight: 600;
            }
        """)

        self.init_ui()

    def _create_editor(self):
        return QTextEdit()

    def format_json(self):
        try:
            QTimer.singleShot(300, self.delayed_parse)
        except Exception as e:
            logger.error(f'定时器启动失败: {e}')

    def delayed_parse(self):
        try:
            data = json.loads(self.input_edit.toPlainText())
            formatted = json.dumps(data, indent=4, ensure_ascii=False)
            self.output_edit.setPlainText(formatted)
            logger.success('JSON格式化成功')
        except json.JSONDecodeError as e:
            error_msg = f'格式错误: {str(e)}\n原始文本: {self.input_edit.toPlainText()}'
            logger.error(error_msg)
            self.output_edit.setPlainText(error_msg)
        except Exception as e:
            logger.error(f'未知错误: {str(e)}')
            self.output_edit.setPlainText(f'未知错误: {str(e)}')

    def convert_format(self, target_format):
        selected_format = self.convert_combo.currentText()
        if selected_format == 'JSON':
            return
        elif selected_format == 'Python字典':
            try:
                import ast
                json_data = json.loads(self.input_edit.toPlainText())
                dict_str = f"# Python字典\n{pprint.pformat(json_data, indent=4, width=80)}"
                self.output_edit.setPlainText(dict_str)
                logger.info("转换为Python字典格式")
            except json.JSONDecodeError as e:
                error_msg = f"JSON 格式错误：{e}"
                self.output_edit.setPlainText(error_msg)
                logger.error(f"JSON格式错误：{e.msg}")
        elif selected_format == 'YAML':
            try:
                import yaml
                json_data = json.loads(self.input_edit.toPlainText())
                yaml_data = yaml.dump(json_data, indent=4, allow_unicode=True)
                self.output_edit.setPlainText(yaml_data)
                logger.info("转换为YAML格式")
            except ImportError:
                error_msg = "需要安装PyYAML库才能转换为YAML格式"
                self.output_edit.setPlainText(error_msg)
                logger.error(error_msg)
            except json.JSONDecodeError as e:
                error_msg = f"JSON 格式错误：{e}"
                self.output_edit.setPlainText(error_msg)
                logger.error(f"JSON格式错误：{e.msg}")
        elif selected_format == 'XML':
            try:
                from dicttoxml import dicttoxml
                json_data = json.loads(self.input_edit.toPlainText())
                xml_data = dicttoxml(json_data, attr_type=False).decode('utf-8')
                self.output_edit.setPlainText(xml_data)
                logger.info("转换为XML格式")
            except ImportError:
                error_msg = "需要安装dicttoxml库才能转换为XML格式"
                self.output_edit.setPlainText(error_msg)
                logger.error(error_msg)
            except json.JSONDecodeError as e:
                error_msg = f"JSON 格式错误：{e}"
                self.output_edit.setPlainText(error_msg)
                logger.error(f"JSON格式错误：{e.msg}")
        

    def clear_content(self):
        self.input_edit.clear()
        self.output_edit.clear()
        logger.info('已清空所有输入输出内容')

    def copy_result(self):
        logger.info("结果已复制到剪贴板")

    def validate_structure(self):
        try:
            json.loads(self.input_edit.toPlainText())
            logger.info("JSON验证通过")
        except json.JSONDecodeError as e:
            logger.error(f"JSON格式错误：{e.msg}")

    def minify_content(self):
        pass

    def validate_json(self):
        try:
            json.loads(self.input_edit.toPlainText())
            self.output_edit.setPlainText("JSON 格式正确")
            logger.info("JSON验证通过")
        except json.JSONDecodeError as e:
            text = self.input_edit.toPlainText()
            pos = e.pos
            start = max(0, pos-20)
            end = min(len(text), pos+20)
            context = text[start:end]
            marker = ' '*(pos-start) + '↑'
            error_msg = f"JSON 格式错误(位置 {pos}):\n{e.msg}\n\n上下文:\n{context}\n{marker}"
            self.output_edit.setPlainText(error_msg)
            logger.error(f"JSON格式错误：{e.msg}")

    def download_content(self):
        pass

    def minify_json(self):
        try:
            data = json.loads(self.input_edit.toPlainText())
            minified = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            self.output_edit.setPlainText(minified)
            logger.info("JSON已压缩")
        except json.JSONDecodeError as e:
            error_msg = f"JSON 格式错误：{e}"
            self.output_edit.setPlainText(error_msg)
            logger.error(f"JSON格式错误：{e.msg}")

    def json_to_tree(self, json_data, parent):
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                key_item = QStandardItem(key)
                parent.appendRow(key_item)
                self.json_to_tree(value, key_item)
        elif isinstance(json_data, list):
            for i, value in enumerate(json_data):
                index_item = QStandardItem(str(i))
                parent.appendRow(index_item)
                self.json_to_tree(value, index_item)
        else:
            value_item = QStandardItem(str(json_data))
            parent.appendRow(value_item)

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 输入面板
        input_panel = QWidget()
        input_layout = QVBoxLayout(input_panel)
        
        # 功能按钮区域
        btn_layout = QHBoxLayout()
        buttons = [
            ('格式化', self.format_json),
            ('清空', self.clear_content),
            ('复制结果', self.copy_result),
            ('验证JSON', self.validate_json),
            ('压缩JSON', self.minify_json)
        ]
        
        for text, slot in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(self.BUTTON_STYLE)
            btn.clicked.connect(slot)
            btn_layout.addWidget(btn)
        
        # 格式转换下拉框
        self.convert_combo = QComboBox()
        self.convert_combo.addItems(['JSON', 'YAML', 'XML', 'Python字典'])
        self.convert_combo.activated.connect(self.convert_format)
        btn_layout.addWidget(self.convert_combo)
        
        input_layout.addLayout(btn_layout)
        
        # 输入区域
        input_group = QGroupBox("输入JSON")
        group_layout = QVBoxLayout(input_group)
        self.input_edit = QTextEdit()
        group_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_group)
        
        # 输出面板
        output_panel = QWidget()
        output_layout = QVBoxLayout(output_panel)
        
        # 输出区域
        output_group = QGroupBox("格式化结果")
        group_layout = QVBoxLayout(output_group)
        # 输出控件 - 使用QTextEdit作为代码编辑器
        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setLineWrapMode(QTextEdit.NoWrap)
        font = QFont("Consolas", 10)
        self.output_edit.setFont(font)
        self.output_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
            }
        """)
        self.highlighter = JsonHighlighter(self.output_edit.document())
        
        output_btn_layout = QHBoxLayout()
        self.download_btn = QPushButton('下载')
        self.download_btn.clicked.connect(self.download_content)
        output_btn_layout.addStretch()
        output_btn_layout.addWidget(self.download_btn)
        
        group_layout.addWidget(self.output_edit)
        group_layout.addLayout(output_btn_layout)
        output_layout.addWidget(output_group)
        
        # 设置分割器
        splitter.addWidget(input_panel)
        splitter.addWidget(output_panel)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
