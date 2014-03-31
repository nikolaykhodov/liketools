# -*- coding: utf8 -*-
""" Декораторы """

from django.http import HttpResponse
import json

def json_answer(func):
    """ Декоратор для возврата HttpResponse по JSON-ответу """
    def wrapper(*args, **kwargs):
        return HttpResponse(json.dumps(func(*args, **kwargs)))

    return wrapper

from django.db.models.sql import compiler
import re
def log_sql_queries_def_handler(queries, func_name, exception):
    """
    Prints somethinng:
    some_sql_func: SELECT * FROM auth_user WHERE id= ...
    
    """
    if func_name.find('test_') >= 0 or func_name.find('setUp') >= 0:
        for q in queries:
            print '\n', func_name, ':'
            if type(q) == tuple:
                print '    ', q[0] % q[1]
            elif type(q) == list:
                print '    ', q[0][0] % tuple(q[0][1])
 
class QueryAccumulator(object):
    """
    SQL query logger by intercepting django.db.models.sql.compiler.SQLCompiler.as_sql().
    
    This class is intended to log all queries.
    
    In order to log all queries made by some function, you should write something:
    ...
    accumulator = QueryAccumulator(False, cb=my_callback)
    accumulator.enable()
    try:
      some_sql_method(...)
      accumulator.disable('some_sql_method')
    except Exception, ex:
      accumulator.disable('some_sql_method', ex)
      raise
    """
 
    def __init__(self, mode, cb, only_except):
        """ """
 
        self.mode = mode
        self.cb = cb
        self.only_except = only_except
 
        self.queries = []
        self.enabled = False
 
        # Save original method
        get_attribute = compiler.SQLCompiler.__getattribute__
        
        # this
        accumulator = self
 
        def log_wrapper(self, name):
            """ Wrapper for hooking as_sql() """
 
            attr = get_attribute(self, name)
 
            if name == 'as_sql':
                def new_as_sql(*args, **kwargs):
                    query = attr(*args, **kwargs)
                    if accumulator.enabled is True:
                        accumulator.queries.append(query)
                    return query
                return new_as_sql
            else:
                return attr
 
        # Hook
        compiler.SQLCompiler.__getattribute__ = log_wrapper
 
    def enable(self, func_name):
        """ Enable logging """
 
        # Add some element to array: flag of enabling is len > 0
        self.enabled = True
 
        # Empty query log
        self.queries = []

        # Save callee
        self.func_name = func_name
 
    def disable(self, exception=None):
        """ Disable logging: restore original method """
 
        # Clear enabled array
        self.enabled = False
 
        # If there are no errors
        if self.only_except is True and exception is None:
            return
 
        # Process query log
        self.cb(self.queries, self.func_name, exception)
 
class log_sql_queries(object):
    """
    Decorator to catch all SQL queries for Django apps.
 
    This decorator can be applied either for classes or basic methods.
 
    Paramaters:
        -- mode:
            -- immediately - callback will be called just after SQL request
            -- post - callback will be called after termination of the method decorated
        -- only_except - callback will be triggered only if the decorated method raises exception
        -- callback - method to process query log:
            -- queries - [tuple(prepared statement, params), ...]
            -- func_name - name of function where SQL query was requested
            -- exception - error instance
    """
 
    def __init__(self, mode='immediately', only_except=False, callback=log_sql_queries_def_handler):
 
        self.only_except = only_except
        self.callback = callback
        self.mode = mode
 
    def __call__(self, obj):
        """
        Parameters:
            -- obj - class (all class methods will be intercepted) or method to be intercepted
        """
 
        # Params
        only_except = self.only_except
        callback = self.callback
        mode = self.mode
 
        def method_wrapper(*args, **kwargs):
            """ Wrapper for basic methods """
            accumulator = QueryAccumulator(mode, callback, only_except)
            accumulator.enable(obj.__name__)
 
            try:
                result = obj(*args, **kwargs)
                accumulator.disable()
            except Exception, ex:
                accumulator.disable(ex)
                raise
 
            return result
 
        def class_wrapper(kls):
            """ Wrapper for classes """
 
            # Save old __getattribute__()
            old_getattribute = kls.__getattribute__
            
            # Override
            def getattribute(self, name):
                """ Return wrapped version of class method otherwise attribute itself """
 
                attr = old_getattribute(self, name)
 
                # Is callabble
                if hasattr(attr, '__call__'):
 
                    # Get func name
                    func_name = ''
                    if hasattr(attr, 'im_class'):
                        func_name = re.findall(r'\'(.*?)\'', str(attr.im_class))[0] + '.' + attr.__name__
 
                    # Wrapped func
                    def newfunc(*args, **kwargs):
                        accumulator = QueryAccumulator(mode, callback, only_except)
                        accumulator.enable(func_name)
                        try:
                            result = attr(*args, **kwargs)
                            accumulator.disable()
                        except Exception, ex:
                            accumulator.disable(ex)
                            raise
                            
                        return result
 
                    # Return wrapped func
                    return newfunc
                else:
                    return attr
 
            # Hook
            kls.__getattribute__ = getattribute
 
            return kls
 
        # Choose the proper wrapper
        import inspect
        if inspect.isclass(obj):
            return class_wrapper(obj)
        else:
            return method_wrapper
