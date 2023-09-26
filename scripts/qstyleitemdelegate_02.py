#!/usr/bin/env python2
import os
import sys
import re

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, QString


class MyDelegate(QtGui.QStyledItemDelegate):

    def paint(self, painter, option, index):
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        painter.save()
        data = index.model().data(index, Qt.UserRole).toInt()
        option_rect = option.rect
        # if UserRole = 1 draw custom line
        if data[1]:
            if data[0] == QtGui.QAbstractItemView.AboveItem:
                line = QtCore.QLine(option_rect.topLeft(), option_rect.topRight())
                painter.drawLine(line)
            elif data[0] == QtGui.QAbstractItemView.BelowItem:
                line = QtCore.QLine(option_rect.bottomLeft(), option_rect.bottomRight())
                painter.drawLine(line)
            elif data[0] == QtGui.QAbstractItemView.OnItem:
                rect = QtCore.QRect(option_rect)
                painter.drawRect(rect)

        painter.restore()


class MyTreeWidget(QtGui.QTreeWidget):

    def paintEvent(self, event):
        painter = QtGui.QPainter(self.viewport())
        self.drawTree(painter, event.region())
        # in original implementation, it calls an inline function paintDropIndicator here

    def mouseMoveEvent(self, e):
        mimeData = self.model().mimeData(self.selectedIndexes())
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.exec_(QtCore.Qt.MoveAction)

    def dragMoveEvent(self, event):
        pos = event.pos()
        item = self.itemAt(pos)

        # If hovered over an item during drag, set UserRole = 1
        if item:
            index = self.indexFromItem(item)
            rect = self.visualRect(index)
            self.dropIndicatorPosition = self.position(event.pos(), rect, index)
            self.model().setData(index, self.dropIndicatorPosition, Qt.UserRole)

        iterator = QtGui.QTreeWidgetItemIterator(self)
        while iterator.value():
            item_iter = iterator.value()
            if item_iter is not item:
                _index = self.indexFromItem(item_iter, 0)
                self.model().setData(_index, QtGui.QAbstractItemView.OnViewport, Qt.UserRole)
            iterator += 1

        # This is necessary or else the previously drawn rect won't be erased
        self.viewport().update()

    def dropEvent(self, e):
        pos = e.pos()
        item = self.itemAt(pos)
        if item:
            index = self.indexFromItem(item)
            self.model().setData(index, 0, Qt.UserRole)

        QtGui.QTreeWidget.dropEvent(self, e)
        self.expandAll()

    def position(self, pos, rect, index):
        r = QtGui.QAbstractItemView.OnViewport
        # margin defaults to 2, it must be smaller than row height, or the drop onItem rect won't show
        margin = 10
        if pos.y() - rect.top() < margin:
            r = QtGui.QAbstractItemView.AboveItem
        elif rect.bottom() - pos.y() < margin:
            r = QtGui.QAbstractItemView.BelowItem
        elif rect.contains(pos, True):
            r = QtGui.QAbstractItemView.OnItem

        return r


class TheUI(QtGui.QDialog):

    def __init__(self, args=None, parent=None):
        super(TheUI, self).__init__(parent)
        self.layout1 = QtGui.QVBoxLayout(self)
        treeWidget = MyTreeWidget()

        # treeWidget.setSelectionMode( QtGui.QAbstractItemView.ExtendedSelection )

        button1 = QtGui.QPushButton('Add')
        button2 = QtGui.QPushButton('Add Child')

        self.layout1.addWidget(treeWidget)

        self.layout2 = QtGui.QHBoxLayout()
        self.layout2.addWidget(button1)
        self.layout2.addWidget(button2)

        self.layout1.addLayout(self.layout2)

        treeWidget.setHeaderHidden(True)

        treeWidget.setItemDelegate(MyDelegate())

        self.treeWidget = treeWidget
        self.button1 = button1
        self.button2 = button2
        self.button1.clicked.connect(lambda *x: self.addCmd())
        self.button2.clicked.connect(lambda *x: self.addChildCmd())

        HEADERS = ("script", "chunksize", "mem")
        self.treeWidget.setHeaderLabels(HEADERS)
        self.treeWidget.setColumnCount(len(HEADERS))

        self.treeWidget.setColumnWidth(0, 160)
        self.treeWidget.header().show()

        self.treeWidget.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.treeWidget.setStyleSheet('''
                                         QTreeView {
                                             show-decoration-selected: 1;
                                         }
                                         QTreeView::item:hover {
                                             background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
                                         }
                                         QTreeView::item:selected:active{
                                             background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);
                                         }
                                         QTreeView::item:selected:!active {
                                             background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);
                                         }
                                         ''')

        self.resize(500, 500)
        for i in xrange(6):
            item = self.addCmd(i)
            if i in (3, 4):
                self.addChildCmd()
                if i == 4:
                    self.addCmd('%s-2' % i, parent=item)

        self.treeWidget.expandAll()
        self.setStyleSheet("QTreeWidget::item{ height: 30px;  }")

    def addChildCmd(self):
        parent = self.treeWidget.currentItem()
        self.addCmd(parent=parent)
        self.treeWidget.setCurrentItem(parent)

    def addCmd(self, i=None, parent=None):
        'add a level to tree widget'

        root = self.treeWidget.invisibleRootItem()
        if not parent:
            parent = root

        if i is None:
            if parent == root:
                i = self.treeWidget.topLevelItemCount()
            else:
                i = str(parent.text(0))[7:]
                i = '%s-%s' % (i, parent.childCount() + 1)

        item = QtGui.QTreeWidgetItem(parent, ['script %s' % i, '1', '150'])

        self.treeWidget.setCurrentItem(item)
        self.treeWidget.expandAll()
        return item

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui = TheUI()
    gui.show()
    app.exec_()