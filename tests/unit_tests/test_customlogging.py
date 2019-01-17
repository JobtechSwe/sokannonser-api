#-*- coding: utf-8 -*-
import logging
import os
import sys
from io import StringIO

import pytest

from sokannonser import NarvalLogFormatter
from sokannonser import log as sokannonserlog


@pytest.mark.unit
def test_log_level_develop():
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    # sokannonserlog.debug(logging.getLevelName(sokannonserlog.getEffectiveLevel()) + ' log level activated.')
    NarvalLogFormatter.printTestLogMessages(sokannonserlog)

    log_level_name = logging.getLevelName(sokannonserlog.getEffectiveLevel())

    assert ('DEBUG' == log_level_name)


@pytest.mark.unit
def test_log_newlines_develop():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    root = logging.getLogger()
    log_stream = StringIO()

    string_io_handler = logging.StreamHandler(stream=log_stream)
    f = NarvalLogFormatter('%(asctime)s|%(levelname)s|%(name)s|MESSAGE: %(message)s', is_develop_mode=True)
    string_io_handler.setFormatter(f)
    root.addHandler(string_io_handler)
    root.handlers[0].setFormatter(f)
    # print('repr(f.linesep)', repr(f.linesep))
    # NarvalLogFormatter.printTestLogMessages(sokannonserlog)

    sokannonserlog.debug('''hello\nworld''')
    logrow_val = log_stream.getvalue()
    assert ('\r' not in logrow_val)

@pytest.mark.unit
def test_log_newlines_production():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    root = logging.getLogger()
    log_stream = StringIO()
    string_io_handler = logging.StreamHandler(stream=log_stream)
    f = NarvalLogFormatter('%(asctime)s|%(levelname)s|%(name)s|MESSAGE: %(message)s', is_develop_mode=False)
    string_io_handler.setFormatter(f)
    root.addHandler(string_io_handler)
    root.handlers[0].setFormatter(f)
    sokannonserlog.debug('''hello\nworld\r''')
    logrow_val = log_stream.getvalue()
    # print('logrow_val', logrow_val)
    assert ('hello\rworld\n' in logrow_val)

@pytest.mark.unit
def test_log_newlines_correct_lastchar():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    root = logging.getLogger()
    log_stream = StringIO()
    string_io_handler = logging.StreamHandler(stream=log_stream)
    f = NarvalLogFormatter('%(asctime)s|%(levelname)s|%(name)s|MESSAGE: %(message)s', is_develop_mode=False)
    string_io_handler.setFormatter(f)
    root.addHandler(string_io_handler)
    root.handlers[0].setFormatter(f)
    sokannonserlog.debug('''hello\nworld''')
    logrow_val = log_stream.getvalue()

    # print(type(logrow_val))
    # print('logrow_val', logrow_val)
    # print(type(repr(logrow_val)))
    assert (logrow_val.endswith('\n'))



if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra','-m unit'])