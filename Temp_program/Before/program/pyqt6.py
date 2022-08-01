import sys
from PyQt6.QtWidgets import *
from PyQt6 import uic
import os
from PyQt6.QtCore import QTimer


## python실행파일 디렉토리
# BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
# UI_class = uic.loadUiType(BASE_DIR + r'\uniform.ui')[0]
UI_class = uic.loadUiType('./uniform.ui')[0]

class main_window(QMainWindow, UI_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('자사몰 네이버 포맷')
    
        self.ImWeb_file.setText('자사몰')
        self.Naver_file.setText('스마트스토어')
        self.Save_label.setText('저장 경로')
    
        self.ImWeb_file_btn.clicked.connect(self.imweb_FileLoad)
        self.Naver_file_btn.clicked.connect(self.naver_FileLoad)  
        self.Format_func_btn.clicked.connect(self.Format_functions)
        self.Save_to_btn.clicked.connect(self.Save_functions)
        
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(60,170,118,23)
        self.progressBar.setMaximum(250)
        self.progressBar.setValue(0)
        

        
    def imweb_FileLoad(self):
        global iwfname
        iwfname = QFileDialog.getOpenFileName(self)
        self.ImWeb_file.setText(os.path.basename(iwfname[0]))
        
    
    
    def naver_FileLoad(self):
        global nvfname
        nvfname = QFileDialog.getOpenFileName(self)
        self.Naver_file.setText(os.path.basename(nvfname[0]))
        
        
    
    def Format_functions(self):
        import func
        import pandas as pd
        global honest
        global total
        total, honest,  = func.total(pd,iwfname[0],nvfnmae[0])
        timer = QTimer(self)
        timer.timeout.connect(self.Increase_Stop)
        timer.start()
        
        
    def Save_functions(self):
            
        import datetime as dt
        today = dt.datetime.today()
        date = today.strftime('%Y%m%d')
        import os
        if not os.path.exists(f'./{date}'):
            os.mkdir(f'./{date}')
        
        honest.to_excel(f'./{date}/어니스트.xlsx',encoding='utf-8-sig',index=0)
        
        total.to_excel(f'./{date}/총합(어니스트제외).xlsx',encoding='utf-8-sig',index=0)
        
        cwd = os.getcwd()
        
        self.Save_label.setText(f'{cwd}/{date}')

        

        
    def Increase_Stop(self):
        self.progressBar.setValue(self.progressBar.value() + 1)
        
        
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    Window = main_window()
    Window.show()
    app.exec()
        