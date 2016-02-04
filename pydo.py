#!/usr/bin/env python3
#
# Basic todo list app.
#

__author__ = 'austen0'

__version__ = 0.1


import npyscreen
import re
import sqlite3


class EditTodo(npyscreen.ActionForm):
  def create(self):
    self.value = None
    self.wgDescription = self.add(npyscreen.TitleText, name = 'Description:',)
    self.wgPriority = self.add(
      npyscreen.TitleSelectOne,
      name = 'Priority:',
      values = ['High', 'Normal', 'Low'],
      scroll_exit = True
    )

  def beforeEditing(self):
    if self.value:
      todo = self.parentApp.myDatabase.get_todo(self.value)
      self.name = 'Todo id : %s' % todo[0]
      self.todo_id = todo[0]
      self.wgDescription.value = todo[1]
      self.wgPriority.value = todo[2]
    else:
      self.name = 'New Todo'
      self.todo_id          = ''
      self.wgDescription.value   = ''
      self.wgPriority.value = ''

  def on_ok(self):
    if self.todo_id:
      self.parentApp.myDatabase.update_todo(
        self.todo_id,
        description = self.wgDescription.value,
        priority = self.wgPriority.get_selected_objects(),
      )
    else:
      self.parentApp.myDatabase.add_todo(
        description = self.wgDescription.value,
        priority    = self.wgPriority.get_selected_objects(),
      )
    self.parentApp.switchFormPrevious()

  def on_cancel(self):
    self.parentApp.switchFormPrevious()


class TodoDatabase(object):
  def __init__(self, filename='example-todos.db'):
    self.dbfilename = filename
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'CREATE TABLE IF NOT EXISTS todos( \
        todo_internal_id INTEGER PRIMARY KEY, \
        description TEXT, \
        priority    TEXT \
      )'
    )
    db.commit()
    c.close()

  def add_todo(self, description = '', priority = ''):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'INSERT INTO todos(description, priority) VALUES(?,?)',
      (description, str(priority))
    )
    db.commit()
    c.close()

  def get_todo(self, todo_id):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'SELECT * FROM todos WHERE todo_internal_id = ?',
      (str(todo_id))
    )
    todos = c.fetchall()
    c.close()
    return todos[0]

  def list_all_todos(self):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute('SELECT * FROM todos')
    todos = c.fetchall()
    c.close()
    return todos

  def update_todo(self, todo_id, description = '', priority = ''):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'UPDATE todos SET description = ?, priority = ? \
      WHERE todo_internal_id = ?',
      (description, str(priority), str(todo_id))
    )
    db.commit()
    c.close()


class TodoList(npyscreen.MultiLineAction):
  def __init__(self, *args, **keywords):
    super(TodoList, self).__init__(*args, **keywords)
    self.add_handlers({
      '^A': self.when_add_todo,
      '^Q': self.when_quit,
    })

  def display_value(self, vl):
    return '%s, %s' % (re.sub('[^A-Za-z0-9]+', '', vl[2]), vl[1])

  def actionHighlighted(self, act_on_this, keypress):
    self.parent.parentApp.getForm('EDITTODOFM').value =act_on_this[0]
    self.parent.parentApp.switchForm('EDITTODOFM')

  def when_add_todo(self, *args, **keywords):
    self.parent.parentApp.getForm('EDITTODOFM').value = None
    self.parent.parentApp.switchForm('EDITTODOFM')

  def when_quit(self, *args, **keywords):
    self.parent.parentApp.switchForm(None)


class TodoListDisplay(npyscreen.FormMutt):
  MAIN_WIDGET_CLASS = TodoList
  def beforeEditing(self):
    self.name = 'Pydo v0.1'
    self.update_list()

  def update_list(self):
    self.wMain.values = self.parentApp.myDatabase.list_all_todos()
    self.wMain.display()


class PydoApp(npyscreen.NPSAppManaged):
  def onStart(self):
    self.myDatabase = TodoDatabase()
    self.addForm('MAIN', TodoListDisplay)
    self.addForm('EDITTODOFM', EditTodo)


if __name__ == '__main__':
  pydo = PydoApp()
  pydo.run()
