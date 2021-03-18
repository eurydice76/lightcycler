from PyQt5 import QtCore, QtWidgets


class RawDataTableView(QtWidgets.QTableView):

    def delete(self):

        if self.selectionModel().hasSelection():
            indexes = [QtCore.QPersistentModelIndex(index) for index in self.selectionModel().selectedRows()]
            indexes = self.selectionModel().selectedRows()
            indexes.reverse()
            if not indexes:
                return
            self.model().remove_indexes([idx.row() for idx in indexes])

    def keyPressEvent(self, event):

        if event.key() in (QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete):
            self.delete()

        super(RawDataTableView, self).keyPressEvent(event)
