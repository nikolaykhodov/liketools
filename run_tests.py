# -*- coding: utf8 -*-

import unittest
from tests import ram_storage
from tests import persist_storage
from tests import sched_test
from tests import vk_api
from tests import settings_test
import sys

runner = unittest.TextTestRunner(verbosity=2)
loader = unittest.TestLoader()
suites = {}

suites['storage'] = storage_suite = loader.loadTestsFromModule(ram_storage)
storage_suite.addTests(loader.loadTestsFromModule(persist_storage))

suites['scheduler'] = scheduler_suite = loader.loadTestsFromModule(sched_test)

suites['api'] = api_suite = loader.loadTestsFromModule(vk_api)
suites['settings'] = settings_suite = loader.loadTestsFromModule(settings_test)

if len(sys.argv) < 2:
    runner.run(storage_suite)
    runner.run(scheduler_suite)
    runner.run(api_suite)
else:
    runner.run(suites[sys.argv[1]])

