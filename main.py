#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, math
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets, uic
from os import path
import codecs


class main(QMainWindow):
    def __init__(self):
        super(main, self).__init__()
        parent_dir = path.dirname(path.abspath(__file__))
        uic.loadUi(path.join(parent_dir, 'mainwindow.ui'), self)

        self.w = {
            'diam': self.edit_diam,
            'ex': self.edit_ex,
            'length': self.edit_length,
            'pitch': self.edit_pitch,
            'feed': self.edit_feed,
            'feedf': self.edit_feedf,
            'depth': self.edit_depth,
            'depthf': self.edit_depthf,
            'outang': self.edit_outang,
            'outdiam': self.edit_outdiam,
            'speed': self.edit_speed,
                }
        for wid in self.w:
            edit = self.w[wid]
            edit.textChanged.connect(self.EditFloatHandle)

        self.cb_dir.currentIndexChanged.connect(self.CbChangedHandle)
        self.bt_calc.clicked.connect(self.calc)
        self.bt_save.clicked.connect(self.save)


        self.data = {
            'diam': 'err',
            'ex': 'err',
            'length': 'err',
            'pitch': 'err',
            'feed': 'err',
            'feedf': 'err',
            'depth': 'err',
            'depthf': 'err',
            'dir': '0',
            'outang': 'err',
            'outdiam': 'err',
            'speed': 'err',
            }
        self.outfile = ''
        self.check_input()

    def CbChangedHandle(self):
        self.data['dir'] = self.sender().currentIndex()

    def EditFloatHandle(self):
        edit = self.sender()
        edit.name = edit.objectName()
        text = edit.text()
        text = text.replace(',', '.')
        edit.setText(text)
        try:
            out = float(text)
            if (out < 0):
                edit.setText(str(-out))
            edit.setStyleSheet('background-color: white;')
        except:
            edit.setStyleSheet('background-color: red;')
            out = 'err'
        self.data[edit.name.replace('edit_', '')] = out


    def check_input(self):
        for wid in self.w:
            edit = self.w[wid]
            text = edit.text()
            text = text.replace(',', '.')
            edit.setText(text)
            try:
                out = float(text)
                if (out < 0):
                    self.data[wid] = -out
                else:
                    self.data[wid] = out
                edit.setStyleSheet('background-color: white;')
            except:
                edit.setStyleSheet('background-color: red;')
                out = 'err'

    def save(self):
        suggest_name = 'worm_' + str(self.data['length']) + '_' + str(self.data['diam']) + '_' + str(self.data['ex'])
        save = QtWidgets.QFileDialog()
        self.outfile = save.getSaveFileName(self, '', suggest_name, "NGC (*.ngc);;TXT (*.txt);;All Files (*)")
        try:
            file = codecs.open(self.outfile[0], 'w', "utf-8")
            file.write(self.code_out.toPlainText())
            file.close()
        except IOError:
            self.dialog_out.append('-ошибка записи на диск')
        self.dialog_out.append('-сохранено в ' + self.outfile[0])


    def calc(self):

        if 'err' in self.data.values():
            self.dialog_out.setText('-ошибка ввода')
            self.bt_save.setEnabled(0)
        else:
            print(self.data)
            makecode1 = makecode(self.code_out, self.dialog_out, self.data)
            self.bt_save.setEnabled(1)

