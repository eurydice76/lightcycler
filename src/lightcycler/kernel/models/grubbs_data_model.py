import collections
import logging
import os
import re

from PyQt5 import QtCore, QtGui

import openpyxl

import tabula

import numpy as np

import pandas as pd


class GrubbsDataModel(QtCore.QAbstractTableModel):

    def __init__(self, cp_values, outliers_indices, *args, **kwargs):
        """Constructor.
        """

        super(GrubbsDataModel, self).__init__(*args, **kwargs)

        self._cp_values = cp_values

        self._outliers_indices = outliers_indices

    def columnCount(self, parent=None):
        """Return the number of columns of the model for a given parent.

        Returns:
            int: the number of columns
        """

        if not self._cp_values:
            return 0

        return max([len(v[1]) for v in self._cp_values])

    def data(self, index, role):
        """Get the data at a given index for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()
        col = index.column()

        if role == QtCore.Qt.DisplayRole:

            try:
                return self._cp_values[row][1][col]
            except IndexError:
                return QtCore.QVariant()

        elif role == QtCore.Qt.BackgroundRole:

            if (row, col) in self._outliers_indices:
                return QtGui.QBrush(QtGui.QColor(255, 119, 51))
            else:
                return QtGui.QBrush(QtCore.Qt.white)

    def headerData(self, idx, orientation, role):
        """Returns the header data for a given index, orientation and role.

        Args:
            idx (int): the index
            orientation (int): the orientation
            role (int): the role
        """

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Vertical:
                return self._cp_values[idx][0]

    def rowCount(self, parent=None):
        """Return the number of rows of the model for a given parent.

        Returns:
            int: the number of rows
        """

        if not self._cp_values:
            return 0

        return len(self._cp_values)
