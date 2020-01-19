import unittest
from unittest.mock import Mock

from b3.functions import splitDSN
from b3.storage import Storage
from b3.storage import getStorage
from b3.storage.mysql import MysqlStorage
from b3.storage.sqlite import SqliteStorage
from tests import B3TestCase

is_mysql_ready = True
no_mysql_reason = ''

try:
    import pymysql
except ImportError:
    try:
        import mysql.connector
    except ImportError:
        is_mysql_ready = False
        no_mysql_reason = "no pymysql or mysql.connector module available"


class Test_Storage(B3TestCase):
    storage = None

    def setUp(self):
        B3TestCase.setUp(self)
        self.storage = Storage()

    def test_getCounts(self):
        self.assertRaises(NotImplementedError, self.storage.getCounts)

    def test_getClient(self):
        self.assertRaises(NotImplementedError, self.storage.getClient, Mock())

    def test_getClientsMatching(self):
        self.assertRaises(NotImplementedError, self.storage.getClientsMatching, Mock())

    def test_setClient(self):
        self.assertRaises(NotImplementedError, self.storage.setClient, Mock())

    def test_setClientAlias(self):
        self.assertRaises(NotImplementedError, self.storage.setClientAlias, Mock())

    def test_getClientAlias(self):
        self.assertRaises(NotImplementedError, self.storage.getClientAlias, Mock())

    def test_getClientAliases(self):
        self.assertRaises(NotImplementedError, self.storage.getClientAliases, Mock())

    def test_setClientIpAddresse(self):
        self.assertRaises(NotImplementedError, self.storage.setClientIpAddress, Mock())

    def test_getClientIpAddress(self):
        self.assertRaises(NotImplementedError, self.storage.getClientIpAddress, Mock())

    def test_getClientIpAddresses(self):
        self.assertRaises(NotImplementedError, self.storage.getClientIpAddresses, Mock())

    def test_setClientPenalty(self):
        self.assertRaises(NotImplementedError, self.storage.setClientPenalty, Mock())

    def test_getClientPenalty(self):
        self.assertRaises(NotImplementedError, self.storage.getClientPenalty, Mock())

    def test_getClientPenalties(self):
        self.assertRaises(NotImplementedError, self.storage.getClientPenalties, Mock())

    def test_getClientLastPenalty(self):
        self.assertRaises(NotImplementedError, self.storage.getClientLastPenalty, Mock())

    def test_getClientFirstPenalty(self):
        self.assertRaises(NotImplementedError, self.storage.getClientFirstPenalty, Mock())

    def test_disableClientPenalties(self):
        self.assertRaises(NotImplementedError, self.storage.disableClientPenalties, Mock())

    def test_numPenalties(self):
        self.assertRaises(NotImplementedError, self.storage.numPenalties, Mock())

    def test_getGroups(self):
        self.assertRaises(NotImplementedError, self.storage.getGroups)

    def test_getGroup(self):
        self.assertRaises(NotImplementedError, self.storage.getGroup, Mock())


class Test_getStorage(unittest.TestCase):

    @unittest.skipIf(not is_mysql_ready, no_mysql_reason)
    def test_mysql(self):
        storage = getStorage('mysql://b3:password@localhost/b3', splitDSN('mysql://b3:password@localhost/b3'), Mock())
        self.assertIsInstance(storage, MysqlStorage)

    def test_sqlite(self):
        storage = getStorage('sqlite://:memory:', splitDSN('sqlite://:memory:'), Mock())
        self.assertIsInstance(storage, SqliteStorage)
