import sys
from reboot_ui import *
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QListView,
    QMessageBox, 
    QListWidget, 
    QListWidgetItem, 
    QMainWindow, 
    QPushButton,
    QLineEdit)
from PyQt5.QtCore import QStringListModel,Qt, QThread
from PyQt5.Qt import QRect
from PyQt5 import QtCore


class Install_Thread(QThread):
    notifyProgress = QtCore.pyqtSignal(str)
    popup_error = QtCore.pyqtSignal(str)
    notifySuccess  = QtCore.pyqtSignal()

    def __init__(self, host_name,host_pw, parent=None):
        QThread.__init__(self, parent)
        self.host_name = host_name
        self.host_pw = host_pw

    def run(self):
        try:
            self.notifyProgress.emit("安装中")
            self.sleep(1)
            print(self.host_name)
            print(self.host_pw)
            self.notifySuccess.emit()
            self.notifyProgress.emit("安装完成")
        except Exception as e:
            self.notifyProgress.emit("安装脚本")
            self.popup_error.emit(str(e))




class Project_View(QMainWindow, Ui_MainWindow):
    def __init__(self,parent=None):
        super(Project_View, self).__init__(parent)
        self.setupUi(self)
        #设置初始大小与标题
        self.setWindowTitle('reboot工具')
        vLayout = QVBoxLayout(self)
        vLayout.addWidget(self.scrollArea)
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.pushButton.clicked.connect(self._widget_add)
        self.scrollArea.setWidget(self.main_widget)
        self.WList = []

        #self.scrollAreaWidgetContents.addWidget(QPushButton('aa'))

    def clearSpacer(self, layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)

            if isinstance(item, QtWidgets.QWidgetItem):
                print("widget" + str(item))
                #item.widget().close()
                # or
                # item.widget().setParent(None)
            elif isinstance(item, QtWidgets.QSpacerItem):
                print("spacer " + str(item))
                layout.removeItem(item)
                # no need to do extra stuff
            else:
                print("layout " + str(item))
                #self.clearLayout(item.layout())

            # remove the item from layout
            #layout.removeItem(item)    


    def _widget_add(self):
        try:
            self.clearSpacer(self.main_widget.children()[0])
        except Exception as e:
            pass
        self.son = MyScrollWidget()
        self.son.setFixedSize(650, 50)
        self.WList.append(self.son)
        self.main_layout.addWidget(self.son)
        self.main_layout.addStretch(1)
        self.main_widget.setLayout(self.main_layout)
        self.scrollArea.setWidget(self.main_widget)



        print(self.WList[0].user_edit.text())









class MyScrollWidget(QtWidgets.QWidget):


    c_red_style = """QLabel{
                    min-width:     16px;     
                    min-height:    16px;     
                    max-width:     16px;    
                    max-height:    16px;  
                    border:0px;
                    border-radius: 8px;     
                    background: red;    
                    }
                  """

    c_green_style = """QLabel{
                    min-width:     16px;     
                    min-height:    16px;     
                    max-width:     16px;    
                    max-height:    16px;  
                    border:0px;
                    border-radius: 8px;     
                    background: green;    
                    }
                  """

    def __init__(self,parent=None):
        super(MyScrollWidget, self).__init__(parent)
        
        self.frame = QtWidgets.QFrame(self)
        self.frame.setStyleSheet("QFrame{border:1px solid grey; } ")
        self.frame.setFixedSize(650, 50)
        self.layout = QtWidgets.QHBoxLayout(self.frame)
        self.label1 = QtWidgets.QLabel()
        self.label1.setText('用户名')
        self.label1.setStyleSheet("QLabel{border:0px; } ")
        self.layout.addWidget(self.label1)
        self.user_edit = QtWidgets.QLineEdit()
        self.layout.addWidget(self.user_edit)

        self.label2 = QtWidgets.QLabel()
        self.label2.setText('密码')
        self.label2.setStyleSheet("QLabel{border:0px; } ")
        self.layout.addWidget(self.label2)
        self.pw_edit = QtWidgets.QLineEdit()
        self.pw_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.layout.addWidget(self.pw_edit)

        self.connect_btn = QtWidgets.QPushButton()
        self.connect_btn.setText('连接')
        self.layout.addWidget(self.connect_btn)

        self.status_icon = QtWidgets.QLabel()
        self.status_icon.setStyleSheet(MyScrollWidget.c_red_style)
        self.layout.addWidget(self.status_icon)

        self.install_btn = QtWidgets.QPushButton()
        self.install_btn.setText('安装脚本')
        self.install_btn.setCheckable(True)
        self.layout.addWidget(self.install_btn)

        self.layout.setSpacing(8)  # 控件间距
        # https://cloud.tencent.com/developer/article/1437295
        self.layout.addStretch(1)  # addStretch的参数只要大于0，则表示占满整个布局最后一部分，前面的控件显示为正常大小，不要拉伸
        self.connect_btn.clicked.connect(self.fresh)
        self.install_btn.clicked.connect(self.install)
        self.isconnected = False


    def fresh(self):
        if self.no_blank():
            self.status_icon.setStyleSheet(MyScrollWidget.c_green_style)
            self.isconnected = True


    def no_blank(self):
        
        # 如果每个输入项都不为空的表示输入正确
        if self.user_edit.text() != '' and self.pw_edit.text() != '' :
            return True
        else:
            QMessageBox().critical(self,"警告",'必填项不能为空')
            return False


    def install(self):
        if self.isconnected:
            if self.no_blank():
                self.install_btn.setEnabled(False)
                self.install_pkg = Install_Thread(host_name=self.user_edit.text(), host_pw=self.pw_edit.text())
                self.install_pkg.notifyProgress.connect(self.installing)
                self.install_pkg.popup_error.connect(self.error_win)  
                self.install_pkg.notifySuccess.connect(self.success_win)  
                self.install_pkg.start()   
            else:
                self.install_btn.setChecked(False)
        else:
            QMessageBox().critical(self,"警告",'没有连接到主机')
            self.install_btn.setChecked(False)



    def installing(self, btnstr):
        self.install_btn.setText(btnstr)

        #self.install_btn.setCheckable(False)
        
    def error_win(self, estr):
        self.install_btn.setChecked(False)
        self.install_btn.setEnabled(True)
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setText("Error")
        error_msg.setInformativeText(estr)
        error_msg.setWindowTitle("出错了")
        error_msg.exec_()    

    def success_win(self):
        QMessageBox().information(self,"成功",'安装完成')







if __name__ == '__main__':
    app=QApplication(sys.argv)
    win=Project_View()
    win.show()
    sys.exit(app.exec_())