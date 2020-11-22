import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog

import ui
import dialog
from one_perm_key import encrypt_file, decrypt_file
from one_perm_brute_force import brute_force_file


class BruteForceResultDialog(QtWidgets.QDialog, dialog.Ui_Dialog):

    def set_errors_count(self, errors: int):
        self.errors.setText(f'Неверных слов: {errors}')

    def set_text(self, text: str):
        self.textBrowser.setText(text)

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)


class MainApp(QtWidgets.QMainWindow, ui.Ui_MainWindow):

    def show_error(self, error: str):
        self.error_dialog.setText(error)
        self.error_dialog.show()

    def show_info(self, message: str):
        self.info_dialog.setText(message)
        self.info_dialog.show()

    def show_brute_result(self, errors: int, text: str) -> bool:
        dlg = BruteForceResultDialog()
        dlg.set_errors_count(errors)
        dlg.set_text(text)
        result: int = dlg.exec_()
        return result > 0

    def set_encrypt_filepath(self, filepath: str):
        self.encrypt_filepath = filepath

    def set_decrypt_filepath(self, filepath: str):
        self.decrypt_filepath = filepath

    def set_brute_force_filepath(self, filepath: str):
        self.brute_force_filepath = filepath

    def set_keyword(self, keyword: str):
        self.keyword = keyword
        if self.keywordInput.text() != keyword:
            self.keywordInput.setText(keyword)
        if self.keywordInput_2.text() != keyword:
            self.keywordInput_2.setText(keyword)

    def set_max_errors(self, max_errors: str):
        try:
            if max_errors == '':
                self.max_errors: int = 0
            else:
                self.max_errors: int = int(max_errors)
        except ValueError:
            self.show_error('Неверный формат максимального числа ошибок')
            self.max_errors_input.setText('0')

    def encrypt_choose_file(self):
        self.encrypt_filepath = QFileDialog.getOpenFileName(self, 'Выберете файл для шифрования')[0]
        self.filepathInput.setText(self.encrypt_filepath)

    def decrypt_choose_file(self):
        self.decrypt_filepath = QFileDialog.getOpenFileName(self, 'Выберете файл для расшифровки')[0]
        self.filepathInput_2.setText(self.decrypt_filepath)

    def brute_force_choose_file(self):
        self.brute_force_filepath = QFileDialog.getOpenFileName(self, 'Выберете файл для взлома')[0]
        self.filepathInput_3.setText(self.brute_force_filepath)

    def encrypt_chosen_file(self):
        try:
            if self.encrypt_filepath == '':
                raise Exception('Файл не выбран')
            if self.keyword == '':
                raise Exception('Ключевое слово не указано')
            encrypt_file(self.encrypt_filepath, self.keyword)
            self.show_info('Зашифрованный файл создан рядом с исходным')
        except Exception as e:
            self.show_error(str(e))

    def decrypt_chosen_file(self):
        try:
            if self.decrypt_filepath == '':
                raise Exception('Файл не выбран')
            if self.keyword == '':
                raise Exception('Ключевое слово не указано')
            decrypt_file(self.decrypt_filepath, self.keyword)
            self.show_info('Расшифрованный файл создан рядом с исходным')
        except Exception as e:
            self.show_error(str(e))

    def cancel_brute_force(self):
        self.stop_brute_force: bool = True

    def brute_force_chosen_file(self):
        try:
            if self.brute_force_filepath == '':
                raise Exception('Файл не выбран')

            decrypted_text: str = ''
            for step in brute_force_file(self.brute_force_filepath):
                QtWidgets.QApplication.processEvents()
                if self.stop_brute_force:
                    break
                self.bruteForceBar.setValue(int(step['progress']))
                self.bruteForceBar.setFormat(str(step['current_try']))
                if step['errors'] <= self.max_errors:
                    save_now: bool = self.show_brute_result(step['errors'], step['permed_text'])
                    if save_now:
                        decrypted_text = step['permed_text']
                        break
            if not self.stop_brute_force:
                output_filename: str = self.brute_force_filepath.replace('_encrypted', '_hacked')
                with open(output_filename, 'w') as output:
                    output.write(decrypted_text)
                self.show_info('Взломанный файл создан рядом с исходным')
            else:
                self.show_info('Взлом завершен')
        except ZeroDivisionError:
            self.show_error('Файл не может быть взломан')
        except Exception as e:
            self.show_error(str(e))
        finally:
            self.bruteForceBar.setValue(0)
            self.bruteForceBar.setFormat('0')
            self.stop_brute_force: bool = False

    def __init__(self):
        super().__init__()
        self.encrypt_filepath: str = ''
        self.decrypt_filepath: str = ''
        self.brute_force_filepath: str = ''
        self.keyword: str = ''
        self.max_errors: int = 0
        self.stop_brute_force: bool = False

        self.setupUi(self)

        self.max_errors_input.textEdited.connect(self.set_max_errors)

        self.error_dialog = QMessageBox()
        self.error_dialog.setIcon(QMessageBox.Critical)
        self.error_dialog.setStandardButtons(QMessageBox.Ok)
        self.error_dialog.setWindowTitle('Ошибка')

        self.info_dialog = QMessageBox()
        self.info_dialog.setIcon(QMessageBox.Information)
        self.info_dialog.setStandardButtons(QMessageBox.Ok)
        self.info_dialog.setWindowTitle('Результат')

        self.brute_result_dialog = QDialog()

        self.filepathButton.clicked.connect(self.encrypt_choose_file)
        self.filepathButton_2.clicked.connect(self.decrypt_choose_file)
        self.filepathButton_3.clicked.connect(self.brute_force_choose_file)

        self.filepathInput.textEdited.connect(self.set_encrypt_filepath)
        self.filepathInput_2.textEdited.connect(self.set_decrypt_filepath)
        self.filepathInput_3.textEdited.connect(self.set_brute_force_filepath)

        self.keywordInput.textEdited.connect(self.set_keyword)
        self.keywordInput_2.textEdited.connect(self.set_keyword)

        self.encryptButton.clicked.connect(self.encrypt_chosen_file)
        self.decryptButton.clicked.connect(self.decrypt_chosen_file)
        self.bruteForceButton.clicked.connect(self.brute_force_chosen_file)
        self.cancelBruteForceButton.clicked.connect(self.cancel_brute_force)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
