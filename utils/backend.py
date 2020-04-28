
import pandas as pd
import numpy as np
from IPython import get_ipython

from .frontend import Printed, HTMLCode

def getmain() -> 'module':
    '''
    getmain() -> module
    
    Returns the __main__ module.
    '''
    import __main__
    return __main__

def maineval(code: str) -> 'Any':
    '''
    maineval(code: str) -> Any
    
    Evaluates a string as code in the __main__ enviroment.
    and returns the result.
    
    Parameters:
    -----------
        code (str): String to be be evaluated.
    '''
    return eval(code, getmain().__dict__)
        
class EnvObj:
    '''
    EnvObj()
    
    Base class for objects that will not be used by envtodict.
    '''
    __envdontuse__ = True
    
class EnvDict(dict, EnvObj):
    '''
    EnvDict(a: dict)
    
    dict object that will not be used by ``envdict``
    
    Parameters:
    -----------
        a (dict): Any instance of a dict.
    '''
    pass

class EnvDf(pd.DataFrame, EnvObj):
    '''
    EnvDf(a: dict)
    
    Pandas DataFrame object that will not be used by ``envdict``.
    
    Parameters:
    -----------
        a (DataFrame): Any instance of a ``pd.DataFrame``.
    '''
    pass

def envtodict(env: 'Any') -> EnvDict:
    '''
    envtodict(env: Any) -> EnvDict
    
    Returns an ``EnvDict`` instance of the attribute names (keys)
    and corresponding values (values) from the given object.
    
    Note that attributes that meet one or more of the following
    conditions will NOT be included in the returned dictionary:
                    
        - Attribute is named 'In'.
        - Attribute is named 'Out'.
        - Name of the attribute starts with '_'.
        - Attribute is an instance of the EnvObj class.
        
    Parameters:
    -----------
        env (Any): Any python object.
        
    '''
    attrs = dir(env)
    attrs = [attr for attr in attrs if (attr not in ('In', 'Out')) and (not attr.startswith('_'))]
    envdict = {attr: getattr(env, attr) for attr in attrs}
    envdict = {attr: val for attr, val in zip(envdict.keys(), envdict.values()) if not isinstance(val, EnvObj)}
    envdict = envdict.copy()
    envdict = EnvDict(envdict)
    
    return envdict

def getattrsafe(*args, default: 'Any'=None, **kwargs):
    '''
    getattrsafe(obj: Any, key: str, defalut: Any=None)
    
    Wrapper around getattr which allows for a default value
    to be returned in the event that the given object does
    not contain an attribute with the given name.
    
    Parameters:
    -----------
        obj (Any): Object from which to retrive the attribute.
        key (str): Name of the attribute to retrive.
        default (Any): Value to be returned in the event that
            ``obj`` has not attribute named ``key`` (default is 
            None).
    '''
    try:
        return getattr(*args, **kwargs)
    except AttributeError:
        return default
    
def envtopandas(env: 'Any', 
                funcs: dict={'Type': type},
                attrs: dict={'Documentation': '__doc__'}
               ) -> EnvDf:
    '''
    envtopandas(env: Any, funcs: dict={'Type': type}, 
        attrs: dict={'Documentation': '__doc__'}) -> EnvDf
        
    Creates a pandas DataFrame (EnvDf) from a given object and adds
    columns extra infomation about the objects determined by the 
    ``funcs`` and ``attrs`` arguments passed.
    
    Note, if the given object is not an EnvDict, ``envtodict`` will
    be used to create and EnvDict from the given object which is then
    used to create the EnvDf.
    
    Parameters
    ----------
        env (Any): Object used as/to create the EnvDict.
        funcs (dict): Mapping of column names to functions 
            to be applied to the attribute values to create
            extra columns (default is ({'Type': type})).
            
            Note, the value 'Err' will be given to cells of
            these columns where applying the given function
            raises an exception.
            
        attrs (dict): Mapping of column names to attribute names
            of the attribute values used to create extra columns
            (default is {'Documentation': '__doc__'}).
            
            Note, ``getattrsafe(..., default='Err')`` is used to get 
            the attributes.
    '''
    envdict = env if isinstance(env, EnvDict) else envtodict(env)
    envtups = list(zip(envdict.keys(), envdict.values()))
    envtups = None if envtups == [] else envtups 
    envdf = pd.DataFrame(envtups, columns=['Variable', 'Value'])
    envdf.set_index('Variable', inplace=True)
    
    for col in funcs.keys():
        def func(*args, **kwargs):
            try:
                return funcs[col](*args, **kwargs)
            except:
                return 'Err'
            
        envdf[col] = envdf.Value.apply(func)
    
    for col in attrs.keys():
        envdf[col] = envdf.Value.apply(lambda x: getattrsafe(x, attrs[col], default=''))
    
    return EnvDf(envdf)

def envtohtmltable(env: 'Any', 
                   envtopandas_kwargs: dict={}, 
                   to_html_kwargs: dict={}) -> str:
    '''
    envtohtmltable(env: Any, envtopandas_kwargs: dict={}, 
        to_html_kwargs: dict={}) -> str
        
    Creates and returns an html table from an EnvDf instance using the
    ``pandas.DataFrame.to_html`` method.
    
    Note, if env is not an EnvDf, ``envtopandas(env, **envtopandas_kwargs)`` 
    will be used to create one.
    
    Parameters:
    -----------
        env (Any): Object used as/to create the EnvDf
        envtopandas_kwargs (dict): Dictionary of key word arguments to be
            passed to ``envtopandas`` to create the EnvDf. This argument is
            redundent if env is an EnvDf (default is {}).
        to_html_kwargs (dict): Dictionary of key word arguments to be passed
            to the ``pandas.DataFrame.to_html`` method to convert the EnvDf
            into HMTL code.
    '''
    envdf = env if isinstance(env, EnvDf) else envtopandas(env, **envtopandas_kwargs)
    envdf.apply(
        lambda x: x.str.replace('\n', '|-|<|-|br|-|>|-|') if x.dtype == str else x
    )
    envhtml = envdf.to_html(**to_html_kwargs)
    
    return envhtml.replace('|-|', '')

    