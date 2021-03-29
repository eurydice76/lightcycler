import numpy as np

from PyQt5 import QtCore, QtGui

from lightcycler.kernel.models.pandas_data_model import PandasDataModel


class DiffDataModel(PandasDataModel):

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            elif role == QtCore.Qt.BackgroundRole:
                row = index.row()
                col = index.column()
                # The nan will be in orange/red
                if np.isnan(self._data.iloc[row, col]):
                    return QtGui.QBrush(QtGui.QColor(255, 119, 51))
                else:

                    # The zero will be in orange/red
                    if self._data.iloc[row, col] > 0.5:
                        return QtGui.QBrush(QtGui.QColor(255, 119, 51))
                    # Otherwise use a grayscale
                    else:
                        return QtGui.QBrush(QtCore.Qt.white)

        return None
