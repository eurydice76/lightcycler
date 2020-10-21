from PyQt5 import QtCore, QtWidgets

from lightcycler.gui.views.copy_pastable_tableview import CopyPastableTableView
from lightcycler.kernel.models.rq_matrix_model import RQMatrixModel


class RQMatrixWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):

        super(RQMatrixWidget, self).__init__(*args, **kwargs)

        self._init_ui()

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._rq_matrix_tableview)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._rq_matrix_tableview = CopyPastableTableView(delimiter=',')
        rq_matrix_model = RQMatrixModel(self)
        self._rq_matrix_tableview.setModel(rq_matrix_model)

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()

    def model(self):
        """Return the CT matrix underlying model.
        """

        return self._rq_matrix_tableview.model()
