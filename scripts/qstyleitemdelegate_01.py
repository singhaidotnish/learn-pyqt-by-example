import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Delegate_1(QStyledItemDelegate): 
    def createEditor(self, parent, option, index):
        combo = QComboBox()
        combo.addItem('BINARY')
        combo.addItem('ASCII')
        return combo

    def setModelData(self, editor, model, index):
        txt = editor.currentText()
        model.setData(index, txt)

class Delegate_2(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        combo = QComboBox()
        combo.addItem('True')
        combo.addItem('False')
        return combo

    def setModelData(self, editor, model, index):
        txt = editor.currentText()
        model.setData(index, txt)

if __name__ == '__main__':

    app = QApplication(sys.argv)

    model = QStandardItemModel(2, 2)
    
    it = QStandardItem('File_mode')
    model.setItem(0, 0, it)
    it = QStandardItem('ASCII') # apply delegate_1 to the cell
    model.setItem(0, 1, it)

    it = QStandardItem('Opened')
    model.setItem(1, 0, it)
    it = QStandardItem('True') # apply delegate_2 to the cell
    model.setItem(1, 1, it)

    t = QTreeView() # <- it's json data 
    t.setModel(model)
    t.setItemDelegateForColumn(0, Delegate_2()) # <- column 1  
    #t.setItemDelegate(Delegate()) # <- all cells
    t.show()
    sys.exit(app.exec_())