# -*- coding: utf-8 -*-
import common
import cherrypy
from bs4 import BeautifulSoup

import lib.item
import lib.itembuilder
from plugins.backend import Backend as Root
from tests.backend.cptestcase import BaseCherryPyTestCase
from tests.mock.core import MockSmartHome



def setUpModule():
    bs = MockBackendServer()
    sh = bs._sh
    cherrypy.tree.mount(Root(backendserver=bs,developer_mode=True), '/')
    cherrypy.engine.start()
setup_module = setUpModule


def tearDownModule():
    cherrypy.engine.exit()
teardown_module = tearDownModule


class TestCherryPyApp(BaseCherryPyTestCase):
    def test_backendIntegration(self):
        response = self.request('/index')
        self.assertEqual(response.output_status, b'200 OK')
        body = BeautifulSoup(response.body[0])
        self.assertEqual( str(body.find("a", href="logics.html"))[:2], '<a' )
        self.assertEqual( str(body.find("a", href="logics_blockly.html"))[:2], '<a' )

    def test_logics_blockly_html(self):
        response = self.request('/logics_blockly_html')
        self.assertEqual(response.output_status, b'200 OK')
        resp_body = str(response.body[0],'utf-8')
        self.assertRegex(resp_body, 'xml id="toolbox"')
        self.assertRegex(resp_body, 'div id="content_blocks"')
        self.assertRegex(resp_body, '<category name="Trigger">')
        # self.assertEqual(response.body, ['hello world'])

    def test_DynToolbox(self):
        response = self.request('/logics_blockly_html')
        #resp_body = str(response.body[0],'utf-8')
        bs_body = BeautifulSoup(response.body[0])
        #items = bs_body.find("category", name="SmartHome Items")
        shItemsCat = bs_body.xml.find_all(attrs={'name': 'SmartHome Items'})[0]
        # print(shItemsCat)
        # print("categories: {}".format(len(list(shItemsCat.find_all("category")))) )
        # print("    blocks: {}".format(len(shItemsCat.find_all("block", type="sh_item_obj") )) )
        self.assertEqual(len(list(shItemsCat.find_all("block", type="sh_item_obj") )), 9 )
        self.assertEqual(len(list(shItemsCat.find_all("category") )), 6 )

    def test_logics_blockly_load(self):
        response = self.request('/logics_blockly_load')
        self.assertEqual(response.output_status, b'200 OK')
        resp_xml = str(response.body[0],'utf-8')
        #print(resp_xml)
        self.assertRegex(resp_xml, '<field name="N">Unit Test</field>')
        self.assertRegex(resp_xml, '<field name="P">testen.unit.test</field>')
        self.assertRegex(resp_xml, '<field name="T">bool</field>')



    # def test_logics_blockly_load(self):
    #     with open(fn_py, 'w') as fpy:
    #         with open(fn_xml, 'w') as fxml:
    #             fpy.write(py)
    #             fxml.write(xml)

    # def test_echo(self):
    #     response = self.request('/echo', msg="hey there")
    #     self.assertEqual(response.output_status, '200 OK')
    #     self.assertEqual(response.body, ["hey there"])
    #
    #     response = self.request('/echo', method='POST', msg="back from the future")
    #     self.assertEqual(response.output_status, '200 OK')
    #     self.assertEqual(response.body, ["back from the future"])
    #


class MockSmartHome():

    class MockScheduler():
        def add(self, name, obj, prio=3, cron=None, cycle=None, value=None, offset=None, next=None):
            print(name)
            print( obj)
            print(obj.__self__.get_instance_name())
            # __logs = {}
    _sh = None
    __item_dict = {}
    __items = []
    __children = []
    _plugins = []
    scheduler = MockScheduler()
    base_dir = common.BASE
    _logic_dir = base_dir + "/tests/resources/"


    def __init__(self):

        #############################################################
        # Init Items
        #############################################################
        self._sh = self
        item_conf = None
        item_conf = lib.config.parse("resources/blockly_items.conf", item_conf)

        ib = lib.itembuilder.ItemBuilder(self)
        ib.build_itemtree(item_conf, self)
        self.__item_dict, self.__items = ib.get_items()
        ib.run_items()

        # for attr, value in item_conf.items():
        #     if isinstance(value, dict):
        #         child_path = attr
        #         child = lib.item.Item(self, self, child_path, value)
        #         vars(self)[attr] = child
        #         self.add_item(child_path, child)
        #         self.__children.append(child)
        # # del(item_conf)  # clean up
        # for item in self.return_items():
        #     item._init_prerun()
        # for item in self.return_items():
        #     item._init_run()
        # self.item_count = len(self.__items)
        # self.logger.info("Items: {}".format(self.item_count))


    # def add_log(self, name, log):
    #     self.__logs[name] = log
    def now(self):
        import datetime
        return datetime.datetime.now()
    def add_item(self, path, item):
        #print("added {} at {}".format(item, path))
        print(path)
        if path not in self.__items:
            self.__items.append(path)
        self.__item_dict[path] = item

    def return_item(self, string):
        if string in self.__items:
            return self.__item_dict[string]

    def return_items(self):
        for item in self.__items:
            yield self.__item_dict[item]
    def return_plugins(self):
        for plugin in self._plugins:
            yield plugin
    def append_child(self, child,name):
        self.__children.append(child)
        # add top level itemst to SmartHome object.
        vars(self)[name] = child

class MockBackendServer():
    _sh = MockSmartHome()

    def __init__(self):
        self._sh.with_items_from(common.BASE + "/tests/resources/blockly_items.conf")

        # HACK: Make tests work! Backend accesses private field _logic_dir
        # directly instead of using a method (the field was remove in the
        # meantime). Setting this just to make it work again.
        self._sh._logic_dir = common.BASE + "/tests/resources/"


if __name__ == '__main__':
    import unittest
    unittest.main()
