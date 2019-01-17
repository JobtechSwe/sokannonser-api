import logging
import json
import os


class NarvalLogFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', is_develop_mode=False):
        super().__init__(fmt, datefmt, style)

        self.is_develop_mode = is_develop_mode

        if(is_develop_mode==True):
            self.linesep = os.linesep
            print('NarvalLogFormatter configured to development mode.')
        else:
            self.linesep = '\r'
            print('NarvalLogFormatter is configured with newline separator \\r')

    def lastreplace(self, str, old, new):
        li = str.rsplit(old, maxsplit=1)
        return new.join(li)

    def format(self, record):
        is_json_str = False
        json_obj = None
        # print(type(record.msg))
        if type(record.msg) == str and '{' in record.msg:
            try:
                json_obj = json.loads(record.msg)
                is_json_str = True
            except ValueError:
                # print('Got ValueError when trying json.loads')
                pass

        if is_json_str and json_obj is not None:
            message = json.dumps(json_obj)
            record.msg = message

        result = super(NarvalLogFormatter, self).format(record)
        # Replace all occurances of '|n' to wanted lineseparator
        # since openshift makes newline with '\r' and new logrow
        # with '\n'
        result = result.replace('\n', self.linesep)
        # Replace last occurrence of lineseparator to '\n’ to
        # create separate log-row in openshift.
        if result.endswith(self.linesep):
            result = self.lastreplace(result, self.linesep, '\n')

        if not self.is_develop_mode and not result.endswith('\n'):
            result = result + '\n'

        return result


    def formatException(self, exc_info):
        result = super(NarvalLogFormatter, self).formatException(exc_info)
        return result.replace('\n', self.linesep)

    def formatMessage(self, record):
        result = super(NarvalLogFormatter, self).formatMessage(record)
        return result.replace('\n', self.linesep)

    @classmethod
    def printTestLogMessages(cls, log):
        log.info('Testing log levels - BEGIN')

        test_dict = {
            "prop1":"dict_val1",
            "prop2": "dict_val2",
            "inner": {
                "innerobjprop":"innerobjval"
            }
        }
        log.debug(test_dict)

        test_json = '''{
            "jsontestprop1": "jsontestval1",
            "jsontestprop2": "jsontestval2"

        }'''

        log.debug(test_json)

        test_non_json = '''function test{
                                alert('just testing logging...');
                            }'''
        log.debug(test_non_json)


        try:
            json_obj = json.loads('not a json-string')
        except ValueError as e:
            logging.exception('Testmessage for exception')


        test_newline = '''hello
                    world
                    test'''
        log.debug(test_newline)


        log.info('Testing log levels - END')


