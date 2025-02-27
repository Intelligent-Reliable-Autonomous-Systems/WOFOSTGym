"""
Function dectorators for clarity in different simulation objects
    @prepare_states
    @prepare_rates

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""

from __future__ import print_function
from functools import wraps

class descript(object):
    def __init__(self, f, lockattr):
        self.f = f
        self.lockattr = lockattr
    
    def __get__(self, instance, klass):
        if instance is None:
            # Class method was requested
            return self.make_unbound(klass)
        return self.make_bound(instance)
    
    def make_unbound(self, klass):
        @wraps(self.f)
        def wrapper(*args, **kwargs):
            '''This documentation will vanish :)'''
            raise TypeError(
                'unbound method %s() must be called with %s instance '
                'as first argument (got nothing instead)'
                %
                (self.f.__name__, klass.__name__)
            )
        return wrapper
    
    def make_bound(self, instance):
        @wraps(self.f)
        def wrapper(*args, **kwargs):
            '''This documentation will disapear :)'''
            #print "Called the decorated method %r of %r with arguments %s "\
            #      %(self.f.__name__, instance, args)
            attr = getattr(instance, self.lockattr)
            if attr is not None:
                attr.unlock()
            ret = self.f(instance, *args, **kwargs)
            attr = getattr(instance, self.lockattr)
            if attr is not None:
                attr.lock()
            return ret
        # This instance does not need the descriptor anymore,
        # let it find the wrapper directly next time:
        setattr(instance, self.f.__name__, wrapper)
        return wrapper

def prepare_states(f):
    '''
    Class method decorator unlocking and locking the states object.

    It uses a descriptor to delay the definition of the 
    method wrapper. For more details:
    http://wiki.python.org/moin/PythonDecoratorLibrary#Class_method_decorator_using_instance
    '''

    return descript(f, "states")

def prepare_rates(f):
    '''
    Class method decorator unlocking and locking the rates object.

    It uses a descriptor to delay the definition of the 
    method wrapper. For more details:
    http://wiki.python.org/moin/PythonDecoratorLibrary#Class_method_decorator_using_instance
    '''

    return descript(f, "rates")
