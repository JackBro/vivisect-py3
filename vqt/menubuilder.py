from PyQt5 import QtCore, QtWidgets, QtGui


class FieldAdder:
    def __init__(self, splitchar='.'):
        self.kids = {}
        self.splitchar = splitchar
        self._dyn_callback = None

    def _addMenuFields(self, plist):
        parent = self
        kid = self
        for p in plist:
            kid = parent.kids.get(p)
            if kid is None:
                kid = VQMenu(p, parent=parent, splitchar=self.splitchar)
                action = parent.addMenu(kid)
                parent.kids[p] = kid
            parent = kid

        return kid

    def _addDynActions(self):
        self.clear()
        for name in self._dyn_callback():
            act = QtWidgets.QAction(name, self)
            cb = ActionCall(self._dyn_callback, name)
            act.triggered.connect(cb)
            self.addAction(act)

    def addDynMenu(self, pathstr, callback):
        """
        Add a dynamic menu item which will populate on-hover by asking
        the specified callback for a list of actions.

        Example:
            def callback(name=None):

                if name == None:
                    return ('one', 'two', 'three')

                print('SELECTED: %s' % name)

            m.addDynMenu( callback )
        """
        plist = pathstr.split(self.splitchar)
        menu = self._addMenuFields(plist)
        menu._dyn_callback = callback
        menu.aboutToShow.connect(menu._addDynActions)

    def addField(self, pathstr, callback=None, args=(), tip=None):
        plist = pathstr.split(self.splitchar)
        kid = self._addMenuFields(plist[:-1])

        acall = ActionCall(callback, *args)
        action = QtWidgets.QAction(plist[-1], kid)
        action.triggered.connect(acall)

        if tip:
            action.setStatusTip(tip)

        kid.addAction(action)

        return kid


class VQMenuBar(FieldAdder, QtWidgets.QMenuBar):
    def __init__(self, parent=None, splitchar='.'):
        QtWidgets.QMenuBar.__init__(self, parent=parent)
        FieldAdder.__init__(self, splitchar=splitchar)


class VQMenu(FieldAdder, QtWidgets.QMenu):
    def __init__(self, name, parent=None, splitchar='.'):
        QtWidgets.QMenu.__init__(self, name, parent=parent)
        FieldAdder.__init__(self, splitchar=splitchar)


class ActionCall:
    def __init__(self, callback, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.callback = callback

    def __call__(self):
        return self.callback(*self.args, **self.kwargs)
