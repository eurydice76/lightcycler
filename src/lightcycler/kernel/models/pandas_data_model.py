from PyQt5 import QtCore, QtGui


class PandasDataModel(QtCore.QAbstractTableModel):

    def __init__(self, data, parent):
        super(PandasDataModel, self).__init__(parent)
        self._data = data
        self._colored_rows = {}

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            elif role == QtCore.Qt.BackgroundRole:
                return self._colored_rows.get(index.row(), QtGui.QColor('white'))

        return None

    def headerData(self, col, orientation, role):
        """
        """

        if self._data.empty:
            return None

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._data.columns[col]
            else:
                return self._data.index[col]
        return None

    def setColoredRows(self, rows):
        """Sets the rows which will be colored.
        """

        self._colored_rows = rows

        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()), [QtCore.Qt.BackgroundRole])

    @property
    def dataframe(self):

        return self._data

    @dataframe.setter
    def dataframe(self, dataframe):

        self._data = dataframe
