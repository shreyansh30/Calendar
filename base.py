import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget,
    QPushButton, QListWidget, QLineEdit, QLabel, QMessageBox,
    QListWidgetItem, QSpacerItem, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QBrush, QLinearGradient, QPainter

REMINDER_FILE = "reminders.json"

def get_gradient_palette():
    palette = QPalette()
    gradient = QLinearGradient(0, 0, 0, 600)
    gradient.setColorAt(0.0, QColor("#f7fafd"))
    gradient.setColorAt(0.7, QColor("#e9f0fa"))
    gradient.setColorAt(1.0, QColor("#f3f5fb"))
    palette.setBrush(QPalette.Window, QBrush(gradient))
    return palette

class CustomCalendarWidget(QCalendarWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set current date to ensure month/year show properly
        self.setSelectedDate(QDate.currentDate())
        
        # Style navigation bar with lighter gradient background
        nav_bar = self.findChild(QWidget, "qt_calendar_navigationbar")
        if nav_bar:
            nav_bar.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e8f1fc, stop:1 #ffffff);
                padding: 6px;
                border-radius: 8px;
            """)
            for child in nav_bar.children():
                cls = child.metaObject().className()
                # Month ComboBox styling
                if cls == 'QComboBox':
                    child.setStyleSheet("""
                        QComboBox {
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #eff5fc, stop:1 #ffffff);
                            border-radius: 8px;
                            padding: 6px 16px;
                            font-size: 24px;
                            color: #25355c;
                            border: 1px solid #a6c6f9;
                            min-width: 140px;
                            max-height: 36px;
                        }
                        QComboBox::drop-down { width: 0px; border: none; }
                        QComboBox::down-arrow { width:0; height:0; }
                    """)
                # Year SpinBox styling
                if cls == 'QSpinBox':
                    child.setStyleSheet("""
                        QSpinBox {
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #eff5fc, stop:1 #ffffff);
                            border-radius: 8px;
                            padding: 6px 12px;
                            font-size: 24px;
                            color: #25355c;
                            border: 1px solid #a6c6f9;
                            min-width: 100px;
                            max-height: 36px;
                        }
                        QSpinBox::up-button, QSpinBox::down-button { width:0; height:0; }
                    """)
                # Improved Prev/Next buttons with better design
                if cls == 'QToolButton':
                    try:
                        arrow = child.arrowType()
                        if arrow == Qt.LeftArrow:
                            child.setText("❮")
                        elif arrow == Qt.RightArrow:
                            child.setText("❯")
                        else:
                            child.setText("◀")
                    except:
                        child.setText("◀")
                    
                    child.setStyleSheet("""
                        QToolButton {
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #ffffff, stop:1 #f0f8ff);
                            border: 2px solid #b5d6fa;
                            border-radius: 20px;
                            font-size: 16px;
                            font-weight: bold;
                            color: #5374b6;
                            min-width: 40px;
                            min-height: 40px;
                        }
                        QToolButton:hover {
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #a6c6f9, stop:1 #8fd3bd);
                            color: #ffffff;
                            border: 2px solid #8fd3bd;
                            
                        }
                        QToolButton:pressed {
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #8fd3bd, stop:1 #a6c6f9);
                            border: 2px solid #25355c;
                        }
                    """)

class ReminderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendar & Reminders")
        self.setWindowIcon(QIcon("icon.png"))
        self.setMinimumSize(900, 700)
        self.setAutoFillBackground(True)
        self.setPalette(get_gradient_palette())

        # Enhanced stylesheet with improved hover effects for calendar dates
        self.setStyleSheet("""
            QWidget { font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; }
            #HeaderLabel { color: #25355c; font-size: 34px; font-weight: 600; letter-spacing: 1.5px; }
            #SubLabel { color: #6e8dc7; font-size: 20px; font-weight: 500; margin-top: 3px; }

            QCalendarWidget {
                border-radius: 14px;
                background: rgba(255,255,255,0.99);
                border: 1.5px solid #b5d6fa;
                selection-background-color: #a6c6f9;
                selection-color: #25355c;
                font-size: 21px;
                margin-bottom: 10px;
                padding: 10px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 21px;
                color: #25355c;
                font-weight: 500;
                selection-background-color: #a6c6f9;
                selection-color: #25355c;
            }
            QCalendarWidget QAbstractItemView::item {
                border-radius: 6px;
                margin: 1px;
                padding: 4px;
            }
            QCalendarWidget QAbstractItemView::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #dbe9fc, stop:1 #e8f4f8);
                color: #25355c;
                font-weight: 600;
                border: 1px solid #a6c6f9;
            }
            QCalendarWidget QAbstractItemView::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #a6c6f9, stop:1 #8fd3bd);
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #25355c;
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #a0bfff, stop:1 #8fd3bd);
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 8px 0;
                font-size: 17px;
                font-weight: 600;
                min-height: 32px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8fd3bd, stop:1 #a0bfff);
                color: #25355c;
            }

            QLineEdit {
                border: 1.5px solid #b5d6fa;
                border-radius: 8px;
                padding: 16px;
                background: #fafdff;
                font-size: 20px;
                font-weight: 500;
                color: #25355c;
                margin-bottom: 16px;
            }

            QListWidget {
                background: #fafdff;
                border: 1.5px solid #b5d6fa;
                border-radius: 10px;
                font-size: 20px;
                min-height: 220px;
                padding: 10px 2px;
            }
            QListWidget::item {
                padding: 13px 10px;
                border-bottom: 1.5px solid #eef4fb;
            }
            QListWidget::item:selected {
                background: #a6c6f9;
                color: #25355c;
            }

            QFrame#SidePanel {
                background: rgba(255,255,255,0.95);
                border-radius: 14px;
                border: 1.5px solid #b5d6fa;
                padding: 24px 18px;
                margin-left: 14px;
                margin-top: 10px;
            }
        """)

        self.reminders = self.load_reminders()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(34, 28, 34, 18)
        layout.setSpacing(12)

        header = QLabel("Calendar & Reminders")
        header.setObjectName("HeaderLabel")
        layout.addWidget(header, alignment=Qt.AlignHCenter)

        subtitle = QLabel("Stay organized. Plan ahead. Never forget.")
        subtitle.setObjectName("SubLabel")
        layout.addWidget(subtitle, alignment=Qt.AlignHCenter)

        main_hbox = QHBoxLayout()
        main_hbox.setSpacing(30)

        # Calendar Widget with current date set by default
        self.calendar = CustomCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setFont(QFont('Segoe UI', 21))
        
        # Ensure current date is selected and displayed
        current_date = QDate.currentDate()
        self.calendar.setSelectedDate(current_date)
        self.calendar.showToday()
        
        self.calendar.selectionChanged.connect(self.update_reminder_list)
        self.calendar.setFixedSize(520, 400)
        main_hbox.addWidget(self.calendar, stretch=2)

        # Side Panel for Reminders
        side_panel = QFrame()
        side_panel.setObjectName("SidePanel")
        side_panel.setFixedWidth(340)
        side_vbox = QVBoxLayout()
        side_vbox.setSpacing(14)

        date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.date_label = QLabel(f"Reminders for {date_str}")
        self.date_label.setFont(QFont('Segoe UI', 20, QFont.Bold))
        self.date_label.setStyleSheet("color:#5374b6; margin-bottom: 6px;")
        side_vbox.addWidget(self.date_label)

        self.reminder_input = QLineEdit()
        self.reminder_input.setPlaceholderText("Add a reminder.")
        self.reminder_input.setFont(QFont('Segoe UI', 20))
        self.reminder_input.returnPressed.connect(self.add_reminder)
        side_vbox.addWidget(self.reminder_input)

        self.reminder_list = QListWidget()
        self.reminder_list.setFont(QFont('Segoe UI', 19))
        side_vbox.addWidget(self.reminder_list, stretch=4)

        # Buttons laid out side-by-side, smaller size
        btn_hbox = QHBoxLayout()
        btn_hbox.setSpacing(10)

        add_btn = QPushButton("Add")
        add_btn.setFont(QFont('Segoe UI', 16, QFont.Bold))
        add_btn.setFixedSize(100, 32)
        add_btn.clicked.connect(self.add_reminder)
        btn_hbox.addWidget(add_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setFont(QFont('Segoe UI', 16, QFont.Bold))
        delete_btn.setFixedSize(100, 32)
        delete_btn.clicked.connect(self.delete_reminder)
        btn_hbox.addWidget(delete_btn)

        side_vbox.addLayout(btn_hbox)
        side_vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        side_panel.setLayout(side_vbox)
        main_hbox.addWidget(side_panel, stretch=1)
        layout.addLayout(main_hbox)
        self.setLayout(layout)

        self.update_reminder_list()

    def load_reminders(self):
        if os.path.exists(REMINDER_FILE):
            with open(REMINDER_FILE, "r") as f:
                try:
                    return json.load(f)
                except:
                    return {}
        return {}

    def save_reminders(self):
        with open(REMINDER_FILE, "w") as f:
            json.dump(self.reminders, f, indent=2)

    def update_reminder_list(self):
        sel = self.calendar.selectedDate()
        date_str = sel.toString("yyyy-MM-dd")
        self.date_label.setText(f"Reminders for {date_str}")
        self.reminder_list.clear()
        for text in self.reminders.get(date_str, []):
            item = QListWidgetItem("📝  " + text)
            item.setFont(QFont('Segoe UI', 12))
            self.reminder_list.addItem(item)
        self.highlight_reminder_dates()

    def highlight_reminder_dates(self):
        # Clear previous
        for dt_str in list(self.reminders.keys()) + [self.calendar.selectedDate().toString("yyyy-MM-dd")]:
            dt = QDate.fromString(dt_str, "yyyy-MM-dd")
            fmt = self.calendar.dateTextFormat(dt)
            fmt.setBackground(Qt.white)
            fmt.setForeground(Qt.black)
            self.calendar.setDateTextFormat(dt, fmt)
        # Highlight dates with reminders
        for dt_str in self.reminders:
            dt = QDate.fromString(dt_str, "yyyy-MM-dd")
            fmt = self.calendar.dateTextFormat(dt)
            fmt.setBackground(QColor("#e6f0fc"))
            fmt.setForeground(QColor("#25355c"))
            font = fmt.font()
            font.setBold(True)
            fmt.setFont(font)
            self.calendar.setDateTextFormat(dt, fmt)

    def add_reminder(self):
        text = self.reminder_input.text().strip()
        if not text:
            return
        date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.reminders.setdefault(date_str, []).append(text)
        self.save_reminders()
        self.reminder_input.clear()
        self.update_reminder_list()

    def delete_reminder(self):
        items = self.reminder_list.selectedItems()
        if not items:
            QMessageBox.information(self, "Delete Reminder", "Select a reminder to delete.")
            return
        date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
        for it in items:
            txt = it.text().lstrip("📝  ")
            if txt in self.reminders.get(date_str, []):
                self.reminders[date_str].remove(txt)
        if not self.reminders.get(date_str):
            self.reminders.pop(date_str, None)
        self.save_reminders()
        self.update_reminder_list()

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ReminderApp()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()