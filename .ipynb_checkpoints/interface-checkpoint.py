import re
import inspect
import time
import pandas as pd
import numpy as np
import ipywidgets as ipw
import traitlets as tra
from multiprocessing import Process
from datetime import datetime
from IPython import display
from collections.abc import Iterator

try:
    from utils import frontend as utils
    from processing import EnvHandeler
except ImportError:
    from .utils import frontend as utils
    from .processing import EnvHandeler

class WidgetCell(ipw.Button):
    '''
    WidgetCell(use_iloc: bool=False, index: Any, column: Any,
        owner: pd.DataFrame, out: ipw.Output=ipw.Output())
    
    Child of ipywidgets' Button class for representing a cell of
    a data frame by the WidgetDf class.
    
    See ``ipywidgets.Button`` and ``WidgetDf`` for more infomation.
    
    Parameters:
    -----------
        use_iloc (bool): Weather or not the iloc should be used to
            locate the cell value in the passed DataFrame ('owner' 
            argument) instead of the loc (default is False).
        index (Any): Index of the desired cell.
        column (Any): Column of the desired cell.
        owner (pd.DataFrame): DataFrame from which to locate the cell's
            value.
        out (ipw.Output): Ipywidgets' Output widget in which the cell's
            value will be displayed upon being clicked (default is 
            ``ipw.Output()``).
    '''
    
    def __init__(self,
                 use_iloc: bool=False,
                 index: 'Any'=None,
                 column: 'Any'=None,
                 owner: pd.DataFrame=None,
                 out: ipw.Output=ipw.Output(),
                 **kwargs):
        super().__init__(**kwargs)
        
        self.use_iloc = use_iloc
        self.owner = owner
        self.out = out
        
        self.add_traits(
            value=tra.Any(), 
            index=tra.Any(),
            column=tra.Any(),
        )
        
        self.index = index
        self.column = column
        
        self.observe(self.update, names=[
            'column', 'index',
        ])
        
        self.on_click(self.click)
        self.update(self.getvalue())
        
    @property
    def fromowner_(self) -> bool:
        return self.use_loc or self.use_iloc
    
    @property
    def loc_(self) -> 'pd.core.indexing._LocIndexer|pd.core.indexing._iLocIndexer':
        '''
        self.owner.iloc if self.use_iloc else self.owner.loc
        '''
        return self.owner.iloc if self.use_iloc else self.owner.loc
    
    def getvalue(self, value: 'Any'=None) -> 'Any':
        '''
        self.getvalue(value: Any=None) -> Any
        
        If the value passed is None, the value of the cell in ``self.owner``
        with the index ``self.index`` and column ``self.column``.  Otherwise 
        the given value is returned.
        
        Parameters:
        -----------
            value (Any): Either None or the value to be returned (default is
                None).
        '''
        value = self.value if value is None else value
        return self.loc_[self.index, self.column]
        
    def setvalue(self, *args, **kwargs) -> None:
        '''
        self.setvalue(*args, **kwargs) -> None
        
        Inplace method for setting the 'value' trait using ``self.getvalue``.
        
        See ``self.getvalue`` for more infomation.
        
        Parameters:
        -----------
            *args: Positional arguments passed to ``self.getvalue``.
            **kwargs: Key Word arguments passed to ``self.getvalue``.
        '''
        self.value = self.getvalue(*args, **kwargs)
    
    def update(self, value: 'Any'=None) -> None:
        '''
        self.update(value: Any=None) -> Any
        
        Updates the 'value', 'description' and 'tooltip' traits.
        
        See ``self.setvalue`` and ``self.setdesc`` for more infomation.
        
        Parameters:
        -----------
            value (Any): value argument passed to ``self.setvalue`` (default is
                None).
        '''
        self.setvalue(value)
        self.setdesc()
        
    def getdesc(self) -> str:
        '''
        self.getdesc() -> str
        
        Returns the appropriate description and tooltip.
        
        See ``utils.usename`` for more infomation.
        '''
        return utils.usename(self.value)
    
    def setdesc(self) -> None:
        '''
        self.setdesc() -> None
        
        Inplace method for setting the 'description' and 'tooltip' traits.
        
        See ``self.getdesc`` for more infomation.
        '''
        self.description = self.tooltip = self.getdesc()
        
    def click(self, button: 'WidgetCell') -> None:
        '''
        self.click(button: WidgetCell) -> None
        
        For adding to the buttons on_click functions.  It displays the value of 
        the cell using ``utils.showobj`` in the 'out' attribute.
        
        See ``utils.showobj`` for more infomation.
        
        Parameters:
        -----------
            button (WidgetCell): Should generally be self.
        '''
        head = f'{button.index} - {button.column}'
        
        with self.out:
            print('\n'+inspect.cleandoc(f'''
            {head}
            {"="*len(head)}
            '''))
            utils.showobj(button.value)

