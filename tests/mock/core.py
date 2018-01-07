
import os

import datetime
import dateutil.tz
import logging

import lib.config
import lib.connection

import lib.item
import lib.plugin
from lib.shtime import Shtime
from lib.module import Modules

from lib.model.smartplugin import SmartPlugin
from lib.constants import (YAML_FILE, CONF_FILE, DEFAULT_FILE)

from tests.common import BASE


logger = logging.getLogger('Mockup')


class MockScheduler():

    def __init__(self):
        # set scheduler_instance to MockScheduler instance
        import lib.scheduler
        lib.scheduler._scheduler_instance = self


    def add(self, name, obj, prio=3, cron=None, cycle=None, value=None, offset=None, next=None):
        logger.warning('MockScheduler (add): {}, cron={}, cycle={}, value={}, offset={}'.format( name, str(cron), str(cycle), str(value), str(offset) ))
        try:
            if isinstance(obj.__self__, SmartPlugin):
                name = name +'_'+ obj.__self__.get_instance_name()
        except:
            pass

    def remove(self, name):
        logger.warning('MockScheduler (remove): {}'.format( name ))


class MockSmartHome():

    _base_dir = BASE
    base_dir = _base_dir     # for external modules using that var (backend, ...?)
    _default_language = 'de'

    _etc_dir = os.path.join(_base_dir, 'tests', 'resources', 'etc')
#    _var_dir = os.path.join(_base_dir, 'var')
    _lib_dir = os.path.join(_base_dir, 'lib')
    _env_dir = os.path.join(_lib_dir, 'env' + os.path.sep)

    _module_conf_basename = os.path.join(_etc_dir,'module')
    _module_conf = ''	# is filled by module.py while reading the configuration file, needed by Backend plugin

    _plugin_conf_basename = os.path.join(_etc_dir,'plugin')
    _plugin_conf = ''	# is filled by plugin.py while reading the configuration file, needed by Backend plugin

    _env_logic_conf_basename = os.path.join( _env_dir ,'logic')
#    _items_dir = os.path.join(_base_dir, 'items'+os.path.sep)
    _logic_conf_basename = os.path.join(_etc_dir, 'logic')
    _logic_dir = os.path.join(_base_dir, 'tests', 'resources', 'logics'+os.path.sep)
#    _cache_dir = os.path.join(_var_dir,'cache'+os.path.sep)
#    _log_config = os.path.join(_etc_dir,'logging'+YAML_FILE)
#    _smarthome_conf_basename = None

    # the APIs available though the smarthome object instance:
    shtime = None

    plugins = None
    items = None
    logics = None
    scheduler = None

    _SmartHome__items = []


    def __init__(self):
        VERSION = '1.3c.'
        VERSION += '0.man'
        self.version = VERSION
        self.__logs = {}
        self.__item_dict = {}
        self.__items = []
        self.children = []
        self._use_modules = 'True'
        self._modules = []
        self._moduledict = {}
        self._plugins = []
        self._tzinfo = dateutil.tz.tzutc()
        self.scheduler = MockScheduler()
        self.connections = lib.connection.Connections()
        
        self.shtime = Shtime(self)
        # Start()
#        self.scheduler = lib.scheduler.Scheduler(self)
        self.modules = lib.module.Modules(self, configfile=self._module_conf_basename)
        self.items = lib.item.Items(self)
        self.plugins = lib.plugin.Plugins(self, configfile=self._plugin_conf_basename)
        

    def get_defaultlanguage(self):
        return self._default_language

    def set_defaultlanguage(self, language):
        self._default_language = language

    def get_basedir(self):
        return self._base_dir

    def getBaseDir(self):
        """ Deprecated """
        return self._base_dir

    def trigger(self, name, obj=None, by='Logic', source=None, value=None, dest=None, prio=3, dt=None):
        logger.warning('MockSmartHome (trigger): {}'.format(str(obj)))

    def with_plugins_from(self, conf):
        lib.plugin.Plugins._plugins = []
        lib.plugin.Plugins._threads = []
        self._plugins = lib.plugin.Plugins(self, conf)
        return self._plugins

    def with_modules_from(self, conf):
        lib.module.Modules._modules = []
        self._modules = lib.module.Modules(self, conf)
        return self._plugins

    def with_items_from(self, conf):
        item_conf = lib.config.parse(conf, None)
        for attr, value in item_conf.items():
            if isinstance(value, dict):
                child_path = attr
                try:
                    child = lib.item.Item(self, self, child_path, value)
                except Exception as e:
                    print("Item {}: problem creating: {}".format(child_path, e))
                else:
                    vars(self)[attr] = child
                    self.add_item(child_path, child)
                    self.children.append(child)
        return item_conf

    def add_log(self, name, log):
        self.__logs[name] = log

    def now(self):
        return datetime.datetime.now()

    def tzinfo(self):
        return self._tzinfo

    def add_item(self, path, item):
        if path not in self.__items:
            self.__items.append(path)
        self.__item_dict[path] = item

#    def return_item(self, string):
#        if string in self.__items:
#            return self.__item_dict[string]

#    def return_items(self):
#        for item in self.__items:
#            yield self.__item_dict[item]

    def return_item(self, string):
        return self.items.return_item(string)

    def return_items(self):
        return self.items.return_items()

    def return_plugins(self):
        for plugin in self._plugins:
            yield plugin

    def return_modules(self):
        l = []
        for module_key in self._moduledict.keys():
            l.append(module_key)
        return l

    def get_module(self, name):
        return self._moduledict.get(name)

    def string2bool(self, string):
        if isinstance(string, bool):
            return string
        if string.lower() in ['0', 'false', 'n', 'no', 'off']:
            return False
        if string.lower() in ['1', 'true', 'y', 'yes', 'on']:
            return True
        else:
            return None


    def return_none(self):
        return None

