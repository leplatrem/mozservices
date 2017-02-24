
import os
import json
import logging
import unittest2

from testfixtures import LogCapture

from mozsvc.util import JsonLogFormatter, MozLogFormatter


class TestJsonLogFormatter(unittest2.TestCase):

    def setUp(self):
        self.handler = LogCapture()
        self.formatter = JsonLogFormatter()

    def tearDown(self):
        self.handler.uninstall()

    def test_basic_operation(self):
        logging.debug("simple test")
        self.assertEquals(len(self.handler.records), 1)
        details = json.loads(self.formatter.format(self.handler.records[0]))
        self.assertEquals(details["message"], "simple test")
        self.assertEquals(details["name"], "root")
        self.assertEquals(details["pid"], os.getpid())
        self.assertEquals(details["op"], "root")
        self.assertEquals(details["v"], 1)
        self.assertTrue("time" in details)

    def test_custom_paramters(self):
        logger = logging.getLogger("mozsvc.test.test_logging")
        logger.warn("custom test %s", "one", extra={
            "more": "stuff",
            "op": "mytest",
        })
        self.assertEquals(len(self.handler.records), 1)
        details = json.loads(self.formatter.format(self.handler.records[0]))
        self.assertEquals(details["message"], "custom test one")
        self.assertEquals(details["name"], "mozsvc.test.test_logging")
        self.assertEquals(details["op"], "mytest")
        self.assertEquals(details["more"], "stuff")

    def test_logging_error_tracebacks(self):
        try:
            raise ValueError("\n")
        except Exception:
            logging.exception("there was an error")
        self.assertEquals(len(self.handler.records), 1)
        details = json.loads(self.formatter.format(self.handler.records[0]))
        self.assertEquals(details["message"], "there was an error")
        self.assertEquals(details["error"], "ValueError('\\n',)")
        tblines = details["traceback"].strip().split("\n")
        self.assertEquals(tblines[-1], details["error"])
        self.assertEquals(tblines[-2], "<type 'exceptions.ValueError'>")


class TestMozLogFormatter(unittest2.TestCase):

    def setUp(self):
        self.handler = LogCapture()
        self.formatter = MozLogFormatter()

    def tearDown(self):
        self.handler.uninstall()

    def test_basic_operation(self):
        logging.debug("simple test")
        self.assertEquals(len(self.handler.records), 1)
        details = json.loads(self.formatter.format(self.handler.records[0]))
        self.assertEquals(details["Fields"]["message"], "simple test")
        self.assertEquals(details["Logger"], "root")
        self.assertEquals(details["Severity"], 7)
        self.assertEquals(details["Pid"], os.getpid())
        self.assertEquals(details["Type"], "debug")
        self.assertEquals(details["EnvVersion"], 2)
        self.assertIn("Timestamp", details)

    def test_custom_paramters(self):
        logger = logging.getLogger("mozsvc.test.test_logging")
        logger.warn("custom test %s", "one", extra={
            "more": "stuff",
            "op": "mytest",
        })
        self.assertEquals(len(self.handler.records), 1)
        details = json.loads(self.formatter.format(self.handler.records[0]))
        self.assertEquals(details["Fields"]["message"], "custom test one")
        self.assertEquals(details["Logger"], "mozsvc")
        self.assertEquals(details["Type"], "test.test_logging")
        self.assertEquals(details["Fields"]["op"], "mytest")
        self.assertEquals(details["Fields"]["more"], "stuff")

    def test_logging_error_tracebacks(self):
        try:
            raise ValueError("\n")
        except Exception:
            logging.exception("there was an error")
        self.assertEquals(len(self.handler.records), 1)
        details = json.loads(self.formatter.format(self.handler.records[0]))
        fields = details["Fields"]
        self.assertEquals(fields["message"], "there was an error")
        self.assertEquals(fields["error"], "ValueError('\\n',)")
        tblines = fields["traceback"].strip().split("\n")
        self.assertEquals(tblines[-1], fields["error"])
        self.assertEquals(tblines[-2], "<type 'exceptions.ValueError'>")
