from PyQt5 import QtCore, QtGui, QtWidgets


class GroupContentsListView(QtWidgets.QListView):
    """This class implements an interface for listviews onto which data can be dropped in.
    """

    def __init__(self, samples_model, *args, **kwargs):
        super(GroupContentsListView, self).__init__(*args, **kwargs)

        self._samples_model = samples_model

        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dragMoveEvent(self, event):
        """Event triggered when the dragged item is moved above the target widget.
        """

        event.accept()

    def dragEnterEvent(self, event):
        """Event triggered when the dragged item enter into this widget.
        """

        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Event triggered when the dragged item is dropped into this widget.
        """

        if self._samples_model is None:
            return

        target_model = self.model()
        if target_model is None:
            return

        # Copy the mime data into a source model to get their underlying value
        source_model = QtGui.QStandardItemModel()
        source_model.dropMimeData(event.mimeData(), QtCore.Qt.CopyAction, 0, 0, QtCore.QModelIndex())
        dragged_items = [source_model.item(i, 0).text() for i in range(source_model.rowCount())]

        self._samples_model.remove_items(dragged_items)

        # # Drop only those items which are not present in this widget
        current_items = [target_model.data(target_model.index(i), QtCore.Qt.DisplayRole) for i in range(target_model.rowCount())]
        for name in dragged_items:
            if name in current_items:
                continue

            target_model.add_sample(name)

    def set_samples_model(self, samples_model):
        """Attach a samples model to the widget
        """

        self._samples_model = samples_model
