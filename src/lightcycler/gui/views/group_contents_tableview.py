from PyQt5 import QtCore, QtGui, QtWidgets


class GroupContentsTableView(QtWidgets.QTableView):
    """
    """

    def __init__(self, *args, **kwargs):

        super(GroupContentsTableView, self).__init__(*args, **kwargs)

        self.setSelectionMode(QtWidgets.QTableView.SingleSelection)

    def keyPressEvent(self, event):
        """Event handler for keyboard interaction.

        Args:
            event (PyQt5.QtGui.QKeyEvent): the keyboard event
        """

        if event.key() == QtCore.Qt.Key_Delete:

            sample_contents_model = self.model()
            if sample_contents_model is None:
                return

            current_index = self.currentIndex()
            sample_contents_model.remove_contents(current_index.row(), current_index.column())

        else:
            super(GroupContentsTableView, self).keyPressEvent(event)
