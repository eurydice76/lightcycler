from PyQt5 import QtCore, QtGui

import numpy as np

import pandas as pd


class RQMatrixModel(QtCore.QAbstractTableModel):

    def __init__(self, *args, **kwargs):
        """Constructor.
        """

        super(RQMatrixModel, self).__init__(*args, **kwargs)

        self._rq_matrix = pd.DataFrame()

    def columnCount(self, parent=None):
        """Return the number of columns of the model for a given parent.

        Returns:
            int: the number of columns
        """

        return len(self._rq_matrix.columns)

    def data(self, index, role):
        """Get the data at a given index for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if self._rq_matrix.empty:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()
        col = index.column()

        if role == QtCore.Qt.DisplayRole:
            return str(self._rq_matrix.iloc[row, col])

        elif role == QtCore.Qt.BackgroundRole:

            if np.isnan(self._rq_matrix.iloc[row, col]):
                return QtGui.QBrush(QtGui.QColor(255, 85, 51))
            else:
                min_value = np.nanmin(self._rq_matrix)
                max_value = np.nanmax(self._rq_matrix)

                gray_scale = 255 - int(128.0*(self._rq_matrix.iloc[row, col] - min_value)/(max_value - min_value))

                return QtGui.QColor(gray_scale, gray_scale, gray_scale)

    def headerData(self, idx, orientation, role):
        """Returns the header data for a given index, orientation and role.

        Args:
            idx (int): the index
            orientation (int): the orientation
            role (int): the role
        """

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._rq_matrix.columns[idx]
            else:
                return self._rq_matrix.index[idx]

    def rowCount(self, parent=None):
        """Return the number of rows of the model for a given parent.

        Returns:
            int: the number of rows
        """

        return len(self._rq_matrix.index)

    @property
    def rq_matrix(self):

        return self._rq_matrix

    @rq_matrix.setter
    def rq_matrix(self, rq_matrix):

        self._rq_matrix = rq_matrix
        self.layoutChanged.emit()
