import numpy as np

from PyQt5 import QtCore, QtGui

from lightcycler.kernel.models.pandas_data_model import PandasDataModel


class NValuesDataModel(PandasDataModel):

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
                    min_value = np.nanmin(self._data)
                    max_value = np.nanmax(self._data)

                    # The zero will be in orange/red
                    if self._data.iloc[row, col] < 1.0e-9:
                        return QtGui.QBrush(QtGui.QColor(255, 119, 51))
                    # Otherwise use a grayscale
                    else:
                        if abs(max_value - min_value) < 1.0e-15:
                            return QtGui.QBrush(QtGui.QColor(255, 255, 255))
                        else:
                            gray_scale = 255 - int(128.0*(self._data.iloc[row, col] - min_value)/(max_value - min_value))
                            return QtGui.QColor(gray_scale, gray_scale, gray_scale)

        return None
