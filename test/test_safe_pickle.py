#!/usr/bin/env python
# Copyright (C) 2009-2014:
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.

#
# This file is used to test reading and processing of config files
#

from shinken_test import *


import cPickle as pickle
from cStringIO import StringIO

class SafeUnpickler(object):
    PICKLE_SAFE = {
      'copy_reg' : set(['_reconstructor']),
      '__builtin__' : set(['object']),
    }

    @classmethod
    def find_class(cls, module, name):
      if not module in cls.PICKLE_SAFE:
        raise pickle.UnpicklingError('Attempting to unpickle unsafe module %s' % module)
      __import__(module)
      mod = sys.modules[module]
      if not name in cls.PICKLE_SAFE[module]:
        raise pickle.UnpicklingError('Attempting to unpickle unsafe class %s' % name)
      return getattr(mod, name)

    @classmethod
    def loads(cls, pickle_string):
      pickle_obj = pickle.Unpickler(StringIO(pickle_string))
      pickle_obj.find_global = cls.find_class
      return pickle_obj.load()


should_not_change = False
def fff(b):
    global should_not_change
    should_not_change = b


class SadPanda(object):
    def __reduce__(self):
        return (fff, (True,))


class TestSafePickle(ShinkenTest):

    def setUp(self):
        #selfa.setup_with_file('etc/shinken_safe_pickle.cfg')
        pass


    def launch_safe_pickle(self, buf):
        SafeUnpickler.loads(buf)
        
        
    def test_safe_pickle(self):
        global should_not_change

        print "Creating payload"
        buf = pickle.dumps(SadPanda(), 0)
        should_not_change = False
        print "Payload", buf
        #self.assertEqual('HARD', host.state_type)
        print "Now loading payload"
        pickle.loads(buf)
        print should_not_change
        self.assertTrue(should_not_change)
        
        # reset and try our fix
        should_not_change = False
        #SafeUnpickler.loads(buf)
        def launch_safe_pickle():
            SafeUnpickler.loads(buf)
        self.assertRaises(pickle.UnpicklingError, launch_safe_pickle)
        print should_not_change
        self.assertFalse(should_not_change)

if __name__ == '__main__':
    unittest.main()