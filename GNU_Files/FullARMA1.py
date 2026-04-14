#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: FullARMA1
# Author: Noctis Solutions
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from datetime import datetime
from gnuradio import blocks
import pmt
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
import os
import osmosdr
import time
import sip
import threading



class FullARMA1(gr.top_block, Qt.QWidget):

    def __init__(self, buflen=4096, instance=0, num_buffers=16, num_xfers=8, rx_frequency=101.5e6, serial="", verbosity="info"):
        gr.top_block.__init__(self, "FullARMA1", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("FullARMA1")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "FullARMA1")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Parameters
        ##################################################
        self.buflen = buflen
        self.instance = instance
        self.num_buffers = num_buffers
        self.num_xfers = num_xfers
        self.rx_frequency = rx_frequency
        self.serial = serial
        self.verbosity = verbosity

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6
        self.rx_gain = rx_gain = 15
        self.record_file_path = record_file_path = r"/mnt/nvme/recordings"
        self.note = note = 'RECORDING_NOTE'
        self.gui_rx_frequency = gui_rx_frequency = rx_frequency
        self.bladerf_selection = bladerf_selection = str(instance) if serial == "" else serial
        self.tx_mode = tx_mode = 0
        self.rec_button = rec_button = 0
        self.filename = filename = record_file_path+note+"_"+str(int(gui_rx_frequency))+"Hz_"+str(int(samp_rate))+"sps_"+str(int(rx_gain))+"dB_"+".cfile"
        self.bladerf_args = bladerf_args = "bladerf=" + bladerf_selection + ",buffers=" + str(num_buffers) + ",buflen=" + str(buflen) + ",num_xfers=" + str(num_xfers) + ",verbosity="+verbosity

        ##################################################
        # Blocks
        ##################################################

        self._tx_mode_choices = {'Pressed': 10, 'Released': 0}

        _tx_mode_toggle_switch = qtgui.GrToggleSwitch(self.set_tx_mode, 'TX', self._tx_mode_choices, False, "red", "gray", 4, 50, 1, 1, self, 'value')
        self.tx_mode = _tx_mode_toggle_switch

        self.top_grid_layout.addWidget(_tx_mode_toggle_switch, 8, 4, 1, 1)
        for r in range(8, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 5):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._gui_rx_frequency_range = qtgui.Range(0, 3.8e9, 1e6, rx_frequency, 200)
        self._gui_rx_frequency_win = qtgui.RangeWidget(self._gui_rx_frequency_range, self.set_gui_rx_frequency, "Frequency", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._gui_rx_frequency_win, 0, 0, 1, 5)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 5):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rec_button_choices = {'Pressed': 1, 'Released': 0}

        _rec_button_toggle_switch = qtgui.GrToggleSwitch(self.set_rec_button, 'RECORD', self._rec_button_choices, False, "red", "gray", 4, 50, 1, 1, self, 'value')
        self.rec_button = _rec_button_toggle_switch

        self.top_grid_layout.addWidget(_rec_button_toggle_switch, 8, 0, 1, 1)
        for r in range(8, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            16384, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            gui_rx_frequency, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(0.1)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)

        self.qtgui_freq_sink_x_0.disable_legend()


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 2, 0, 5, 5)
        for r in range(2, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 5):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + bladerf_args
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(gui_rx_frequency, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(rx_gain, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + bladerf_args
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(150e6, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(tx_mode, 0)
        self.osmosdr_sink_0.set_if_gain(0, 0)
        self.osmosdr_sink_0.set_bb_gain(0, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self._note_tool_bar = Qt.QToolBar(self)
        self._note_tool_bar.addWidget(Qt.QLabel("REC NOTE (press enter to update)" + ": "))
        self._note_line_edit = Qt.QLineEdit(str(self.note))
        self._note_tool_bar.addWidget(self._note_line_edit)
        self._note_line_edit.editingFinished.connect(
            lambda: self.set_note(str(str(self._note_line_edit.text()))))
        self.top_grid_layout.addWidget(self._note_tool_bar, 7, 0, 1, 4)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, '/mnt/nvme/recordings/RECORDING_NOTE_101500000Hz_2000000sps_20dB_.cfile', False, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, filename, False)
        self.blocks_file_sink_0.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.qtgui_freq_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "FullARMA1")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_buflen(self):
        return self.buflen

    def set_buflen(self, buflen):
        self.buflen = buflen
        self.set_bladerf_args("bladerf=" + self.bladerf_selection + ",buffers=" + str(self.num_buffers) + ",buflen=" + str(self.buflen) + ",num_xfers=" + str(self.num_xfers) + ",verbosity="+self.verbosity)

    def get_instance(self):
        return self.instance

    def set_instance(self, instance):
        self.instance = instance
        self.set_bladerf_selection(str(self.instance) if self.serial == "" else self.serial)

    def get_num_buffers(self):
        return self.num_buffers

    def set_num_buffers(self, num_buffers):
        self.num_buffers = num_buffers
        self.set_bladerf_args("bladerf=" + self.bladerf_selection + ",buffers=" + str(self.num_buffers) + ",buflen=" + str(self.buflen) + ",num_xfers=" + str(self.num_xfers) + ",verbosity="+self.verbosity)

    def get_num_xfers(self):
        return self.num_xfers

    def set_num_xfers(self, num_xfers):
        self.num_xfers = num_xfers
        self.set_bladerf_args("bladerf=" + self.bladerf_selection + ",buffers=" + str(self.num_buffers) + ",buflen=" + str(self.buflen) + ",num_xfers=" + str(self.num_xfers) + ",verbosity="+self.verbosity)

    def get_rx_frequency(self):
        return self.rx_frequency

    def set_rx_frequency(self, rx_frequency):
        self.rx_frequency = rx_frequency
        self.set_gui_rx_frequency(self.rx_frequency)

    def get_serial(self):
        return self.serial

    def set_serial(self, serial):
        self.serial = serial
        self.set_bladerf_selection(str(self.instance) if self.serial == "" else self.serial)

    def get_verbosity(self):
        return self.verbosity

    def set_verbosity(self, verbosity):
        self.verbosity = verbosity
        self.set_bladerf_args("bladerf=" + self.bladerf_selection + ",buffers=" + str(self.num_buffers) + ",buflen=" + str(self.buflen) + ",num_xfers=" + str(self.num_xfers) + ",verbosity="+self.verbosity)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_filename(self.record_file_path+self.note+"_"+str(int(self.gui_rx_frequency))+"Hz_"+str(int(self.samp_rate))+"sps_"+str(int(self.rx_gain))+"dB_"+".cfile")
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.gui_rx_frequency, self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.set_filename(self.record_file_path+self.note+"_"+str(int(self.gui_rx_frequency))+"Hz_"+str(int(self.samp_rate))+"sps_"+str(int(self.rx_gain))+"dB_"+".cfile")
        self.osmosdr_source_0.set_gain(self.rx_gain, 0)

    def get_record_file_path(self):
        return self.record_file_path

    def set_record_file_path(self, record_file_path):
        self.record_file_path = record_file_path
        self.set_filename(self.record_file_path+self.note+"_"+str(int(self.gui_rx_frequency))+"Hz_"+str(int(self.samp_rate))+"sps_"+str(int(self.rx_gain))+"dB_"+".cfile")

    def get_note(self):
        return self.note

    def set_note(self, note):
        self.note = note
        self.set_filename(self.record_file_path+self.note+"_"+str(int(self.gui_rx_frequency))+"Hz_"+str(int(self.samp_rate))+"sps_"+str(int(self.rx_gain))+"dB_"+".cfile")
        Qt.QMetaObject.invokeMethod(self._note_line_edit, "setText", Qt.Q_ARG("QString", str(self.note)))

    def get_gui_rx_frequency(self):
        return self.gui_rx_frequency

    def set_gui_rx_frequency(self, gui_rx_frequency):
        self.gui_rx_frequency = gui_rx_frequency
        self.set_filename(self.record_file_path+self.note+"_"+str(int(self.gui_rx_frequency))+"Hz_"+str(int(self.samp_rate))+"sps_"+str(int(self.rx_gain))+"dB_"+".cfile")
        self.osmosdr_source_0.set_center_freq(self.gui_rx_frequency, 0)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.gui_rx_frequency, self.samp_rate)

    def get_bladerf_selection(self):
        return self.bladerf_selection

    def set_bladerf_selection(self, bladerf_selection):
        self.bladerf_selection = bladerf_selection
        self.set_bladerf_args("bladerf=" + self.bladerf_selection + ",buffers=" + str(self.num_buffers) + ",buflen=" + str(self.buflen) + ",num_xfers=" + str(self.num_xfers) + ",verbosity="+self.verbosity)

    def get_tx_mode(self):
        return self.tx_mode

    def set_tx_mode(self, tx_mode):
        self.tx_mode = tx_mode
        self.osmosdr_sink_0.set_gain(self.tx_mode, 0)

    def get_rec_button(self):
        return self.rec_button

    def set_rec_button(self, rec_button):
        self.rec_button = rec_button

    def get_filename(self):
        return self.filename

    def set_filename(self, filename):
        self.filename = filename
        self.blocks_file_sink_0.open(self.filename)

    def get_bladerf_args(self):
        return self.bladerf_args

    def set_bladerf_args(self, bladerf_args):
        self.bladerf_args = bladerf_args



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--instance", dest="instance", type=intx, default=0,
        help="Set 0-indexed device instance describing device to use. Ignored if a serial-number is provided. [default=%(default)r]")
    parser.add_argument(
        "--num-buffers", dest="num_buffers", type=intx, default=16,
        help="Set Number of buffers to use [default=%(default)r]")
    parser.add_argument(
        "--num-xfers", dest="num_xfers", type=intx, default=8,
        help="Set Number of maximum in-flight USB transfers. Should be <= (num-buffers / 2). [default=%(default)r]")
    parser.add_argument(
        "-f", "--rx-frequency", dest="rx_frequency", type=eng_float, default=eng_notation.num_to_str(float(101.5e6)),
        help="Set Frequency [default=%(default)r]")
    return parser


def main(top_block_cls=FullARMA1, options=None):
    if options is None:
        options = argument_parser().parse_args()

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(instance=options.instance, num_buffers=options.num_buffers, num_xfers=options.num_xfers, rx_frequency=options.rx_frequency)

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
