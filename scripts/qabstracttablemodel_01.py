from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView
import sys


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.ItemDataRole.DisplayRole or role == QtCore.Qt.ItemDataRole.EditRole:
                value = self._data[index.row()][index.column()]
                return str(value)
                # return str(value)

    def setData(self, index, value, role):
        if role == QtCore.Qt.ItemDataRole.EditRole:
            self._data[index.row()][index.column()] = value
            return True
        return False

    def flags(self, index):
        return QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsEditable


class CustomTableView(QtWidgets.QTableView):
    link_activated = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)

        self.setMouseTracking(True)
        self._mousePressAnchor = ''
        self._lastHoveredAnchor = ''

    def mousePressEvent(self, event):
        anchor = self.anchorAt(event.pos())
        self._mousePressAnchor = anchor

    def mouseMoveEvent(self, event):
        anchor = self.anchorAt(event.pos())
        if self._mousePressAnchor != anchor:
            self._mousePressAnchor = ''

        if self._lastHoveredAnchor != anchor:
            self._lastHoveredAnchor = anchor
            if self._lastHoveredAnchor:
                QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            else:
                QtWidgets.QApplication.restoreOverrideCursor()

    def mouseReleaseEvent(self, event):
        if self._mousePressAnchor:
            anchor = self.anchorAt(event.pos())
            if anchor == self._mousePressAnchor:
                self.link_activated.emit(anchor)
            self._mousePressAnchor = ''

    def anchorAt(self, pos):
        index = self.indexAt(pos)
        if index.isValid():
            delegate = self.itemDelegate(index)
            if delegate:
                itemRect = self.visualRect(index)
                relativeClickPosition = pos - itemRect.topLeft()
                html = self.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
                return delegate.anchorAt(html, relativeClickPosition)
        return ''


class CustomDelegate(QtWidgets.QStyledItemDelegate):

    def anchorAt(self, html, point):
        doc = QtGui.QTextDocument()
        doc.setHtml(html)
        textLayout = doc.documentLayout()
        return textLayout.anchorAt(point)

    def paint(self, painter, option, index):
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        if options.widget:
            style = options.widget.style()
        else:
            style = QtWidgets.QApplication.style()

        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)
        options.text = ''

        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)
        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        textRect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText, options)

        painter.save()

        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        painter.translate(0, 0.5 * (options.rect.height() - doc.size().height()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())

        return QtCore.QSize(doc.idealWidth(), doc.size().height())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.table = CustomTableView()

        data = [
            ['<p style="color: #ffffff; background-color: #aa0000">test</p>', 9, 2],
            [1, '<b>Hello</b>', -1],
            [3, '<a href="https://stackoverflow.com/">Stackoverflow</a>', 2],
            ['<a href="https://www.google.com/">Google</a>', 3, 2],
            [5, 8, 9],
        ]

        self.model = PandasModel(data)
        self.table.setModel(self.model)

        self.table.setItemDelegate(CustomDelegate())
        self.setCentralWidget(self.table)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
