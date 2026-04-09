"""
Main entry point for the Virtual Environment Manager application
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QPalette, QColor

from .ui.main_window import VenvManager


def main():
    """Application entry point"""
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle("Fusion")

    # 设置字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 设置调色板（浅色主题）
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(33, 33, 33))
    app.setPalette(palette)

    window = VenvManager()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
