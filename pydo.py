#!/usr/bin/env python3
#
# Basic todo list app.

__author__ = 'austen0'

__version__ = 0.1


import npyscreen
import re
import sqlite3


TODO_INCOMPLETE = 'todo_incomplete.db'
#TODO_COMPLETE = 'todo_complete.db'


class EditTodo(npyscreen.ActionForm):
  def create(self):
    self.value = None
    self.wgDescription = self.add(npyscreen.TitleText, name = 'Description:',)
    self.wgPriority = self.add(
      npyscreen.TitleSelectOne,
      name = 'Priority:',
      values = ['1 (Hi)', '2 (Med)', '3 (Low)'],
      scroll_exit = True
    )

  def beforeEditing(self):
    if self.value:
      todo = self.parentApp.todoDb.get_todo(self.value)
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
      self.parentApp.todoDb.update_todo(
        self.todo_id,
        description = self.wgDescription.value,
        priority_id = self.wgPriority.value,
      )
    else:
      self.parentApp.todoDb.add_todo(
        description = self.wgDescription.value,
        priority_id = self.wgPriority.value,
      )
    self.parentApp.switchFormPrevious()

  def on_cancel(self):
    self.parentApp.switchFormPrevious()


class TodoDatabase(object):
  def __init__(self):
    self.dbfilename = TODO_INCOMPLETE
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'CREATE TABLE IF NOT EXISTS todos( \
        todo_internal_id INTEGER PRIMARY KEY, \
        description TEXT, \
        priority_id INTEGER \
      )'
    )
    db.commit()
    c.close()

  def add_todo(self, description = '', priority_id = ''):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'INSERT INTO todos(description, priority_id) VALUES(?,?)',
      (description, str(priority_id[0]))
    )
    db.commit()
    c.close()

  def delete_todo(self, todo_id):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute('DELETE FROM todos WHERE todo_internal_id = ?', (str(todo_id)))
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
    c.execute('SELECT * FROM todos ORDER BY priority_id')
    todos = c.fetchall()
    c.close()
    return todos

  def update_todo(self, todo_id, description = '', priority_id = ''):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'UPDATE todos SET description = ?, priority_id = ? \
      WHERE todo_internal_id = ?',
      (description, str(priority_id[0]), str(todo_id))
    )
    db.commit()
    c.close()


class TodoList(npyscreen.MultiLineAction):
  def __init__(self, *args, **keywords):
    super(TodoList, self).__init__(*args, **keywords)
    self.add_handlers({
      '^A': self.add_todo,
      '^D': self.delete_todo,
      '^Q': self.quit,
    })

  def display_value(self, vl):
    return '%s  %s' % (vl[2] + 1, vl[1])

  def actionHighlighted(self, act_on_this, keypress):
    self.parent.parentApp.getForm('EDITTODOFM').value = act_on_this[0]
    self.parent.parentApp.switchForm('EDITTODOFM')

  def add_todo(self, *args, **keywords):
    self.parent.parentApp.getForm('EDITTODOFM').value = None
    self.parent.parentApp.switchForm('EDITTODOFM')

  def delete_todo(self, *args, **keywords):
    self.parent.parentApp.todoDb.delete_todo(self.values[self.cursor_line][0])
    self.parent.update_list()

  def quit(self, *args, **keywords):
    self.parent.parentApp.switchForm(None)


class TodoListDisplay(npyscreen.FormMutt):
  MAIN_WIDGET_CLASS = TodoList
  STATUS_WIDGET_CLASS = npyscreen.wgtextbox.Textfield
  COMMAND_WIDGET_CLASS = npyscreen.wgtextbox.Textfield

  def beforeEditing(self):
    self.update_list()

  def update_list(self):
    self.wStatus1.value = 'Pydo v0.1'
    self.wMain.values = self.parentApp.todoDb.list_all_todos()
    self.wCommand.value = '^(A)dd  ^(D)elete  ^(Q)uit'
    self.wMain.display()


class PydoApp(npyscreen.NPSAppManaged):
  def onStart(self):
    self.todoDb = TodoDatabase()
    self.addForm('MAIN', TodoListDisplay)
    self.addForm('EDITTODOFM', EditTodo)


if __name__ == '__main__':
  pydo = PydoApp()
  pydo.run()
