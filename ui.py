import json

from calibre.gui2.actions import InterfaceAction
from calibre.ebooks.conversion.config import get_input_format_for_book
from calibre_plugins.ebook_translator import EbookTranslator
from calibre_plugins.ebook_translator.main import MainWindowFrame


try:
    from qt.core import QMenu, QMessageBox
except ImportError:
    from PyQt5.Qt import QMenu, QMessageBox

load_translations()


class EbookTranslatorGui(InterfaceAction):
    name = EbookTranslator.name
    action_spec = (
        _('Translate Book'), None, _('Translate Ebook Content'), None)

    def genesis(self):
        try:
            icon = get_icons('images/icon.png', name)
        except Exception:
            icon = get_icons('images/icon.png')

        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

        # menu = QMenu(self.gui)
        # test = menu.addAction(_('Setting'))
        # test.triggered.connect(self.setting)
        # self.qaction.setMenu(menu)

    def show_dialog(self):
        ebooks = self.get_selected_ebooks()

        if len(ebooks) < 1:
            alert = QMessageBox(self)
            alert.setIcon(QMessageBox.Warning)
            alert.setText(_('You must choose at least one ebook.'))
            alert.exec_()
            return

        window = MainWindowFrame(self, self.qaction.icon(), ebooks)
        window.setModal(True)
        window.setMinimumWidth(600)
        window.setMinimumHeight(530)
        window.setWindowTitle(
            '%s - %s' % (EbookTranslator.title, EbookTranslator.get_version()))
        window.setWindowIcon(self.qaction.icon())
        window.show()

    def setting(self):
        pass

    # {
    #     0: [
    #         'book_id': 123,  # book ID in db
    #         'test',  # Title
    #         {
    #             'mobi': '/path/to/ebook.mobi',  # Format 1
    #             'txt': '/path/to/ebook.txt',  # Format 2
    #         },
    #         'txt',  # Input format
    #         'epub',  # Output format
    #         'en-US',  # Source language
    #         'zh-CN',  # Target Language
    #     ]
    # }
    def get_selected_ebooks(self):
        ebooks = {}
        api = self.gui.current_db.new_api
        rows = self.gui.library_view.selectionModel().selectedRows()
        model = self.gui.library_view.model()
        for index, row in enumerate(rows):
            row_number = row.row()
            book_id = model.id(row)
            book_metadata = api.get_proxy_metadata(book_id)
            fmt, fmts = get_input_format_for_book(
                self.gui.current_db, book_id, 'epub')
            ebooks[index] = [
                book_id,
                model.title(row_number),
                dict(zip(
                    map(lambda fmt: fmt.lower(), fmts),
                    map(lambda fmt: api.format_abspath(book_id, fmt), fmts),
                )),
                fmt.lower(),
                None,
                book_metadata.language,
                None,
            ]
        return ebooks