class WidgetDf(ipw.VBox):
    '''
    WidgetDf(data: pd.DataFrame, out: ipw.Output, **kwargs)
    
    Widget for representing pandas Data Frames.  It inherits from 
    ipywidgets' VBox class.  Each cell is represented by a WidgetCell
    object.
    
    See ``ipywidgets.VBox`` and ``WidgetCell`` for more infomation.
    
    Parameters:
    -----------
        data (pd.DataFrame): Any pandas DataFrame, used as the 'owner'
            attribute of each cell.
        out (ipw.Output): Any ipw.Output object, used as the 'out' 
            attribute of each cell (default is ``ipw.Output()``).
        **kwargs: Key word arguments used to initalise the parent
            (ipw.VBox).
    '''
    cell_layout = ipw.Layout(width='150px')
    index_layout = ipw.Layout(width='100px')
    column_layout = ipw.Layout(width=cell_layout.width)
    
    def __init__(self, 
                 data: pd.DataFrame, 
                 out: ipw.Output=ipw.Output(),
                 **kwargs):
        super().__init__(**kwargs)
        self.add_traits(data=tra.Any())
        self.data = data
        self.out = out
        self.clear_button = utils.ClearButton(self.out)
        self.setbuttonbox()
        self.setchildren()
        self.observe(self.setchildren, names='data')
        
    @property
    def loc_(self) -> pd.core.indexing._LocIndexer:
        '''
        self.data.loc
        '''
        return self.data.loc
    
    @property
    def iloc_(self) -> pd.core.indexing._iLocIndexer:
        '''
        self.data.iloc
        '''
        return self.data.iloc
    
    def _ipython_display_(self) -> None:
        display.display(super(), self.button_box, self.out)
        
    def getbuttonbox(self) -> ipw.HBox:
        '''
        self.getbuttonbox() -> ipw.HBox
        
        Returns an ipywidgets HBox containing the 'clear_button'.
        '''
        return ipw.HBox((self.clear_button,))
    
    def setbuttonbox(self) -> None:
        '''
        self.setbuttonbox() -> None
        
        Inplace method for setting the 'button_box' attribute using
        ``self.getbuttonbox``.
        
        See ``self.getbuttonbox`` for more infomation.
        '''
        self.button_box = self.getbuttonbox()
        
    def getcell(self, index: 'Any', column: 'Any') -> WidgetCell:
        '''
        self.getcell(index: Any, column: Any) -> WidgetCell
        
        Returns a WidgetCell object representing the cell in ``self.data`` at
        the given column and index.
        
        See ``WidgetCell`` for more infomation.
        
        Parameters:
        -----------
            index (Any): Index of the cell in self.data.
            column (Any): Column of the cell in self.data.
        '''
        return WidgetCell(
            use_iloc=False,
            owner=self.data,
            index=index,
            column=column,
            out=self.out,
            layout=self.__class__.cell_layout
        )
    
    def getindex(self, index: 'Any') -> ipw.Label:
        '''
        self.getindex(index: Any) -> ipw.Label
        
        Returns a Label widget which has a value equal to the string
        representation of the passed index.  This is used to represent an
        individual item in ``self.data.index``.
        
        Parameters:
        -----------
            index (Any): Item of an index.
        '''
        return ipw.Label(str(index), layout=self.__class__.index_layout)
    
    def getcolumn(self, column: 'Any') -> ipw.Label:
        '''
        self.getindex(column: Any) -> ipw.Label
        
        Returns a Label widget which has a value equal to the string
        representation of the passed column.  This is used to represent an
        individual item in ``self.data.columns``.
        
        Parameters:
        -----------
            column (Any): Column name.
        '''
        return ipw.Label(str(column), layout=self.__class__.column_layout)
    
    def getrow(self, index: 'Any') -> tuple:
        '''
        self.getrow(index: Any) -> tuple
        
        Returns the appropriate tuple of widgets to represent the row in
        ``self.data`` at the given index.
        
        See ``self.getindex`` and ``self.getcell`` for more infomation.
        
        Parameters:
        ----------
            index (Any): Item in ``self.data.index``.
        '''
        return (self.getindex(index), *tuple(pd.Series(self.data.columns).apply(
            lambda col: self.getcell(index, col)
        ).values))
    
    def getrows(self) -> tuple:
        '''
        self.getrows() -> tuple
        
        Returns a tuple of tuples, with each inner tuple being generated by
        ``self.getrow`` for a given index.
        
        See ``self.getrow`` for more infomation.
        '''
        return tuple(pd.Series(self.data.index).apply(
            lambda i: self.getrow(i)
        ).values)
    
    def getchildren(self) -> tuple:
        '''
        self.getchildren() -> tuple
        
        Returns a tuple appropriate for use as the 'child' trait.
        
        See ``self.getcolumns`` and ``self.getrows`` for more infomation.
        '''
        return (self.getcolumns(), *utils.hboxes(self.getrows()))
    
    def getcolumns(self) -> ipw.HBox:
        '''
        self.getcolumns() -> ipw.HBox
        
        Returns an ipywidgets HBox of Label widgets representing the column
        names of ``self.data``.
        
        Note, the 0th child of returned HBox represents the index name. If the
        index is unnamed, the value of the 0th child is blank.
        '''
        inam = self.data.index.name
        return ipw.HBox(
            [self.getcolumn('') if inam is None else self.getcolumn(inam)] +
            [self.getcolumn(col) for col in self.data.columns]
        )
    
    def setchildren(self, *args) -> None:
        '''
        self.setchildren() -> None
        
        Inplace method for setting the 'child' trait.
        
        See self.getchildren for more infomation.s
        '''
        self.children = self.getchildren()
        
    def itercells(self) -> Iterator:
        '''
        itercells(self) -> Iterator
        
        Yields each cell by row then column.
        '''
        for row in self.children[1:]:
            for cell in row.children[1:]:
                yield cell
                
    def changeout(self, out: ipw.Output) -> None:
        '''
        self.changeout(out: ipw.Ouput) -> None
        
        Inplace method for safly changing the 'out' attribute.
        
        Parameters:
        -----------
            out (ipw.Output): New Output widget in which to display cell values
                when clicked.
        '''
        self.out = out
        self.clear_button.out = out
        for cell in self.itercells():
            cell.out = self.out 

