from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                            QSplitter, QLabel, QComboBox, QStyledItemDelegate,
                            QGroupBox, QStyle, QPlainTextEdit, QAbstractScrollArea,
                            QFileDialog)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QFontMetrics,
                        QPainter, QPen, QBrush, QPixmap, QSyntaxHighlighter,
                        QTextCharFormat, QColor, QFont, QKeySequence)
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtCore import Qt, QTimer, QRect, QRegularExpression, QSize
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QAbstractScrollArea

import json
import pprint
from loguru import logger
import yaml
from dicttoxml import dicttoxml
from PyQt5.QtGui import QFont


class LineNumberWidget(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setFont(editor.font())

    def sizeHint(self):
        return QSize(self.width(), 0)

    def width(self):
        return 30  # Adjust as needed

    def update_number(self, rect):
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#333333"))  # Line number area background color

        font_metrics = QFontMetrics(self.font())
        current_block = self.editor.firstVisibleBlock()
        block_number = current_block.blockNumber()
        block_top = self.editor.blockBoundingGeometry(current_block).translated(self.editor.contentOffset()).top()
        bottom = event.rect().bottom()

        while current_block.isValid() and block_top <= bottom:
            number = str(block_number + 1)
            painter.setPen(QColor("#D4D4D4"))  # Line number color
            painter.drawText(0, round(block_top + font_metrics.ascent()), self.width(), font_metrics.height(),
                             Qt.AlignRight, number)

            current_block = current_block.next()
            block_number += 1
            block_top = self.editor.blockBoundingGeometry(current_block).translated(self.editor.contentOffset()).top()


class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlight_rules = []
        self.search_format = QTextCharFormat()
        self.search_format.setBackground(QColor(255, 255, 0))  # 黄色背景
        self.search_text = ""

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
        # 先执行原有的语法高亮
        for pattern, fmt in self.highlight_rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
        
        # 执行搜索高亮
        if self.search_text:
            expression = QRegularExpression(QRegularExpression.escape(self.search_text),
                                          QRegularExpression.CaseInsensitiveOption)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.search_format)

    def highlight_error(self, pos):
        error_format = QTextCharFormat()
        error_format.setBackground(QColor(255, 0, 0))  # 红色背景
        self.setFormat(pos, 1, error_format)  # 高亮错误位置

    def set_search_text(self, text):
        """设置搜索文本并重新高亮"""
        self.search_text = text
        self.rehighlight()

    def clear_highlight(self):
        """清除所有高亮"""
        self.search_text = ""
        self.rehighlight()


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
            QTextEdit, QPlainTextEdit {
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
        return QPlainTextEdit()

    def format_json(self):
        text = self.input_edit.toPlainText()
        try:
            data = json.loads(text)
            formatted = json.dumps(data, indent=4, ensure_ascii=False)
            self.output_edit.setPlainText(formatted)
            logger.success('JSON格式化成功')
        except json.JSONDecodeError as e:
            pos = e.pos
            start = max(0, pos - 20)
            end = min(len(text), pos + 20)
            context = text[start:end]
            error_msg = f"JSON 格式错误(位置 {pos}):\n{e.msg}\n上下文:\n{context}"
            self.output_edit.setPlainText(error_msg)  # 显示错误信息
            self.highlighter.highlight_error(e.pos)  # 高亮错误部分
            logger.error(f"JSON格式错误：{e.msg}")
        except Exception as e:
            logger.error(f'格式化失败: {e}')


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

    # def validate_json(self):
    #     try:
    #         json.loads(self.input_edit.toPlainText())
    #         self.output_edit.setPlainText("JSON 格式正确")
    #         logger.info("JSON验证通过")
    #     except json.JSONDecodeError as e:
    #         text = self.input_edit.toPlainText()
    #         pos = e.pos
    #         start = max(0, pos-20)
    #         end = min(len(text), pos+20)
    #         context = text[start:end]
    #         marker = ' '*(pos-start) + '↑'
    #         error_msg = f"JSON 格式错误(位置 {pos}):\n{e.msg}\n\n上下文:\n{context}\n{marker}"
    #         self.output_edit.setPlainText(error_msg)
    #         logger.error(f"JSON格式错误：{e.msg}")

    def download_content(self):
        """下载格式化后的JSON内容到文件"""
        if not self.output_edit.toPlainText():
            logger.warning("没有可下载的内容")
            return
            
        # 获取默认文件名
        default_name = "formatted.json"
        if self.convert_combo.currentText() == "YAML":
            default_name = "converted.yaml"
        elif self.convert_combo.currentText() == "XML":
            default_name = "converted.xml"
        elif self.convert_combo.currentText() == "Python字典":
            default_name = "converted.py"
            
        # 打开文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", default_name,
            "All Files (*);;JSON Files (*.json);;YAML Files (*.yaml);;XML Files (*.xml);;Python Files (*.py)")
            
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_edit.toPlainText())
                logger.success(f"文件已保存到: {file_path}")
            except Exception as e:
                logger.error(f"保存文件失败: {e}")

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
        self.input_edit = QPlainTextEdit()
        group_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_group)

        # 输出面板
        output_panel = QWidget()
        output_layout = QVBoxLayout(output_panel)

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_input = QPlainTextEdit()
        self.search_input.setMaximumHeight(30)
        self.search_button = QPushButton("搜索")
        self.prev_button = QPushButton("上一个")
        self.next_button = QPushButton("下一个")
        self.search_button.clicked.connect(self.search_text)
        self.prev_button.clicked.connect(self.prev_match)
        self.next_button.clicked.connect(self.next_match)
        search_layout.addWidget(QLabel("搜索:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.prev_button)
        search_layout.addWidget(self.next_button)
        output_layout.addLayout(search_layout)

        # 输出区域
        output_group = QGroupBox("格式化结果")
        group_layout = QVBoxLayout(output_group)

        # 输出控件 - 使用QPlainTextEdit显示JSON
        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)
        font = QFont("Consolas", 10)
        self.output_edit.setFont(font)
        self.output_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #252526;
                color: #9CDCFE;
                border: 1px solid #3C3C3C;
                font-family: Consolas;
                font-size: 12px;
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

        # 添加Ctrl+F快捷键
        self.shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_search.activated.connect(self.search_text)

    def search_text(self):
        """执行搜索并高亮匹配文本"""
        search_text = self.search_input.toPlainText()
        if hasattr(self, 'highlighter') and search_text:
            self.highlighter.set_search_text(search_text)
            
            # 查找所有匹配位置
            document = self.output_edit.document()
            text = document.toPlainText().lower()
            search_text_lower = search_text.lower()
            self.matches = []
            index = text.find(search_text_lower)
            while index >= 0:
                self.matches.append(index)
                index = text.find(search_text_lower, index + len(search_text_lower))
            
            self.current_match = 0 if self.matches else -1
            self.navigate_to_match()
    
    def navigate_to_match(self):
        """导航到当前匹配项"""
        if hasattr(self, 'matches') and 0 <= self.current_match < len(self.matches):
            cursor = self.output_edit.textCursor()
            cursor.setPosition(self.matches[self.current_match])
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,
                              len(self.search_input.toPlainText()))
            self.output_edit.setTextCursor(cursor)
            self.output_edit.setFocus()
    
    def prev_match(self):
        """导航到上一个匹配项"""
        if hasattr(self, 'matches') and len(self.matches) > 0:
            self.current_match = (self.current_match - 1) % len(self.matches)
            self.navigate_to_match()
    
    def next_match(self):
        """导航到下一个匹配项"""
        if hasattr(self, 'matches') and len(self.matches) > 0:
            self.current_match = (self.current_match + 1) % len(self.matches)
            self.navigate_to_match()

    def test_fix_json(self, json_string):
        pass
