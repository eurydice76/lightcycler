import collections
import logging

from PyQt5 import QtCore, QtGui

import numpy as np

import pandas as pd

import numpy as np

import scipy.stats as stats

import scikit_posthocs as sk

from outliers import smirnov_grubbs as grubbs

from lightcycler.kernel.models.droppable_model import DroppableModel


def get_nested_indices(nested_list, index):
    """Return the nested indices matching a flattened index from a nested list.

    Example:
        get_nested_indices([[1,2,3],[4,5],[6,7,8,9]], 6) --> (2,1)
    """

    comp = 0
    for i in range(len(nested_list)):
        for j in range(len(nested_list[i])):
            if comp == index:
                return (i, j)
            comp += 1

    return None


class GroupsModel(QtCore.QAbstractListModel):

    model = QtCore.Qt.UserRole + 1

    selected = QtCore.Qt.UserRole + 2

    student_test_zones = ['ABCDE', 'ABCD', 'AB', 'CD', 'E', 'Z']

    def __init__(self, *args, **kwargs):
        """Constructor.
        """

        super(GroupsModel, self).__init__(*args, **kwargs)

        self._dynamic_matrices = None

        self._groups = []

        self._group_control = None

    def add_group(self, group_name):
        """Add a new group to the model.

        Args:
            group_name (str): the name of the group to add
        """

        # Check that the group has a unique name
        group_names = [group[0] for group in self._groups]
        if group_name in group_names:
            return

        # Update the model
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self._groups.append([group_name, DroppableModel(self), True])
        self.endInsertRows()

    def clear(self):
        """Clear the model by removing all groups.
        """

        self.reset()

    def compute_ct_matrix(self, ct_power):
        """Compute the CT matrix.

        Args:
            ct_power (float): the power used to compute the CT matrix
        """

        if self._group_control is None:
            logging.info('No group control set')
            return None

        # Compute the statistics, especially the mean, for each gene of the group control.
        statistics = self.get_statistics(selected_groups=[self._group_control])

        average_matrix = pd.DataFrame(np.nan, index=self._dynamic_matrix.index, columns=self._dynamic_matrix.columns)

        for gene in average_matrix.index:
            if gene in statistics:
                average_matrix.loc[gene, :] = statistics[gene].loc['mean', self._group_control]
            else:
                average_matrix.loc[gene, :] = np.nan

        means = pd.DataFrame(np.nan, index=self._dynamic_matrix.index, columns=self._dynamic_matrix.columns)

        for i in range(len(self._dynamic_matrix.index)):
            for j in range(len(self._dynamic_matrix.columns)):
                if self._dynamic_matrix.iloc[i, j]:
                    means.iloc[i, j] = np.mean(self._dynamic_matrix.iloc[i, j])

        ct_matrix = average_matrix - means

        ct_matrix = pow(ct_power, ct_matrix)

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

            return QtGui.QBrush(QtCore.Qt.red) if group == self._group_control else QtGui.QBrush(QtCore.Qt.black)

        elif role == GroupsModel.model:
            return model

        elif role == GroupsModel.selected:
            return selected

    def export(self, workbook):
        """Export the model to an excel spreadsheet

        Args:
            workbook (openpyxl.workbook.workbook.Workbook): the excel spreadsheet
        """

        # Create a worksheet which will store the groups contents
        worksheet = workbook.create_sheet('Groups')

        sorted_groups = sorted(self._groups, key=lambda x: x[0])

        for i, (group, samples_per_group_model, _) in enumerate(sorted_groups):
            worksheet.cell(row=1, column=i+1).value = group
            for j, sample in enumerate(samples_per_group_model.items):
                worksheet.cell(row=j+2, column=i+1).value = sample

        # Create a worksheet which will store the group control. If None has been set, the sheet will be empty
        worksheet = workbook.create_sheet('Group control')
        if self._group_control is not None:
            worksheet.cell(row=1, column=1).value = self._group_control

        # Create a worksheet for storing the results of the statistics computation
        worksheet = workbook.create_sheet('Statistics')

        statistics = self.get_statistics(selected_groups=[v[0] for v in sorted_groups])
        if not statistics:
            return

        comp = 1
        for gene, d in statistics.items():

            worksheet.cell(row=comp, column=1).value = gene

            for zone, df in d.items():
                comp += 1
                worksheet.cell(row=comp, column=1).value = zone

                comp += 1
                for i, v in enumerate(df.columns):
                    worksheet.cell(row=comp, column=i+2).value = v

                for i, row in enumerate(df.index):
                    comp += 1
                    worksheet.cell(row=comp, column=1).value = row
                    for j, _ in enumerate(df.columns):
                        worksheet.cell(row=comp, column=j+2).value = df.iloc[i, j]

                comp += 2

        # Create a worksheet for storing the results of the student tests
        worksheet = workbook.create_sheet('Student tests')

        student_test = self.run_student_test()

        comp = 1
        for gene, d in student_test.items():
            worksheet.cell(row=comp, column=1).value = gene

            for zone, df in d.items():
                comp += 1
                worksheet.cell(row=comp, column=1).value = zone

                comp += 1
                for i, v in enumerate(df.columns):
                    worksheet.cell(row=comp, column=i+2).value = v

                for i, row in enumerate(df.index):
                    comp += 1
                    worksheet.cell(row=comp, column=1).value = row
                    for j, _ in enumerate(df.columns):
                        worksheet.cell(row=comp, column=j+2).value = df.iloc[i, j]

                comp += 2

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
            collections.OrderedDict: the statistics for each gene and student test zone
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

        # Loop over the dynamc matrices
        for gene, df in self._dynamic_matrices.items():

            statistics[gene] = collections.OrderedDict()

            # Loop over the student test zones
            for zone in GroupsModel.student_test_zones:

                # The statistics will be stored in a pandas DataFramewhose indexes are resp. the average, the stds and the number of values and the columns are the group names
                statistics_per_gene_and_zone = pd.DataFrame(np.nan, index=['mean', 'stddev', 'n'], columns=[group for group, _ in selected_groups])

                # Loop over the selected groups
                for group, samples_per_group_model in selected_groups:

                    values = []
                    for sample in samples_per_group_model.items:
                        if sample not in df.columns:
                            continue
                        values.extend(df.loc[zone, sample])
                    if values:
                        mean = np.mean(values)
                        stddev = np.std(values)
                    else:
                        mean = stddev = np.nan

                    statistics_per_gene_and_zone.loc['mean', group] = mean
                    statistics_per_gene_and_zone.loc['stddev', group] = stddev
                    statistics_per_gene_and_zone.loc['n', group] = len(values)

                statistics[gene][zone] = statistics_per_gene_and_zone

        return statistics

    def get_outliers(self, group):
        """Compute the outliers for each gene and zone.
        """

        outliers = collections.OrderedDict()

        all_groups = dict([(group, model) for group, model, _ in self._groups])

        if group not in all_groups:
            logging.error('Unknown group: {}'.format(group))
        else:
            samples_per_group_model = all_groups[group]

            # Loop over the genes
            for gene, df in self._dynamic_matrices.items():

                outliers[gene] = collections.OrderedDict()

                # Loop over the zones used for the student test
                for zone in GroupsModel.student_test_zones:

                    values = []
                    for sample in samples_per_group_model.items:
                        # If the sample is not registered anymore in the dynamic matrix skip it
                        if sample not in df.columns:
                            continue
                        values.append((sample, df.loc[zone, sample]))

                    # Flatten the values in order to perform the Grubbs test
                    flattened_values = [vv for v in values for vv in v[1]]

                    if flattened_values:
                        # Retrieve the indices of the outliers
                        outliers_indices = grubbs.max_test_indices(flattened_values, alpha=0.05)
                        outliers_indices = [get_nested_indices(values, outlier) for outlier in outliers_indices if outlier is not None]

                        outliers[gene][zone] = (values, outliers_indices)
                    else:
                        outliers[gene][zone] = ([], [])

        return outliers

    @ property
    def group_control(self):

        return self._group_control

    @ group_control.setter
    def group_control(self, group):
        """Set the group control.

        Args:
            index (int): the index of the group control
        """

        group_names = [group for group, _, _ in self._groups]
        if group not in group_names:
            return

        self._group_control = group

        self.layoutChanged.emit()

    def get_group_control_contents(self):

        if self._group_control is None:
            return []

        for group, model, _ in self._groups:
            if group == self._group_control:
                return model.items
        else:
            return []

    @property
    def group_names(self):
        """Return the group names.
        """

        return [group for group, _, _ in self._groups]

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

    def on_set_dynamic_matrices(self, dynamic_matrices):
        """Event handler which set the dynamic matrices.

        Args:
            _dynamic_matrices (collections.OrderedDict: the dynamic matrices
        """

        self._dynamic_matrices = dynamic_matrices

    def remove_groups(self, items):
        """Remove groups from the models
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

        self.__dynamic_matrices = None
        self._groups = []
        self._group_control = None
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        """Returns the number of groups.
        """

        return len(self._groups)

    def run_student_test(self):
        """Perform a pairwise student test over the groups.
        """

        student_test_per_gene = collections.OrderedDict()

        if self._dynamic_matrices is None:
            return student_test_per_gene

        selected_groups = [(group, samples_per_group_model) for group, samples_per_group_model, selected in self._groups if selected]

        selected_group_names = [group[0] for group in selected_groups]

        # Loop over the gene and perform the student test for this gene
        for gene, dynamic_matrix in self._dynamic_matrices.items():

            # Create a dict for each student test zone
            student_test_per_gene[gene] = collections.OrderedDict()

            # Loop over the zones
            for zone in GroupsModel.student_test_zones:

                # Create a data frame which contains as entry the name of the group and the average of each sample
                df = pd.DataFrame(columns=['groups', 'averages'])

                for group, samples_per_group_model in selected_groups:

                    for sample in samples_per_group_model.items:

                        # Check that the sample is in the dynamic matrix
                        if sample not in dynamic_matrix.columns:
                            continue

                        if not dynamic_matrix.loc[zone, sample]:
                            continue

                        mean = np.mean(dynamic_matrix.loc[zone, sample])
                        row = pd.DataFrame([[group, mean]], columns=['groups', 'averages'])
                        df = pd.concat([df, row])

                # If the dataframe storing the group and average per sample is not empty compute the student test
                if not df.empty:

                    if df.isnull().values.any():
                        logging.warning('NaN values detected for {} group in zone {} of gene {}'.format(group, zone, gene))

                    # Any kind of error must be caught here
                    try:
                        student_test_per_gene[gene][zone] = sk.posthoc_ttest(df, val_col='averages', group_col='groups', p_adjust='holm')
                    except:
                        logging.error('Can not compute student test for gene {} zone {}. Skip it.'.format(gene, zone))
                        student_test_per_gene[gene][zone] = pd.DataFrame(np.nan, index=selected_group_names, columns=selected_group_names)
                        continue

                else:
                    logging.warning('No group selected for student test for gene {} zone {}'.format(gene, zone))

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

            # If the group under edition is the control group then update the group control too
            if self._groups[row][0] == self._group_control:
                self._group_control = value

            self._groups[row][0] = value

        return super(GroupsModel, self).setData(index, value, role)

    def sort(self):
        """Sort the model by sorting the groups by their name.
        """

        self._groups.sort(key=lambda x: x[0])
        self.layoutChanged.emit()