class WidgetEnv(WidgetDf, EnvHandeler):
    '''
    WidgetEnv(*args, **kwargs)
    
    Widget for representing the EnvHandeler objects. It inherits from
    the WidgetDf and EnvHandeler classes.
    
    See ``WidgetDf`` and ``EnvHandeler`` for more infomation.
    
    Parameters:
    -----------
        *args: Positional arguments used to initialise the EnvHandeler
            parent.
        **kwargs: Key word arguments used to initialise the EnvHandeler
            parent.
    '''
    
    def __init__(self, *args, **kwargs):
        EnvHandeler.__init__(self, *args, **kwargs)
        WidgetDf.__init__(self, self.df)
        self.add_traits(last_updated=tra.Any())
        self.last_updated = None
        self.setupdatebutton()
    
    @utils.inthread
    def update(self, *args, **kwargs) -> None:
        '''
        self.update(self, *args, **kwargs) -> None
        
        Wrapper around the 'update' method of the EnvHandeler parent in which
        ``self.data`` is ``set.df`` after the parent's update method is called.
        Finally, it updates the 'last_updated' attribute using ``datetime.now``.
        
        Note, this function is decorated with ``utils.inthread``, hence will
        run in its own thread. 
        
        See ``EnvHandeler.update``, ``utils.inthread`` and ``datetime.now`` for 
        more infomation.
        
        Parameters:
        -----------
            *args: Positional arguments passed to the parents update method.
            **kwargs: Key word arguments passed to the parents update method.
        '''
        super().update(*args, **kwargs)
        self.data = self.df
        self.last_updated = datetime.now()
        
    def getupdatebutton(self, *args, **kwargs) -> utils.UpdateButton:
        '''
        self.getupdatebutton(*args, **kwargs) -> utils.UpdateButton
        
        Returns an instance of the ``utils.UpdateButton`` class which calls the
        'update' method upon being clicked.
        
        See ``self.update`` and ``utils.UpdateButton`` for more infomation.
        
        Parameters:
        -----------
            *args: Positional arguments passed to the update method upon the 
                returned button being clicked.
            **kwargs: Key word arguments passed to the update method upon the
                returned button being clicked.
        '''
        button = utils.UpdateButton()
        button.on_click(lambda button: self.update(*args, **kwargs))
        
        return button
    
    def setupdatebutton(self, *args, **kwargs) -> None:
        '''
        self.setbutton(*args, **kwargs) -> None:
        
        Inplace method for creating the 'update_button' and adding it to the
        children of the 'button_box' attribute.
        
        See ``self.getupdatebutton`` for more infomation.
        
        Parameters:
        -----------
            *args: Positional arguments passed to ``self.getupdatebutton``.
            **kwargs: Key word arguments passed to ``self.getupdatebutton``.            
        '''
        self.update_button = self.getupdatebutton(*args, *kwargs)
        self.button_box.children += (self.update_button,)
    
    def subenv(self, *args, new_output: bool=True, **kwargs) -> 'WidgetEnv':
        '''
        self.subenv(*args, new_output: bool=True, **kwargs) -> WidgetEnv
        
        Wrapper around the 'subenv' method of the EnvHandeler parent in which
        the resulting WidgetEnv is given a new Output widget as its 'out'
        attribute.
        
        See ``EnvHandeler.subenv``, and ``self.changeout`` for more infomation.
        
        Parameters:
        -----------
            *args: Positional arguments passed to ``super().subenv``.
            new_output (bool): Weather or not the returned WidgetEnv should
                have its own, new, output.
                
                Note, if False, output from both self and the returned
                WidgetEnv will share an output.
                
            **kwargs: Key word arguments passed to ``super().subenv``.
        '''
        env = super().subenv(*args, **kwargs)
        env.changeout(ipw.Output()) if new_output else None
        
        return env

