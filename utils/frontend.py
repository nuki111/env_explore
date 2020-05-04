
import ipywidgets as ipw
import traitlets as tra
import pandas as pd
import numpy as np
import re
import time
from IPython import get_ipython, display
from threading import Thread
from collections.abc import Iterable

def usename(obj: 'Any') -> str:
    '''
    usename(obj: Any) -> str
    
    Returns obj.__name__ if obj has an attribute '__name__',
    otherwise ``str(obj)`` is returned.
    
    Parameters:
    -----------
        obj (Any): Any object with an attribute '__name__'
            and/or with an '__str__' method. Cases in which
            the latter condition are not be met are rare.
    '''
    return obj.__name__ if hasattr(obj, '__name__') else str(obj)

def hboxes(widgets: 'Iterable[[ipw.Widget]]') -> 'tuple[HBox]':
    '''
    hboxes(widgets: Iterable[[ipw.Widgets]]) -> tuple(HBox)
    
    Returns a tuple of ipywidget HBoxes for each nested 
    Iterable in widgets with a child for each ipywidget
    in the Iterable.
    
    Parameters:
    -----------
        widgets (Iterable): 2 dimentional iterable of ipywidgets.
    '''
    return tuple([ipw.HBox(item) for item in widgets])

def vboxes(widgets: 'Iterable[[ipw.Widget]]') -> 'tuple[VBox]':
    '''
    vboxes(widgets: Iterable[[ipw.Widgets]]) -> tuple(HBox)
    
    Returns a tuple of ipywidget VBoxes for each nested 
    Iterable in widgets with a child for each ipywidget
    in the Iterable.
    
    Parameters:
    -----------
        widgets (Iterable): 2 dimentional nested iterable of ipywidgets.
    '''
    return tuple([ipw.VBox(item) for item in widgets])

def arrange(widgets: 'Iterable[Iterable[ipw.Widget]]', 
            column_wise: bool=False) -> ipw.Box:
    '''
    arrange(widgets: Iterable[Iterable[ipw.Widget]], columnwise: bool=False)
    
    Returns either an ipywidget HBox of VBoxes or vise versa from a 2 
    dimensional Iterable object.
    
    Parameters:
    -----------
        widgets (Iterable[Iterable[ipw.Widget]]): 2 dimentional Iterable object
            containing widgets.
        column_wise (bool): If True, a VBox of HBoxes will be returned instead
            of a HBox of VBoxes (default is False).
    '''
    inner_cls = ipw.VBox if column_wise else ipw.HBox
    outer_cls = ipw.HBox if column_wise else ipw.VBox
    
    return outer_cls(
        children=[inner_cls(inner) for inner in widgets]
    )

def inthread(func: callable) -> 'function':
    '''
    inthread(func: callable) -> function
    
    Used as a function decorator, the provided function is run within
    a new thread with the positional and key word arguments provided to
    the fuction.
    
    Paremeters:
    -----------
        func (callable): target of the thread.
    '''
    def wrapper(*args, **kwargs):
        Thread(target=func, args=args, kwargs=kwargs).start()
    return wrapper

def ishtml(string: str) -> bool:
    '''
    ishtml(string: str) -> bool
    
    Returns weather the given string matches the fromat of
    a standard HTML element, roughly '<...>...</...>'.
    
    Paremeters:
    -----------
        string (str): Any str.
    '''
    return bool(re.match('^<+(\S|\s)+>(\S|\s)+</+\S+>', string))
    
def showobj(obj: 'Any') -> None:
    '''
    showobj(obj: Any) -> None
    
    Displays the given object using the following conditions:
    
        - If the object is a string and matches the fromat of
          a standard HTML element, it is displayed as
          html code.
        - If the object is string but does not match the HTML 
          format, it is printed.
        - Otherwise the object is displayed as normal.
        
    Parmeters:
    ----------
        obj (Any): Any object.
    '''
    if isinstance(obj, str):
        if ishtml(obj):
            disp = HTMLCode(obj)
        else:
            disp = Printed(obj)
    else:
        disp = obj
        
    display.display(disp)

