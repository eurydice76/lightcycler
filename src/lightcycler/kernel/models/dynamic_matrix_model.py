import collections
import logging
import os
import re

from PyQt5 import QtCore, QtGui

import openpyxl

import tabula

import numpy as np

import pandas as pd


class InvalidViewError(Exception):
    """Exception raised for dynamic matrix view related errors.
    """


class DynamicMatrixModel(QtCore.QAbstractTableModel):

    def __init__(self, *args, **kwargs):
        """Constructor.
        """

        super(DynamicMatrixModel, self).__init__(*args, **kwargs)

        self._view = 0

        self._n_values = pd.DataFrame()
        self._means = pd.DataFrame()
        self._stds = pd.DataFrame()

    def rowCount(self, parent=None):
        """Return the number of rows of the model for a given parent.

        Returns:
            int: the number of rows
        """

        return len(self._n_values.index)

    def columnCount(self, parent=None):
        """Return the number of columns of the model for a given parent.

        Returns:
            int: the number of columns
        """

        return len(self._n_values.columns)

    def data(self, index, role):
        """Get the data at a given index for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if self._n_values.empty:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()
        col = index.column()

        if self._view == 0:
            values = self._means

        elif self._view == 1:
            values = self._stds

        elif self._view == 2:
            values = self._n_values

        else:
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            return str(values.iloc[row, col])

        elif role == QtCore.Qt.BackgroundRole:

            if np.isnan(values.iloc[row, col]):
                return QtGui.QBrush(QtCore.Qt.red)
            else:
                min_value = np.nanmin(values)
                max_value = np.nanmax(values)

                gray_scale = 255 - int(128.0*(values.iloc[row, col] - min_value)/(max_value - min_value))

                return QtGui.QColor(gray_scale, gray_scale, gray_scale)

        elif role == QtCore.Qt.ToolTipRole:

            return str(self._dynamic_matrix.iloc[row, col])

    def export(self, filename):
        """Export the raw data to an excel spreadsheet.

        Args:
            filename (str): the name of the output excel file
        """

    def headerData(self, idx, orientation, role):
        """Returns the header data for a given index, orientation and role.

        Args:
            idx (int): the index
            orientation (int): the orientation
            role (int): the role
        """

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._n_values.columns[idx]
            else:
                return self._n_values.index[idx]

    def set_dynamic_matrix(self, rawdata_model):
        """Build the dynamic matrix from a rawdata model.

        Args:
            rawdata_model (lightcycler.kernel.models.rawdata_model.RawDataModel): the raw data model
        """

        rawdata = rawdata_model.rawdata

        genes = list(collections.OrderedDict.fromkeys(rawdata['Gene']))

        samples = list(collections.OrderedDict.fromkeys(rawdata['Name']))

        self._dynamic_matrix = pd.DataFrame(None, index=genes, columns=samples)
        for row in self._dynamic_matrix.index:
            for col in self._dynamic_matrix.columns:
                self._dynamic_matrix.loc[row, col] = []

        for i in range(len(rawdata.index)):
            columns = rawdata.iloc[i]
            gene = columns['Gene']
            sample = columns['Name']
            cp = columns['CP']
            self._dynamic_matrix.loc[gene, sample].append(cp)

        self._n_values = pd.DataFrame(0, index=self._dynamic_matrix.index, columns=self._dynamic_matrix.columns)
        self._means = pd.DataFrame(np.nan, index=self._dynamic_matrix.index, columns=self._dynamic_matrix.columns)
        self._stds = pd.DataFrame(np.nan, index=self._dynamic_matrix.index, columns=self._dynamic_matrix.columns)

        for i in range(len(self._dynamic_matrix.index)):
            for j in range(len(self._dynamic_matrix.columns)):
                self._n_values.iloc[i, j] = len(self._dynamic_matrix.iloc[i, j])
                if self._dynamic_matrix.iloc[i, j]:
                    self._means.iloc[i, j] = np.mean(self._dynamic_matrix.iloc[i, j])
                    self._stds.iloc[i, j] = np.std(self._dynamic_matrix.iloc[i, j])

        self._means = self._means.round(3)
        self._stds = self._stds.round(3)

        self.layoutChanged.emit()

    def set_view(self, view):

        if view not in range(3):
            raise InvalidViewError('The view must be an integer in [0,2]')

        self._view = view

        self.layoutChanged.emit()