class AutoWidgetEnv(WidgetEnv):
    '''
    AutoWidgetEnv(*args, interval: float=5, start: bool=True, **kwargs)
    
    Child class of ``WidgetEnv``.  Is able to automatically update itself
    periodically in the background.
    
    See ``WidgetEnv`` for more infomation.
    
    Parameters:
    -----------
        *args: Positional arguments passed to the parent's constructor.
        interval (float): Number of seconds between updates (default is 5).
        start (bool): Weather to start automatic updates on initialisation.
            ``self.start`` can be used to commence automatic updating after
             the fact (default is True).
        **kwargs: Key word arguments passed to the parent's constructor.
    '''
    
    def __init__(self, 
                 *args, 
                 interval: float=5, 
                 start:bool=True, 
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.interval = interval
        self.paused = False
        self.setpausebutton()
        self.start() if start else None
    
    def update(self, *args, **kwargs) -> None:
        '''
        self.update(*args, **kwargs) -> None
        
        Wrapper around the 'update' method of the parent which only calls the
        method if ``self.paused`` is False.
        
        See ``WidgetEnv.update`` for more infomation.
        
        Parameters:
        -----------
            *args: Positional arguments passed to ``super().update``.
            **kwargs: Key word arguments passed to ``super().update``.
        '''
        if not self.paused:
            super().update(*args, **kwargs)
        
    def start(self, *args, **kwargs) -> None:
        '''
        self.start(*args, **kwargs) -> None:
        
        Commences automatic updating.
        
        See See ``WidgetEnv.update`` and ``utils.runperiodic`` for more
        infomation.
        
        Parameters:
        -----------
            *args: Positional arguments passed to ``super().update``.
            **kwargs: Key word arguments passed to ``super().update``.
        '''
        utils.runperiodic(
            func=self.update,
            interval=self.interval
        )(*args, **kwargs)

    def stop(self):
        self.update_process.terminate()
        self.setupdateprocess()
    
    def getpausebutton(self, **kwargs) -> utils.PausePlayButton:
        pause_button = utils.PausePlayButton(self.paused, **kwargs)
        
        pause_button.on_click(
            lambda button: setattr(self, 'paused', button.paused)
        )
        
        return pause_button
    
    def setpausebutton(self, **kwargs) -> None:
        self.pause_button = self.getpausebutton(**kwargs)
        self.button_box.children += (self.pause_button,)