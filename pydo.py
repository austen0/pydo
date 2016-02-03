#!/usr/bin/env python3
#
# Basic todo list app.
#
# Author: ***REMOVED*** (***REMOVED***)


import npyscreen

class PydoApp(npyscreen.NPSAppManaged):
  def onStart(self):
    self.registerForm('MAIN', MainForm())

class MainForm(npyscreen.Form):
  def create(self):
    self.add(npyscreen.TitleText, name = 'Text:', value = 'Hello, world.')

  def afterEditing(self):
    self.parentApp.setNextForm(None)

if __name__ == '__main__':
  pydo = PydoApp()
  pydo.run()