def runperiodic(func: callable, interval: float=5) -> None:
    '''
    runperiodic(func: callable, interval: float=5) -> None
    
    Decorator function for continuously running a function 
    periodically in its own thread.
    
    Parameters:
    -----------
        func (callable): Function to be decorated.
        interval (float): Number of seconds waiting between
            runs (defalult is 5).
    '''
    def wrapper(*args, **kwargs):
        def run(*args, **kwargs):
            while True:
                func(*args, **kwargs)
                time.sleep(interval)
        Thread(target=run, args=args, kwargs=kwargs).start()
    return wrapper

def runperiodicfactory(interval: float=5) -> None:
    '''
    runperiodicfactory(interval: float=5) -> None
    
    Factory function for ``runperiodic``.
    
    See ``runperiodic`` for more infomation.
    
    Parameters:
    -----------
        interval (float): Number of seconds waiting between
            runs (defalult is 5).
    '''
    def factory(func):
        return runperiodic(func, interval)
    return factory

# class AutoUpdater:
#     '''
#     AutoUpdater(update_method: str='update', interval: float=5)
    
#     Base class for objects that run a given inplace method
#     periodically with a given time interval.
    
#     Parameters:
#     -----------
#         update_method (str): Name of the method to be run
#             periodically (default is 'update').
#         interval (float): Number of seconds wait between runs
#             (default is 5).
#     '''
#     def __init__(self, 
#                  update_method: str='update',
#                  update_args: Iterable=[],
#                  update_kwargs: dict={},
#                  interval: float=5):
#         self.update_method = update_method
#         self.update_args = update_args
#         self.update_kwargs = update_kwargs
#         self.interval = interval
#         self.paused = False
#         self.setupdatewrapper()
#         self.globaliseupdatewrapper()
    
#     def getupdatewrapper(self) -> function:
#         return runperiodicfactory(self.interval)
    
#     def setupdatewrapper(self) -> None:
#         self.updatewrapper = self.getupdatewrapper()
        
#     def globaliseupdatewrapper(self) -> None:
#         global updatewrapper
#         updatewrapper = self.updatewrapper
    
#     @updatewrapper
#     def update__(self) -> None:
#         if not self.paused:
#             self.update_method
            
class Printed(str):
    '''
    Printed(a: str)
    
    Child of the str class for which the ``_ipython_display_``
    method is a wrapper for ``print``.
    
    Parameters:
    ----------
        a (str): Any str object.
    '''
    def __repr__(self):
        return str(self)

class HTMLCode(str):
    '''
    HTMLCode(a: str)
    
    Child of the str class for which the ``_ipython_display_`` 
    method uses the current Ipython instance's ``run_cell_magic``
    function with ``magic_name`` as 'html' and ``line`` as ''.
    
    Parameters:
    ----------
        a (str): Any str object.
    '''
    def _ipython_display_(self):
        get_ipython().run_cell_magic('html', '', self)

class LoadingButton(ipw.Button):
    '''
    LoadingButton(*args, **kwargs)
    
    Child of the ipw.Button class which displays a specified
    icon whilst it reacts to being clicked.
    
    Parmeters:
    ----------
        *args: Positional arguments passed to the ipw.Button
            constructor.
        **kwargs: Key word arguments passed to the ipw.Button
            constructor.
    '''
    loading_icon = 'truck-loading'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_traits(loading=tra.Bool())
        self.loading = False
        self.org_icon = self.icon
        self.observe(self.updateicon, names='loading')
        self.observe(self.updateorgicon, names='icon')
    
    def startloading(self, *args) -> None:
        '''
        self.startloading(*args) -> None
        
        Inplace method for setting button icon to
        ``self.loading_icon``.
        
        Parameters:
        -----------
            *args: Redundent positional arguments (required 
                to run on the click of a button).
        '''
        self.icon = self.loading_icon
        
    def stoploading(self, *args) -> None:
        '''
        self.startloading(*args) -> None
        
        Inplace method for setting button icon to 
        ``self.org_icon``.  By default, this is the icon with
        which the button was initialised.
        
        Parameters:
        -----------
            *args: Redundent positional arguments (required 
                to run on the click of a button).
        '''
        
        self.icon = self.org_icon
    
    def updateicon(self, change: tra.Bunch) -> None:
        '''
        self.updateicon(self, change: tra.Bunch) -> None
        
        Runs either ``self.startloading()`` or 
        ``self.stoploading()`` depending on the new value of the
        given traitlets Bunch.
        
        Parameters:
        -----------
            change (tra.Bool): Widget event.
        '''
        self.startloading() if change.new else self.stoploading()
    
    def _handle_button_msg(self, *args, **kwargs) -> None:
        '''
        self._handle_button_msg(*args, **kwargs) -> None
        
        Wrapper around ``super()._hanel_button_msg``. Sets the
        button icon to ``self.loading_icon`` until the parent
        function has finished running.
        
        See ``ipw.Button._handle_button_msg``, ``self.startloading``
        and ``self.stoploading`` for more infomation.
        
        Parameters:
        -----------
            *args: Positional arguments passed to
                ``super()._hanel_button_msg``.
            **kwargs: Key word arguments passed to
                ``super()._hanel_button_msg``
        '''
        self.startloading()
        super()._handle_button_msg(*args, **kwargs)
        self.stoploading()
    
    def updateorgicon(self, change: tra.Bunch):
        if change.new != self.loading_icon:
            self.org_icon = change.new
            
