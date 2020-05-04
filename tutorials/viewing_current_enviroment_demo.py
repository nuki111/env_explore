
# coding: utf-8

# In[1]:


import sys
sys.path.insert(0, '..')


# ## Interfacing with the Running Enviroment
# #### By the end of this demo, you should be able to do the following:
# 1 - Expose variables in the current enviroment as a pandas DataFrame 
#     using the ``EnvHandeler`` class.
#         
# 2 - Expose variables in the current enviroment as an ipython widget 
#     using the ``WidgetEnv`` class.
#         
# 3 - Expose variables in the current enviroment as an ipython widget
#     which updates itself periodically using the ``AutoWidgetEnv`` 
#     class.
#         
# 4 - Use the common ``update`` method to update an instance of each 
#     of these classes when the enviroment changes.

# ### Import classes and functions
#  - ``getmain`` is a function wich returns an instance of the 
#     current enviroment (``__main__``)

# In[2]:


from env_explore import getmain, EnvHandeler, WidgetEnv, AutoWidgetEnv


# ### The current envirmoment can be specified with the 'name' argument
# The ``name`` argument is the name by which the object can be referenced (or generated) in the main enviroment.  Setting this to ``'getmain()'`` means that the EnvHandeler instance will be initialised and updated from the current enviroment.

# #### 1 - ``EnvHandeler``

# In[3]:


eh = EnvHandeler(
    name='getmain()'
)


# #### 2 - ``WidgetEnv``

# In[4]:


we = WidgetEnv(
    name='getmain()'
)


# #### 3 - ``AutoWidgetEnv``

# In[5]:


awe = AutoWidgetEnv(
    name='getmain()'
)


# In[6]:


display(
    eh,
    we,
    awe
)


# #### 4 - ``update``
# The ``update`` method is defined for each of the mentioned classes.  
# 
# It sets the backend value of the object to the result of evaluating the ``name`` attribute (``'getmain()'`` above) in the current enviroment and recaluclates other attributes accordingly.
# 
# For the ``AutoWidgetEnv`` class, this is done periodically in the backgroud and can also be done for both the ``WidgetEnv`` and ``AutoWidgetEnv`` classes manually by clicking the update button.
# 
# For the ``WidgetEnv`` and ``AutoWidgetEnv`` classes, changes should be reflected in the objects whilst they are being displayed.  
# 
# After running the following section, all the objects displayed above should have a row 'z' at the bottom.

# In[7]:


z = 5


# In[8]:


we.update() # Changes should be reflected in the display above
awe.update() # Changes should be reflected in the display above
eh.update()