class makecode():
    def __init__(self, code_wid, dialog_wid, data):
        self.diam = data['diam']
        self.ex = data['ex']
        self.length = data['length']
        self.pitch = data['pitch']
        self.feed = data['feed']
        self.feedf = data['feedf']
        self.depth = data['depth']
        self.depthf = data['depthf']
        self.outang = math.tan(data['outang'] * math.pi / 180)
        self.outdiam = data['outdiam']
        self.speed = data['speed']
        self.dir = data['dir']
        self.oit = 100
        self.outenable = 1
        self.xhome = (self.diam / 2 + 5)
        self.precision = 6
        print(self.diam)

        if (self.outang == 0) and (self.outdiam == 0):
            self.outenable = False
        else:
            self.outenable = True

        dialog = ''
        code = ''
        err = 0

        if (self.diam == 0):
            dialog += '-Нулевой диаметр.' + '\n'
            err = 1
        if (self.ex == 0):
            dialog += '-Нулевой эксцентриситет.' + '\n'
            err = 1
        if (self.length == 0):
            dialog += '-Нулевая длина.' + '\n'
            err = 1
        if (self.pitch == 0):
            dialog += '-Нулевой шаг винта.' + '\n'
            err = 1
        if (self.feedf == 0):
            dialog += '-Нулевая подача.' + '\n'
            err = 1
        if (self.speed == 0):
            dialog += '-Нулевя скорость.' + '\n'
            err = 1
        if (self.depth != 0) and (self.feed == 0):
            dialog += '-Нулевая подача черновой обработки.' + '\n'
            err = 1
        if (self.outdiam != 0) and (self.outang == 0):
            dialog += '-Нулевой угол выхода.' + '\n'
            err = 1
        if (self.outdiam == 0) and (self.outang != 0):
            dialog += '-Нулевой диаметр выхода.' + '\n'
            err = 1
        if (self.speed == 0):
            dialog += '-Нулевая скорость.' + '\n'
            err = 1

        if err:
            dialog_wid.setText(dialog)
            return

        code += '%' + '\n'
        code += 'G93' + '\n'
        code += 'G90' + '\n'
        code += 'G1 X' + self.str(self.xhome) + ' Y0 Z0 A0 F100' + '\n'

        mode = 0
        if (self.feed != 0):
            mode += 1
        if (self.depth != 0):
            mode += 10
        if (self.feedf != 0):
            mode += 100
        if (self.depthf != 0):
            mode += 1000

        if mode == 1111:
            dialog += 'Черновой проход' + '\n'
            dialog += 'S= ' + self.str(self.feed) + ' мм/об' + '\n'
            dialog += 'Получистовой проход' + '\n'
            dialog += 'S= ' + self.str(self.feed) + ' мм/об' + '\n'
            dialog += 'Чистовой проход' + '\n'
            dialog += 'S= ' + self.str(self.feedf) + ' мм/об' + '\n'
            code += self.CalcRough(self.feed)
            code += self.CalcSemiF(self.feed)
            code += self.CalcF(self.feedf)
        elif mode == 1101:
            dialog += 'Получистовой проход' + '\n'
            dialog += 'S= ' + self.str(self.feed) + ' мм/об' + '\n'
            dialog += 'Чистовой проход' + '\n'
            dialog += 'S= ' + self.str(self.feedf) + ' мм/об' + '\n'
            code += self.CalcSemiF(self.feed)
            code += self.CalcF(self.feedf)
        elif mode == 1100:
            dialog += 'Получистовой проход' + '\n'
            dialog += 'S= ' + self.str(self.feedf) + ' мм/об' + '\n'
            dialog += 'Чистовой проход' + '\n'
            dialog += 'S= ' + self.str(self.feedf) + ' мм/об' + '\n'
            code += self.CalcSemiF(self.feedf)
            code += self.CalcF(self.feedf)
        elif mode == 100:
            dialog += 'Чистовой проход' + '\n'
            dialog += 'S= ' + self.str(self.feedf) + ' мм/об' + '\n'
            code += self.CalcF(self.feedf)
        elif mode == 111:
            dialog += 'Черновой проход' + '\n'
            dialog += 'S= ' + self.str(self.feed) + ' мм/об' + '\n'
            dialog += 'Чистовой проход' + '\n'
            dialog += 'S= ' + self.str(self.feedf) + ' мм/об' + '\n'
            code += self.CalcRough(self.feed)
            code += self.CalcF(self.feedf)
        elif mode == 1011:
            dialog += 'Черновой проход' + '\n'
            dialog += 'S= ' + self.str(self.feed) + ' мм/об' + '\n'
            dialog += 'Получистовой проход' + '\n'
            dialog += 'S= ' + self.str(self.feed) + ' мм/об' + '\n'
            dialog += 'Чистовой проход' + '\n'
            dialog += 'S= ' + self.str(self.feed) + ' мм/об' + '\n'
            code += self.CalcRough(self.feed)
            code += self.CalcSemiF(self.feed)
            code += self.CalcF(self.feed)
        code += '(конец программы) ' + '\n'
        code += '%' + '\n'

        code_wid.setText(code)
        dialog_wid.setText(dialog)

    def str(self, val):
        str = ('%.*f' % (self.precision, val)).rstrip('0').rstrip('.')
        return str

    def CalcSemiF(self, feed):
        turns = round(self.length / feed)
        if self.dir:
            adeg = 180 - (feed * 180 / self.pitch)
        else:
            adeg = 180 + (feed * 180 / self.pitch)
        textout = ''
        textout += 'G1 X' + self.str(self.diam / 2 + self.depthf) + ' Y0 Z0 A0 F100' + ' (начало получистового цикла)' + '\n'
        textout += 'G91' + '\n'
        textout += 'o' + self.str(self.oit) + ' repeat [' + self.str(turns) + ']' + '\n'
        textout += 'G2 X' + self.str(-2 * self.ex) + ' Y0 Z' + self.str(-feed / 2) + ' A' + self.str(adeg) + ' I' + str(-self.ex) + ' J0' + ' F' + self.str(self.speed * 2) + '\n'
        textout += 'G2 X' + self.str(2 * self.ex) + ' Y0 Z' + self.str(-feed / 2) + ' A' + self.str(adeg) + ' I' + str(self.ex) + ' J0' + ' F' + self.str(self.speed * 2) + '\n'
        textout += 'o' + self.str(self.oit) + ' endrepeat' + '\n'
        self.oit += 1
        if self.outenable:
            outcountsf = round((self.outdiam / 2 - self.diam / 2 + 2 * self.ex - self.depthf) / (feed / self.outang))
            textout += '\n'
            textout += 'o' + self.str(self.oit) + ' repeat [' + self.str(outcountsf) + ']' + ' (начало выхода)' + '\n'
            textout += 'G2 X' + self.str(-2 * self.ex + feed / self.outang / 2) + ' Y0 Z' + self.str(-feed / 2) + ' A180' + ' I' + self.str(-self.ex + feed / self.outang / 4) + ' J0' + ' F' + self.str(self.speed * 2) + '\n'
            textout += 'G2 X' + self.str(2 * self.ex + feed / self.outang / 2) + ' Y0 Z' + self.str(-feed / 2) + ' A180' + ' I' + self.str(self.ex + feed / self.outang / 4) + ' J0' + ' F' + self.str(self.speed * 2) + '\n'
            textout += 'o' + self.str(self.oit) + ' endrepeat' + '\n'
            self.oit += 1
        textout += 'G90' + '\n'
        textout += 'G0 X' + self.str(self.xhome) + '\n'
        textout += 'G0 Z0' + ' (конец выхода)' + '\n'
        textout += '\n'
        return textout

    def CalcRough(self, feed):
        passes = int((2 * self.ex - self.depthf) / self.depth)
        turns = round(self.length / feed)
        if self.dir:
            adeg = 180 - (feed * 180 / self.pitch)
        else:
            adeg = 180 + (feed * 180 / self.pitch)
        textout = ''
        for i in range(1, passes):
            textout += 'G1 X' + self.str(self.diam / 2 - i * self.depth + 2 * self.ex) + ' Y0 Z0 A0 F100' + ' (начало чернового цикла)' + '\n'
            textout += 'G91' + '\n'
            textout += 'o' + self.str(self.oit) + ' repeat [' + self.str(turns) + ']' + '\n'
            textout += 'G2 X' + self.str(-2 * self.ex) + ' Y0 Z' + self.str(-feed / 2) + ' A' + self.str(adeg) + ' I' + str(-self.ex) + ' J0' + ' F' + self.str(self.speed*2) + '\n'
            textout += 'G2 X' + self.str(2 * self.ex) + ' Y0 Z' + self.str(-feed / 2) + ' A' + self.str(adeg) + ' I' + self.str(self.ex) + ' J0' + ' F' + self.str(self.speed*2) + '\n'
            textout += 'o' + self.str(self.oit) + ' endrepeat' + '\n'
            self.oit += 1
            if self.outenable:
                outcounts = round((self.outdiam / 2 - self.diam / 2 + i * self.depth) / (feed / self.outang))
                textout += '\n';
                textout += 'o' + self.str(self.oit) + ' repeat [' + self.str(outcounts) + ']' + ' (начало выхода)' + '\n'
                textout += 'G2 X' + self.str(-2 * self.ex + feed / self.outang / 2) + ' Y0 Z' + self.str(-feed / 2) + ' A180' + ' I' + self.str(-self.ex + feed / self.outang / 4) + ' J0' + ' F' + self.str(self.speed*2) + '\n'
                textout += 'G2 X' + self.str(2 * self.ex + feed / self.outang / 2) + ' Y0 Z' + self.str(-feed / 2) + ' A180' + ' I' + self.str(self.ex + feed / self.outang / 4) + ' J0' + ' F' + self.str(self.speed*2) + '\n'
                textout += 'o' + self.str(self.oit) + ' endrepeat' + '\n'
                self.oit += 1
            textout += 'G90' + '\n'
            textout += 'G0 X' + self.str(self.xhome) + '\n'
            textout += 'G0 Z0' + ' (конец выхода)' + '\n'
            textout += '\n'
        return textout

    def CalcF(self, feed):
        turns = round(self.length / feed)
        if self.dir:
            adeg = 180 - (feed * 180 / self.pitch)
        else:
            adeg = 180 + (feed * 180 / self.pitch)
        textout = ''
        textout += 'G1 X' + self.str(self.diam / 2) + ' Y0 Z0 A0 F100' + ' (начало чистового цикла)' + '\n'
        textout += 'G91' + '\n'
        textout += 'o' + self.str(self.oit) + ' repeat [' + self.str(turns) + ']' + '\n'
        textout += 'G2 X' + self.str(-2 * self.ex) + ' Y0 Z' + self.str(-feed / 2) + ' A' + self.str(adeg) + ' I' + self.str(-self.ex) + ' J0' + ' F' + self.str(2 * self.speed) + '\n'
        textout += 'G2 X' + self.str(2 * self.ex) + ' Y0 Z' + self.str(-feed / 2) + ' A' + self.str(adeg) + ' I' + self.str(self.ex) + ' J0' + ' F' + self.str(2 * self.speed) + '\n'
        textout += 'o' + self.str(self.oit) + ' endrepeat' + '\n'
        self.oit += 1
        if self.outenable:
            outcounts = round((self.outdiam / 2 - self.diam / 2 + 2 * self.ex + 1) / (feed / self.outang))
            textout += '\n'
            textout += 'o' + self.str(self.oit) + ' repeat [' + self.str(outcounts) + ']' + ' (начало выхода)' + '\n'
            textout += 'G2 X' + self.str(-2 * self.ex + feed / self.outang / 2) + ' Y0 Z' + self.str(-feed / 2) + ' A180' + ' I' + self.str(-self.ex + feed / self.outang / 4) + ' J0' + ' F' + self.str(2 * self.speed) + '\n'
            textout += 'G2 X' + self.str(2 * self.ex + feed / self.outang / 2) + ' Y0 Z' + self.str(-feed / 2) + ' A180' + ' I' + self.str(self.ex + feed / self.outang / 4) + ' J0' + ' F' + self.str(2 * self.speed) + '\n'
            textout += 'o' + self.str(self.oit) + ' endrepeat' + '\n'
            self.oit += 1
        textout += 'G90' + '\n'
        textout += 'G0 X' + self.str(self.xhome) + '\n'
        textout += 'G0 Z0' + ' (конец выхода)' + '\n'
        return textout


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    app = QApplication([])
    window = main()
    window.show()
    sys.exit(app.exec_())
