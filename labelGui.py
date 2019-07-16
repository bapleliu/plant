# -*- coding:utf-8 -*-
import sys
import os
import re
import jieba
from PyQt5.QtWidgets import (QWidget, QToolTip, QPushButton, QApplication, QMessageBox, 
                        QDesktopWidget, QLabel, QGridLayout, QLabel, QLineEdit, QTextEdit,QFileDialog)
from PyQt5.QtGui import QIcon 
from PyQt5.QtCore import QCoreApplication

from pyltp import SentenceSplitter
from pyltp import Segmentor
from py2neo import Node,Relationship,Graph
 
from labelImportNeo4j import FileToNeo4j

class plantGUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.cwd = os.getcwd() # 获取当前程序文件位置
        
        #设置窗口的位置和大小
        self.resize(600, 350)
        self.center() 
        #设置窗口的标题
        self.setWindowTitle('植物知识图谱数据库管理')
        #设置窗口的图标，引用图片
        self.setWindowIcon(QIcon('static/files/plantLogo.png'))        
        
        #三个标签说明功能分区
        self.func1 = QLabel('分句', self) 
        self.func2 = QLabel('分词', self)        
        self.func3 = QLabel('导入数据库', self)
        
        #导入和导出文件夹按钮
        self.cutInputButton = QPushButton("导入文件夹")
        self.cutInputButton.setToolTip('选择待<b>分句</b>的文件夹')
        self.cutInputEdit=QLineEdit()
        
        self.cutOutputButton = QPushButton("导出文件夹")
        self.cutOutputButton.setToolTip('选择<b>分句</b>后文件存储的目标文件夹')   
        self.cutOutputEdit=QLineEdit()
        
        self.cutButton = QPushButton("开始分句")
        
        self.segInputButton = QPushButton("导入文件夹")
        self.segInputButton.setToolTip('选择待<b>分词</b>的文件夹')
        self.segInputEdit=QLineEdit()
        self.segOutputButton = QPushButton("导出文件夹")
        self.segOutputButton.setToolTip('选择<b>分词</b>后文件存储的目标文件夹')
        self.segOutputEdit=QLineEdit()
        
        self.segButton = QPushButton("开始分词")
        
        self.dataInputButton= QPushButton("导入文件夹")
        self.dataInputButton.setToolTip('选择需要导入数据库的文件夹')
        self.dataInputEdit=QLineEdit()
        
        self.pushDataButton = QPushButton("导入数据")
        
        self.errorMessage=QTextEdit()
        
        #退出按钮
        self.qbtn = QPushButton("退出", self)
        self.qbtn.clicked.connect(QCoreApplication.instance().quit)
        self.qbtn.resize(self.qbtn.sizeHint())       
        
        #表格布局
        grid = QGridLayout()
        grid.setSpacing(10) #同行的横向间隔设为10 个字距
 
        grid.addWidget(self.func1, 1, 0)
        grid.addWidget(self.cutButton, 1, 3, 2, 1)
        grid.addWidget(self.cutInputEdit, 1, 1)
        grid.addWidget(self.cutInputButton, 1, 2)
        grid.addWidget(self.cutOutputEdit, 2, 1)
        grid.addWidget(self.cutOutputButton, 2, 2)
 
        grid.addWidget(self.func2, 3, 0)
        grid.addWidget(self.segButton, 3, 3, 2, 1)
        grid.addWidget(self.segInputEdit, 3, 1)
        grid.addWidget(self.segInputButton, 3, 2)
        grid.addWidget(self.segOutputEdit, 4, 1)
        grid.addWidget(self.segOutputButton, 4, 2)
 
        grid.addWidget(self.func3, 5, 0)
        grid.addWidget(self.pushDataButton, 5, 3)
        grid.addWidget(self.dataInputEdit, 5, 1)
        grid.addWidget(self.dataInputButton, 5, 2)
        grid.addWidget(self.errorMessage, 6, 1, 5, 1)
        
        grid.addWidget(self.qbtn, 11, 3)
        
        self.setLayout(grid) 

        
        # 定义按钮操作
        self.cutInputButton.clicked.connect(self.cut_input_chooseDir)
        self.cutOutputButton.clicked.connect(self.cut_output_chooseDir)
        self.segInputButton.clicked.connect(self.seg_input_chooseDir)
        self.segOutputButton.clicked.connect(self.seg_output_chooseDir)
        self.dataInputButton.clicked.connect(self.data_input_chooseDir)

        self.cutButton.clicked.connect(self.cutsents)
        self.segButton.clicked.connect(self.segments)
        self.pushDataButton.clicked.connect(self.importDir)

    #点击按钮触发的函数
    def cut_input_chooseDir(self): 
        dir_choose = QFileDialog.getExistingDirectory(self, "选取文件夹", self.cwd) # 起始路径 
        if dir_choose == "": 
            self.cutInputEdit.setText("请选择文件夹") 
            return 
        self.cutInputEdit.setText(dir_choose)
    
    def cut_output_chooseDir(self): 
        dir_choose = QFileDialog.getExistingDirectory(self, "选取文件夹", self.cwd)  
        if dir_choose == "": 
            self.cutOutputEdit.setText("请选择文件夹") 
            return 
        self.cutOutputEdit.setText(dir_choose)
    
    def seg_input_chooseDir(self): 
        dir_choose = QFileDialog.getExistingDirectory(self, "选取文件夹", self.cwd) 
        if dir_choose == "": 
            self.segInputEdit.setText("请选择文件夹") 
            return 
        self.segInputEdit.setText(dir_choose)
    
    def seg_output_chooseDir(self): 
        dir_choose = QFileDialog.getExistingDirectory(self, "选取文件夹", self.cwd) 
        if dir_choose == "": 
            self.segOutputEdit.setText("请选择文件夹") 
            return 
        self.segOutputEdit.setText(dir_choose)
    
    def data_input_chooseDir(self): 
        dir_choose = QFileDialog.getExistingDirectory(self, "选取文件夹", self.cwd) 
        if dir_choose == "": 
            self.dataInputEdit.setText("请选择文件夹") 
            return 
        self.dataInputEdit.setText(dir_choose)
    #分句函数
    def cutsents(self):
        inputdir=self.cutInputEdit.text()
        outputdir=self.cutOutputEdit.text()
        for i in os.listdir(inputdir):
            try:
                textname=inputdir+'/'+i
                outfile=outputdir+'/'+i
                f=open(textname,mode='r', encoding='UTF-8')
                outf=open(outfile,mode='w', encoding='UTF-8')
                for line in f:
                    sents = SentenceSplitter.split(line)  # 分句
                    outf.writelines ('\n'.join(sents))
                f.close()
                outf.close()
            except:
                self.errorMessage.setText(i+"出错") 
        self.errorMessage.setText("分句完成！")
    #分词函数
    def segments(self):
        inputdir=self.segInputEdit.text()
        outputdir=self.segOutputEdit.text()
        jieba.load_userdict("D:/softwares/pyltp/dict.txt")#载入外部词典
        for i in os.listdir(inputdir):
            try:
                file=inputdir+'/'+i
                outfile=outputdir+'/'+i
                f = open(file,"r", encoding='UTF-8') 
                outf=open(outfile,mode='w', encoding='UTF-8')
                for line in f:
                    words = jieba.cut(line)  #使用jieba分词
                    outf.writelines(' '.join(words))
                f.close()
                outf.close()
            except:
                self.errorMessage.setText(i+"出错")
        self.errorMessage.setText("分词完成！")
    #文件夹中所有文件标注信息导入Neo4j
    def importDir(self):
        inputdir=self.dataInputEdit.text()
        DirToNeo4j=FileToNeo4j() #实例化FileToNeo4j，以调用其中的函数
        DirToNeo4j.importDir(inputdir)
        self.errorMessage.setText("数据导入完成！")

    #窗口显示在屏幕中心
    def center(self):       
        #获得窗口
        qr = self.frameGeometry()
        #获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        #显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())  
    
    #关闭窗口时弹出对话框
    def closeEvent(self, event):        
        reply = QMessageBox.question(self, 'Message',
            "确定要退出吗?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No) 
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()     
        
if __name__ == '__main__':
    #创建应用程序和对象
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    plantWindow = plantGUI()
    plantWindow.show()
    app.exec_()