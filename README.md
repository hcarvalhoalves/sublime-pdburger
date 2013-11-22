Description
-----------

This plugin allows you to set breakpoints for all open files with a
shortcut. It then automatically outputs commands for those breakpoints to your ~/.pdbrc

You can then start a pdb session with those breakpoints by running your Python script with:

`$ python -m pdb foo.py`

Default shortcuts
-----------------

- `Ctrl + B`: Toggle breakpoint at current line

- `Ctrl + Shift + B`: Reset all breakpoints

You will see a confirmation on the status bar if any breakpoints get added.

To-do
----

- Allow symbol-based breakpoints (as opposed to linenumber)
- Allow conditional breakpoints

Credits
-------

Henrique Carvalho Alves <hcarvalhoalves@gmail.com>
