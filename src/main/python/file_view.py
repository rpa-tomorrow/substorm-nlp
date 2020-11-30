from PyQt5 import QtWidgets, QtGui, QtCore
from functools import partial
import os
import sys


class FileView(QtWidgets.QWidget):
    def __init__(self, main_window, design_view, model, action_is_save, *args, **kwargs):
        super(FileView, self).__init__(*args, **kwargs)
        self.main_window = main_window
        self.design_view = design_view
        self.model = model
        self.action_is_save = action_is_save # false = action is loading

        widget = QtWidgets.QWidget();
        widget.setMaximumWidth(960)
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(widget)

        layout = QtWidgets.QGridLayout()

        self.file_system_model = QtWidgets.QFileSystemModel()
        self.file_system_model.setRootPath(QtCore.QDir.rootPath())
        self.file_system_model.setNameFilters(["*.rpa"])
        
        self.tree_view = QtWidgets.QListView()
        self.tree_view.setObjectName("fileView")
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setRootIndex(self.file_system_model.index(os.getcwd()))
        self.tree_view.clicked.connect(self.on_treeView_clicked)
        self.tree_view.doubleClicked.connect(self.on_treeView_double_clicked)

        self.current_dir_view = CurrentDirectoryView(self.tree_view, self.file_system_model)

        self.filename_view = QtWidgets.QLineEdit(self.model.filename)
        if self.action_is_save:
            self.filename_view.returnPressed.connect(self.save_model)
        else:
            self.filename_view.returnPressed.connect(self.load_model)

        self.fileformat_view = QtWidgets.QComboBox()
        self.fileformat_view.addItem("Robotic Process Automation (*.rpa)", ".rpa")
        self.cancel_button = QtWidgets.QPushButton("Cancel");
        self.cancel_button.clicked.connect(lambda: self.main_window.set_active_view(0))
        action_str = "Save" if self.action_is_save else "Load"
        self.action_button = QtWidgets.QPushButton(action_str + " Process");
        if self.action_is_save:
            self.action_button.clicked.connect(self.save_model)
        else:
            self.action_button.clicked.connect(self.load_model)

        layout.addWidget(self.current_dir_view, 0, 0, 1, 4)
        layout.addWidget(self.tree_view, 1, 0, 1, 4)
        layout.addWidget(QtWidgets.QLabel("File name: "), 2, 0)
        layout.addWidget(self.filename_view, 2, 1, 1, 3)
        layout.addWidget(QtWidgets.QLabel("File format: "), 3, 0)
        layout.addWidget(self.fileformat_view, 3, 1, 1, 3)
        layout.addWidget(self.action_button, 4, 2)
        layout.addWidget(self.cancel_button, 4, 3)
        layout.setColumnStretch(1, 1)
        layout.setVerticalSpacing(8)

        self.setLayout(main_layout)
        widget.setLayout(layout)
        
    def save_model(self, filepath=None):
        path = filepath or self.filename_view.text() + ".rpa"
        self.model.save(path)
        self.main_window.set_info_message("Wrote " + path + ".")
        self.main_window.set_active_view(0)

    def load_model(self, filepath=None):
        path = filepath or self.filename_view.text() + ".rpa"
        try:
            self.model.load(path)
        except Exception:
            self.main_window.set_info_message("Could not find file `" + path + "`.")
            return
            
        self.design_view.rebuild_from_loaded_model()
        self.main_window.set_active_view(0)

    def enter_directory_index(self, index):
        self.tree_view.setRootIndex(index)
        self.current_dir_view.set_current_directory_index(index)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_treeView_clicked(self, index):
        index = self.file_system_model.index(index.row(), 0, index.parent())
        if not index.child(0, 0).isValid():
            filename = self.file_system_model.fileName(index)
            filename = ".".join(filename.split(".")[:-1])
            filepath = self.file_system_model.filePath(index)
            self.filename_view.setText(filename)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_treeView_double_clicked(self, index):
        index = self.file_system_model.index(index.row(), 0, index.parent())
        if index.child(0, 0).isValid():
            self.enter_directory_index(index)
        else:
            filepath = self.file_system_model.filePath(index)
            if self.action_is_save:
                self.save_model(filepath)
            else:
                self.load_model(filepath)


class CurrentDirectoryView(QtWidgets.QFrame):
    def __init__(self, tree_view, file_system_model, *args, **kwargs):
        super(CurrentDirectoryView, self).__init__(*args, **kwargs)
        self.tree_view = tree_view
        self.file_system_model = file_system_model
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)

        self.visited_stack = []

        self.next_dir_button = QtWidgets.QToolButton()
        self.next_dir_button.setText("\uf061")
        self.next_dir_button.setObjectName("fileNav")
        self.next_dir_button.clicked.connect(self.set_next_directory)

        self.prev_dir_button = QtWidgets.QToolButton()
        self.prev_dir_button.setObjectName("fileNav")
        self.prev_dir_button.setText("\uf060")
        self.prev_dir_button.clicked.connect(self.set_prev_directory)

        self.layout.insertWidget(0, self.next_dir_button)
        self.layout.insertWidget(0, self.prev_dir_button)

        self.set_current_directory_index(self.tree_view.rootIndex())

        self.setLayout(self.layout)

    def set_next_directory(self):
        if len(self.visited_stack) > 0:
            index = self.visited_stack.pop()
            if index and index.isValid():
                self.set_current_directory_index(index)
                self.tree_view.update()
        
    def set_prev_directory(self):
        index = self.tree_view.rootIndex()
        self.visited_stack.append(index)
        index = index.parent()
        if index and index.isValid():
            self.set_current_directory_index(index)

    def set_current_directory_index(self, index):
        self.tree_view.setRootIndex(index)
        
        self.prev_dir_button.setEnabled(index.parent().isValid());
        self.next_dir_button.setEnabled(len(self.visited_stack) > 0);
        
        item = self.layout.takeAt(2)
        while item:
            if item.widget():
                item.widget().deleteLater()
            self.layout.removeItem(item)
            item = self.layout.takeAt(2)

        while index and index.isValid():
            btn = QtWidgets.QPushButton(str(index.data()))
            btn.index = index
            btn.clicked.connect(partial(self.directory_button_clicked, index))
            self.layout.insertWidget(2, btn)
            index = index.parent()
            if index and index.isValid():
                self.layout.insertWidget(2, QtWidgets.QLabel(">"))

        self.layout.addStretch(1)
        self.tree_view.update()
        self.update()

    def directory_button_clicked(self, index):
        if index and index.isValid():
            self.visited_stack.append(self.tree_view.rootIndex())
            self.set_current_directory_index(index)


# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app

    appctxt, window = initialize_app()
    window.set_active_view(1)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)