class ClearButton(LoadingButton):
    '''
    ClearButton(output: ipw.Output, **kwargs)
    
    Child of the LoadingButton class that clears a given ipw
    Output widget when clicked.
    
    Parameters:
    -----------
        out (ipw.Output): Output widget to be cleared when the
            ClearButton instance is clicked.
        **kwargs: Key word arguments used to initialise the parent.
    '''
    
    def __init__(self, output: ipw.Output, **kwargs):
        self.out = output
        
        kwargs['description'] = kwargs.setdefault('description', 'clear')
        kwargs['icon'] = kwargs.setdefault('icon', 'close')
#         kwargs['button_style'] = kwargs.setdefault('button_style', 'danger')
        
        super().__init__(**kwargs)
        
        self.on_click(self.click)
        
    def click(self, button: 'ClearButton') -> None:
        '''
        self.click(button: ClearButton)
        
        Clear Output widget, ``button.out``.
        
        Parameters:
            button (ClearButton): Should generally be self.
        '''
        button.out.clear_output()

class UpdateButton(LoadingButton):
    '''
    UpdateButton(**kwargs)
    
    Child of the LoadingButton class for updating objects.
    
    Parameters:
    -----------
        **kwargs: Key word arguments used to initialise the parent.
    '''
    
    def __init__(self, **kwargs):
        kwargs['description'] = kwargs.setdefault('description', 'update')
        kwargs['icon'] = kwargs.setdefault('icon', 'refresh')
#         kwargs['button_style'] = kwargs.setdefault('button_style', 'info')
        
        super().__init__(**kwargs)

class PausePlayButton(ipw.Button):
    '''
    PausePlayButton(start: bool=True, **kwargs)
    
    Child of the ipw.Button class which changes its icon from/to
    pause/play directly before ending its response to being clicked.
    
    Parmeters:
    ----------
        start (bool): Initalise with the pause icon.
        **kwargs: Key word arguments passed to the ipw.Button
            constructor.
    '''
    pause_icon = 'pause'
    play_icon = 'play'
    
    def __init__(self, start: bool=True, **kwargs):
        kwargs['icon'] = kwargs.setdefault(
            'icon', (self.pause_icon, self.play_icon)[start]
        )
        
        super().__init__(**kwargs)
        self.paused = not start
        
    def pause(self) -> None:
        '''
        self.pause() -> None
        
        Set 'icon' trait to ``self.pause_icon`` and 'paused' to 
        True.
        '''
        self.icon = self.pause_icon
        self.paused = True
        
    def play(self) -> None:
        '''
        self.play() -> None
        
        Set 'icon' trait to ``self.play_icon`` and 'paused' to 
        False.
        '''
        self.icon = self.play_icon
        self.paused = False
        
    def _handle_button_msg(self, *args, **kwargs) -> None:
        '''
        self._handle_button_msg(*args, **kwargs) -> None
        
        Wrapper around ``super()._hanel_button_msg``. Sets the
        button icon to either 'play' or 'pause' once the parent
        function has finished running.
        
        See ``ipw.Button._handle_button_msg``, ``self.play``
        and ``self.pause`` for more infomation.
        
        Parameters:
        -----------
            *args: Positional arguments passed to
                ``super()._hanel_button_msg``.
            **kwargs: Key word arguments passed to
                ``super()._hanel_button_msg``
        '''
        super()._handle_button_msg(*args, **kwargs)
        self.play() if self.paused else self.pause()
        
        
        
        
        