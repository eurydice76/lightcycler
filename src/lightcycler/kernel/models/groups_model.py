import collections
import logging

from PyQt5 import QtCore, QtGui

import numpy as np

import pandas as pd

import numpy as np

import scipy.stats as stats

import scikit_posthocs as sk

from lightcycler.kernel.models.droppable_model import DroppableModel


class GroupsModel(QtCore.QAbstractListModel):

    model = QtCore.Qt.UserRole + 1

    selected = QtCore.Qt.UserRole + 2

    display_group_contents = QtCore.pyqtSignal(QtCore.QModelIndex)

    def __init__(self, *args, **kwargs):

        super(GroupsModel, self).__init__(*args, **kwargs)

        self._dynamic_matrix = pd.DataFrame()

        self._groups = []

        self._group_control = -1

    def add_group(self, group_name):
        """Add a new group to the model.

        Args:
            group_name (str): the name of the group to add
        """

        group_names = [group[0] for group in self._groups]
        if group_name in group_names:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._groups.append([group_name, DroppableModel(self), True])

        self.endInsertRows()

    def clear(self):

        self.reset()

    def compute_ct_matrix(self):
        """Compute the so-called CT matrix
        """

        if self._group_control == -1:
            logging.info('No group control set')
            return None

        group_control = self._groups[self._group_control][0]

        # Compute the statistics, especially the mean, for each gene of the group control.
        statistics = self.get_statistics(selected_groups=[group_control])

        average_matrix = pd.DataFrame(np.nan, index=self._dynamic_matrix.index, columns=self._dynamic_matrix.columns)

        for gene in average_matrix.index:
            if gene in statistics:
                average_matrix.loc[gene, :] = statistics[gene].loc['mean', group_control]
            else:
                average_matrix.loc[gene, :] = np.nan

        means = pd.DataFrame(np.nan, index=self._dynamic_matrix.index, columns=self._dynamic_matrix.columns)

        for i in range(len(self._dynamic_matrix.index)):
            for j in range(len(self._dynamic_matrix.columns)):
                if self._dynamic_matrix.iloc[i, j]:
                    means.iloc[i, j] = np.mean(self._dynamic_matrix.iloc[i, j])

        ct_matrix = average_matrix - means

        ct_matrix = pow(2, ct_matrix)

        ct_matrix = ct_matrix.round(3)

        return ct_matrix

    def compute_geometric_means(self, ct_matrix, reference_genes):
        """Compute the geometric mean for each sample across given reference genes.
        """

        means = pd.DataFrame(np.nan, index=ct_matrix.index, columns=ct_matrix.columns)

        for i in range(len(ct_matrix.index)):
            for j in range(len(ct_matrix.columns)):
                if ct_matrix.iloc[i, j]:
                    means.iloc[i, j] = np.mean(ct_matrix.iloc[i, j])

        geom_means = stats.gmean(means.loc[reference_genes, :], axis=0)

        geom_means = pd.DataFrame([geom_means], index=['gmean'], columns=means.columns)

        return geom_means

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

        if not self._groups:
            return QtCore.QVariant()

        idx = index.row()

        group, model, selected = self._groups[idx]

        if role == QtCore.Qt.DisplayRole:
            return group

        elif role == QtCore.Qt.CheckStateRole:
            return QtCore.Qt.Checked if selected else QtCore.Qt.Unchecked

        elif role == QtCore.Qt.ForegroundRole:

            return QtGui.QBrush(QtCore.Qt.red) if idx == self._group_control else QtGui.QBrush(QtCore.Qt.black)

        elif role == GroupsModel.model:
            return model

        elif role == GroupsModel.selected:
            return selected

    def export(self, workbook):
        """Export the model to an excel spreadsheet

        Args:
            workbook (openpyxl.workbook.workbook.Workbook): the excel spreadsheet
        """

        workbook.create_sheet('groups')
        worksheet = workbook.get_sheet_by_name('groups')

        sorted_groups = sorted(self._groups, key=lambda x: x[0])

        for i, (group, samples_per_group_model, _) in enumerate(sorted_groups):
            worksheet.cell(row=1, column=i+1).value = group
            for j, sample in enumerate(samples_per_group_model.items):
                worksheet.cell(row=j+2, column=i+1).value = sample

        workbook.create_sheet('statistics-cp')
        worksheet = workbook.get_sheet_by_name('statistics-cp')

        statistics = self.get_statistics(selected_groups=[v[0] for v in sorted_groups])
        if statistics is None:
            return

        for i, (gene, statistics_per_gene) in enumerate(statistics.items()):
            worksheet.cell(row=5*i+1, column=1).value = gene
            worksheet.cell(row=5*i+2, column=1).value = 'mean'
            worksheet.cell(row=5*i+3, column=1).value = 'stddev'
            worksheet.cell(row=5*i+4, column=1).value = 'n'
            for j, group in enumerate(statistics_per_gene.columns):
                worksheet.cell(row=5*i+1, column=j+2).value = group
                worksheet.cell(row=5*i+2, column=j+2).value = statistics_per_gene.loc['mean', group]
                worksheet.cell(row=5*i+3, column=j+2).value = statistics_per_gene.loc['stddev', group]
                worksheet.cell(row=5*i+4, column=j+2).value = statistics_per_gene.loc['n', group]

    def flags(self, index):
        """Return the flag for the item with specified index.

        Returns:
            int: the flag
        """

        default_flags = super(GroupsModel, self).flags(index)

        return QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | default_flags

    def get_statistics(self, selected_groups=None):
        """Returns the mean, error and number of samples for each selected group and gene.

        Args:
            selected_groups (list of str): list of selected groups

        Returns:
            collections.OrderedDict: a mapping betweeb the name of the gene and a pandas.DataFrame storing the mean, error and number of value for each selected group
        """

        if selected_groups is None:
            selected_groups = [(group, model) for group, model, _ in self._groups]
        else:
            model_per_group = dict([(group, model) for group, model, _ in self._groups])
            temp = []
            for group in selected_groups:
                if group in model_per_group:
                    temp.append((group, model_per_group[group]))
            selected_groups = temp

        if not selected_groups:
            logging.error('No group selected for getting statistics')
            return None

        statistics = collections.OrderedDict()

        genes = self._dynamic_matrix.index

        for gene in genes:

            statistics_per_gene = pd.DataFrame(np.nan, index=['mean', 'stddev', 'n'], columns=[group for group, _ in selected_groups])

            for group, samples_per_group_model in selected_groups:

                values = []
                for sample in samples_per_group_model.items:
                    values.extend(self._dynamic_matrix.loc[gene, sample])
                if values:
                    mean = np.mean(values)
                    stddev = np.std(values)
                else:
                    mean = stddev = np.nan

                statistics_per_gene.loc['mean', group] = mean
                statistics_per_gene.loc['stddev', group] = stddev
                statistics_per_gene.loc['n', group] = len(values)

            statistics[gene] = statistics_per_gene

        return statistics

    @ property
    def group_control(self):

        return self._group_control

    @ group_control.setter
    def group_control(self, index):
        """Set the group control.

        Args:
            index (int): the index of the group control
        """

        if index < 0 or index >= self.rowCount():
            return

        self._group_control = index

        self.layoutChanged.emit()

    @ property
    def groups(self):
        """Return the groups.

        Returns:
            list of 3-tuples: the groups
        """

        return self._groups

    def is_selected(self, index):
        """Return true if the group with given index is selected.

        Args:
            index (int): the index of the group
        """

        if index < 0 or index >= len(self._groups):
            return False

        return self._groups[index][2]

    def load_groups(self, groups):
        """Reset the model and load groups.

        Args:
            groups (pd.DataFrame): the groups
        """

        self._groups = []

        for group in groups.columns:
            samples = groups[group].dropna()

            samples_per_group_model = DroppableModel()
            for sample in samples:
                samples_per_group_model.add_item(sample)

            self._groups.append([group, samples_per_group_model, True])

        self.layoutChanged.emit()

    def on_display_group_contents(self, index):
        """Event handler called when the user double click on group item. Pops up a dialog which shows the contents of the selected group.

        Args:
            index (PyQt5.QtCore.QModelIndex): the selected item
        """

        self.display_group_contents.emit(index)

    def on_set_dynamic_matrix(self, dynamic_matrix):
        """Event handler which set the dynamic matrix.

        Args:
            _dynamic_matrix (pandas.DataFrame): the dynamic matrix
        """

        self._dynamic_matrix = dynamic_matrix

    def remove_groups(self, items):
        """
        """

        indexes = []

        group_names = [group[0] for group in self._groups]

        for item in items:
            try:
                indexes.append(group_names.index(item))
            except ValueError:
                continue

        indexes.reverse()

        for idx in indexes:
            self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
            del self._groups[idx]
            self.endRemoveRows()

    def reset(self):
        """Reset the model.
        """

        self.__dynamic_matrix = pd.DataFrame()
        self._groups = []
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        """Returns the number of groups.
        """

        return len(self._groups)

    def run_student_test(self):
        """Perform a pairwise student test over the groups.
        """

        student_test_per_gene = collections.OrderedDict()

        selected_groups = [(group, samples_per_group_model) for group, samples_per_group_model, selected in self._groups if selected]

        selected_group_names = [group[0] for group in selected_groups]

        # Loop over the gene and perform the student test for this gene
        for gene in self._dynamic_matrix.index:
            df = pd.DataFrame(columns=['groups', 'means'])
            for group, samples_per_group_model in selected_groups:

                for sample in samples_per_group_model.items:
                    if not self._dynamic_matrix.loc[gene, sample]:
                        continue
                    mean = np.mean(self._dynamic_matrix.loc[gene, sample])
                    row = pd.DataFrame([[group, mean]], columns=['groups', 'means'])
                    df = pd.concat([df, row])

            if not df.empty:

                if df.isnull().values.any():
                    logging.warning('NaN values detected for {} group in {} gene'.format(group, gene))

                # Any kind of error must be caught here
                try:
                    student_test_per_gene[gene] = sk.posthoc_ttest(df, val_col='means', group_col='groups', p_adjust='holm')
                except:
                    logging.error('Can not compute student test for gene {}. Skip it.'.format(gene))
                    student_test_per_gene[gene] = pd.DataFrame(np.nan, index=selected_group_names, columns=selected_group_names)
                    continue

            else:
                logging.warning('No group selected for student test for gene {}'.format(gene))

        return student_test_per_gene

    def setData(self, index, value, role):
        """Set the data for a given index and given role.

        Args:
            value (QtCore.QVariant): the data
        """

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()

        if role == QtCore.Qt.CheckStateRole:
            self._groups[row][2] = True if value == QtCore.Qt.Checked else False
            return True

        elif role == QtCore.Qt.EditRole:

            self._groups[row][0] = value

        return super(GroupsModel, self).setData(index, value, role)

    def sort(self):
        """Sort the model.
        """

        self._groups.sort(key=lambda x: x[0])
        self.layoutChanged.emit()
