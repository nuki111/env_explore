
import pandas as pd
import numpy as np
from collections.abc import Iterable
from IPython.display import display

try:
    from utils import backend as utils
except ImportError:
    from .utils import backend as utils

class EnvHandeler(utils.EnvObj):
    '''
    EnvHandeler(name:str, display_as:str='df', **kwargs[dict_args: Iterable=[], 
        dict_kwargs: dict={}, df_args: Iterable=[], df_kwargs: dict={}, 
        html_args: Iterable=[], html_kwargs: dict={}])
    
    For processing and displaying the contents objects.
    
    Parameters:
    -----------
        name (str): Name by which the object can be referenced in the main 
            enviroment.
        display_as (str): Name of the attribute to be displayed by the
            ``_ipython_display_`` method (default = 'df').
        **kwargs: Key word defaluts used by ``self.updatefromenv``
            and other methods to update ``self.dicti``, ``self.df`` and
            ``self.html``.
                - dict_args (Iterable): Positional arguments for 
                    ``self.setdict`` (default = []).
                - dict_kwargs (dict): Key word arguments for ``self.setdict`` 
                    (default = {}).
                - df_args (Iterable): Positional arguments for ``self.setdf`` 
                    (default = []).
                - df_kwargs (dict): Key word arguments for ``self.setdf`` 
                    (default = {}).
                - html_args (Iterable): Positional arguments for 
                    ``self.sethtml`` (default = []).
                - html_kwargs (dict): Key word arguments for ``self.sethtml`` 
                    (default = {}).        
    '''
    
    def __init__(self,
                 name: str,
                 display_as: str='df',
                 **kwargs):
        super().__init__()
        self.setname(name)
        self.setenv()
        self.display_as = display_as
        self.update_params = kwargs
        self.updatefromenv(**self.update_params)
    
    @property
    def displayer_(self) -> 'Any':
        '''
        Attribute to be displayed by ``_ipython_display_`` method.
        '''
        return getattr(self, self.display_as)
    
    @property
    def loc(self) -> pd.core.indexing._LocIndexer:
        '''
        self.df.loc
        '''
        return self.df.loc
    
    @property
    def iloc(self) -> pd.core.indexing._iLocIndexer:
        '''
        self.df.iloc
        '''
        return self.df.iloc
    
    def __str__(self):
        return utils.Printed(str(self.displayer_))
    
    def _ipython_display_(self):
        display(self.displayer_)
    
    def __iter__(self):
        for i in self.df.index:
            yield i
        
    def getenv(self) -> 'Any':
        '''
        self.getenv() -> 'Any'
        
        Evaluates ``self.name`` in the __main__ enviroment and returns
        the result.
        '''
        return utils.maineval(self.name)
    
    def getdict(self, *args, **kwargs) -> utils.EnvDict:
        '''
        self.getdict() -> utils.EnvDict
        
        Uses ``utils.envtodict`` to return a dictionary of all required
        attributes of ``self.env``
        '''
        return utils.envtodict(self.env, *args, **kwargs)
    
    def getdf(self, *args, **kwargs) -> utils.EnvDf:
        '''
        self.getdf(*args, **kwargs[funcs: dict={'Type': type}, 
            attrs: dict={'Documentation': '__doc__'}]) -> utils.EnvDf
        
        Uses ``utils.envtodict`` to create a data frame from ``self.dicti``
        and adds extra infomation about the objects determined by the 
        ``funcs`` and ``attrs`` arguments passed.
        
        See ``utils.envtopandas`` for more information.
        
        Parameters:
        -----------
            *args: Positional argumentents passed to ``utils.envtopandas``
                (after the first 'env' argument as this is fixed at 
                ``self.dicti``).
            **kwargs: Key word arguments passed to ``utils.envtopandas``.
        '''
        return utils.envtopandas(self.dicti, *args, **kwargs)
    
    def gethtml(self, *args, **kwargs) -> str:
        '''
        self.gethtml(*args, **kwargs) -> str
        
        Uses ``utils.envtohtmltable`` to create and return a HTML table
        from self.df.
        
        See ``utils.envtohtmltable`` for more infomation.
        
        Parameters:
        -----------
            *args: Positional argumentents passed to ``utils.envtohtmltable``
                (after the first 'env' argument as this is fixed at 
                ``self.df``).
            **kwargs: Key word arguments passed to ``utils.envtohtmltable``.  
        '''
        return utils.envtohtmltable(self.df, *args, **kwargs)
    
    def setname(self, name: str) -> None:
        '''
        self.setname(name: str) -> None
        
        Inplace method for setting the name attribute.
        
        Parameters:
        -----------
            name (str): Name of the desired object in the __main__
                enviroment.
        '''
        self.name = str(name)
    
    def setenv(self) -> None:
        '''
        self.setenv() -> None
        
        Inplace method for setting the env attribute.
        
        See ``self.getenv`` for more infomation.
        '''
        self.env = self.getenv()
        
    def setdict(self, *args, **kwargs) -> None:
        '''
        self.setdict() -> None
        
        Inplace method for setting the dicti attribute.
        
        See ``self.getdict`` for more infomation.
        '''
        self.dicti = self.getdict(*args, **kwargs)
        
    def setdf(self, *args, **kwargs) -> None:
        '''
        self.setdf(*args, **kwargs) -> None
        
        Inplace method for setting the df attribute.
        
        See ``self.getdf`` for more infomation.
        
        Parameters:
        -----------
            *args: Positional argumentents passed to ``self.getdf``.
            **kwargs: Key word arguments passed to ``self.getdf``.
        '''
        self.df = self.getdf(*args, **kwargs)
        
    def sethtml(self, *args, **kwargs) -> None:
        '''
        self.sethtml(*args, **kwargs) -> None
        
        Inplace method for setting the html attribute.  ``self.html`` Is set
        as an instance of the ``utils.HTMLCode`` class, initialised with the 
        string generated by ``self.gethtml``.
        
        See ``self.gethtml`` and ``utils.HTMLCode`` for more infomation.
        
        Parameters:
        -----------
            *args: Positional argumentents passed to ``self.gethtml``.
            **kwargs: Key word arguments passed to ``self.gethtmls``.
        '''
        self.html = utils.HTMLCode(self.gethtml(*args, **kwargs))
    
    def updatefromname(self, name: str=None) -> 'EnvHandeler':
        '''
        self.updatefromname(name: str=None) -> EnvHandeler
        
        If passed a non-null value, the 'name' attribute is updated using the 
        string.  The EnvHandeler then updates the 'env' attribute.
        
        See ``self.setname`` and ``self.setenv`` for more infomation.
        
        Parameters
        ----------
            name (str): String passed to ``self.setname``.  If None,
                ``self.setname`` will not be called. (default is None).
        '''
        self.setname(name) if name is not None else None
        self.setenv()
        
        return self
    
    def updatefromenv(self,
               dict_args: Iterable=[],
               dict_kwargs: dict={},
               df_args: Iterable=[],
               df_kwargs: dict={},
               html_args: Iterable=[],
               html_kwargs: dict={}) -> 'EnvHandeler':
        '''
        self.updatefromenv(dict_args: Iterable=[], dict_kwargs: dict={},
               df_args: Iterable=[], df_kwargs: dict={}, html_args: Iterable=[],
               html_kwargs: dict={}) -> 'EnvHandeler'
        
        Updates the 'dict', 'df' and 'html' attributes. And returns the EnvHandeler
        in its resultant state.
        
        Note, ``self.updatefromname`` should generally be called as a prerequisit
        to this method as this method updates based of the current 'env' 
        attribute.
        
        See ``self.setdict``, ``self.setdf`` and ``self.sethtml`` for more
        infomation.
        
        Parameters:
        -----------
            dict_args (Iterable): Positional arguments passed to 
                ``self.setdict``.
            dict_kwargs (dict): Key word arguments passed to 
                ``self.setdict``.
            df_args (Iterable): Positional arguments passed to 
                ``self.setdf``.
            df_kwargs (dict): Key word arguments passed to 
                ``self.setdf``.
            html_args (Iterable): Positional arguments passed to 
                ``self.sethtml``.
            html_kwargs (dict): Key word arguments passed to 
                ``self.sethtml``.
        '''
        self.setdict(*dict_args, **dict_kwargs)
        self.setdf(*df_args, **df_kwargs)
        self.sethtml(*html_args, **html_kwargs)
        
        return self
        
    def update(self, name: str=None, **kwargs) -> 'EnvHandeler':
        '''
        self.update(name: str=None, **kwargs) -> 'EnvHandeler'
        
        Updates the EnvHandeler from the name passed and returns it in its 
        resultant state.
        
        See ``self.updatefromname`` and ``self.updatefromenv`` for more
        infomation.
        
        Parameters:
        -----------
            name (str): 'name' argument passed to ``self.updatefromname``
                (default is None).
            **kwargs: Key word arguments passed to ``self.updatefromenv``.
                If no key word arguments (other then 'name') are passed,
                the value of the 'update_params' attribute is used instead.
        '''
        self.updatefromname(name)
        kwargs = self.update_params if kwargs == {} else kwargs
        self.updatefromenv(**kwargs)
        
        return self
    
    def subenv(self, var: 'str|Iterable[str]', **kwargs) -> 'EnvHandeler':
        '''
        self.subenv(var: str|Iterable[str], **kwargs) -> EnvHandeler
        
        Creates and returns an EnvHandeler for a given attribute or
        chain of attributes of the 'env' attribute.
        
        See ``EnvHandeler`` for more information.
        
        Parameters:
        -----------
            var (str|Iterable[str]): name of the attribute of the current
                'env' attribute with with to create a new Envhandeler.
                
                Note, if var is a non-str Iterable, this method will 
                recursivly call itself on the result of each previous 
                item in var.
                
            **kwargs: Key word arguments passed to ``EnvHandeler.__init__``.
                If no key word arguments are passed (except for 'name' and 
                'display_as'), the value of the 'update_params' attribute is 
                used instead.
        '''
        kwargs = self.update_params if kwargs == {} else kwargs
        
        if isinstance(var, str):
            env = self.__class__(
                name=f'{self.name}.{var}', 
                display_as=self.display_as,
                **kwargs,
            )
        else:
            env = self
            name = '.'.join(var)
            env = self.subenv(name, **kwargs)
#             for x in var:
#                 env = env.subenv(x, **kwargs)
                
        return env

EnvHandler = EnvHandeler