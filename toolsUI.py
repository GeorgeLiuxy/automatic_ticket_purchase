import logging
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton, QTextEdit,
    QMessageBox, QListWidget, QHBoxLayout, QCheckBox
)

from tools01 import schedule_booking


# 自定义日志处理器，将日志输出到 QTextEdit 控件
class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg + '\n')
        self.text_edit.moveCursor(QtGui.QTextCursor.End)
        self.text_edit.ensureCursorVisible()


# 预定任务的线程类
class BookingThread(QThread):
    log_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    success_signal = pyqtSignal(str)
    stop_signal = pyqtSignal()

    def __init__(self, accounts, court_type, venue_name, target_time, weekday, booking_time, low_flow_mode):
        super().__init__()
        self.accounts = accounts
        self.court_type = court_type
        self.venue_name = venue_name
        self.target_time = target_time
        self.weekday = weekday
        self.booking_time = booking_time
        self.low_flow_mode = low_flow_mode
        self._is_running = True

    def run(self):
        self.success_signal.emit("预定任务已启动")
        try:
            while self._is_running:
                schedule_booking(self.accounts, self.court_type, self.venue_name, self.target_time, self.weekday, self.booking_time, self.low_flow_mode)
                self.log_signal.emit("预定任务执行成功")
                break
        except Exception as e:
            self.error_signal.emit(f"预定过程中出错: {e}")

    def stop(self):
        self._is_running = False


class BookingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.booking_thread = None

    def init_ui(self):
        self.setWindowTitle("场地预定系统")
        self.setGeometry(100, 100, 500, 450)
        layout = QVBoxLayout()

        # 创建账户列表和相关按钮
        self.account_list = QListWidget()
        layout.addWidget(self.account_list)

        account_controls = QHBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")
        self.username_input.setText("cherilyn.li")
        account_controls.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("密码")
        self.password_input.setText("TuTu121866@")
        account_controls.addWidget(self.password_input)

        add_account_button = QPushButton("添加账户")
        add_account_button.clicked.connect(self.add_account)
        account_controls.addWidget(add_account_button)

        remove_account_button = QPushButton("删除选中账户")
        remove_account_button.clicked.connect(self.remove_account)
        account_controls.addWidget(remove_account_button)

        layout.addLayout(account_controls)

        self.court_type_label = QLabel('场地类型:')
        self.court_type_input = QLineEdit()
        self.court_type_input.setText("网球")
        layout.addWidget(self.court_type_label)
        layout.addWidget(self.court_type_input)

        self.venue_name_label = QLabel('场地名称:')
        self.venue_name_input = QLineEdit()
        self.venue_name_input.setText("东区网球场")
        layout.addWidget(self.venue_name_label)
        layout.addWidget(self.venue_name_input)

        self.target_time_label = QLabel('预定时间:')
        self.target_time_input = QLineEdit()
        self.target_time_input.setText("16:00")
        layout.addWidget(self.target_time_label)
        layout.addWidget(self.target_time_input)

        self.weekday_label = QLabel('星期几 (1-7):')
        self.weekday_input = QLineEdit()
        self.weekday_input.setText("3")
        layout.addWidget(self.weekday_label)
        layout.addWidget(self.weekday_input)

        self.booking_time_label = QLabel('抢票时间:')
        self.booking_time_input = QLineEdit()
        self.booking_time_input.setText("12:00")
        layout.addWidget(self.booking_time_label)
        layout.addWidget(self.booking_time_input)

        # 添加低流量模式选择的QCheckBox
        self.low_flow_mode_checkbox = QCheckBox("低流量模式")
        self.low_flow_mode_checkbox.setChecked(True)  # 默认选中
        layout.addWidget(self.low_flow_mode_checkbox)

        self.start_button = QPushButton('开始预定')
        self.start_button.clicked.connect(self.start_booking)
        layout.addWidget(self.start_button)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

        # 配置日志记录
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = QTextEditLogger(self.log_output)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def add_account(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "输入错误", "用户名和密码不能为空")
            return

        account_info = f"{username}:{password}"
        self.account_list.addItem(account_info)

        self.username_input.clear()
        self.password_input.clear()

    def remove_account(self):
        selected_items = self.account_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.account_list.takeItem(self.account_list.row(item))

    def start_booking(self):
        accounts = []
        for i in range(self.account_list.count()):
            account_info = self.account_list.item(i).text()
            username, password = account_info.split(":")
            accounts.append({"username": username, "password": password})

        court_type = self.court_type_input.text()
        venue_name = self.venue_name_input.text()
        target_time = self.target_time_input.text()
        weekday = self.weekday_input.text()
        booking_time = self.booking_time_input.text()
        low_flow_mode = self.low_flow_mode_checkbox.isChecked()

        if not (accounts and court_type and venue_name and target_time and weekday and booking_time):
            QMessageBox.warning(self, "输入错误", "请填写所有字段")
            return

        if self.booking_thread and self.booking_thread.isRunning():
            self.booking_thread.stop()
            self.booking_thread.wait()

        self.booking_thread = BookingThread(accounts, court_type, venue_name, target_time, weekday, booking_time, low_flow_mode)
        self.booking_thread.log_signal.connect(self.log_output.append)
        self.booking_thread.error_signal.connect(lambda msg: logging.error(msg))
        self.booking_thread.success_signal.connect(lambda msg: logging.info(msg))
        self.booking_thread.start()

    def closeEvent(self, event):
        if self.booking_thread and self.booking_thread.isRunning():
            self.booking_thread.stop()
            self.booking_thread.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = BookingApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
