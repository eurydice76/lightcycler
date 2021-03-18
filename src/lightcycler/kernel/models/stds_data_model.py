import numpy as np

from PyQt5 import QtCore, QtGui

from lightcycler.kernel.models.pandas_data_model import PandasDataModel


class StdsDataModel(PandasDataModel):

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            elif role == QtCore.Qt.BackgroundRole:
                row = index.row()
                col = index.column()
                if np.isnan(self._data.iloc[row, col]):
                    return QtGui.QBrush(QtGui.QColor(255, 119, 51))
                else:

                    value = self._data.iloc[row, col]
                    if value < 0.3:
                        return QtGui.QBrush(QtGui.QColor(255, 255, 255))
                    elif value >= 0.3 and value < 0.5:
                        return QtGui.QBrush(QtGui.QColor(220, 220, 220))
                    elif value >= 0.5 and value < 1.0:
                        return QtGui.QBrush(QtGui.QColor(160, 160, 160))
                    else:
                        return QtGui.QBrush(QtGui.QColor(100, 100, 100))

        return None
