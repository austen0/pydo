#!/usr/bin/env python3
#
# Basic todo list app.

__author__ = 'austen0'

__version__ = 0.1


import humanize
import npyscreen
import re
import sqlite3

from time import time
from os.path import expanduser


APP_DIR = expanduser('~') + '/.pydo'
TODO = APP_DIR + '/todo.db'
COMPLETE = APP_DIR + '/complete.db'


class DatabaseManager(object):
  def __init__(self, db_file):
    self.dbfilename = db_file
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'CREATE TABLE IF NOT EXISTS records( \
        record_internal_id INTEGER PRIMARY KEY, \
        description TEXT, \
        priority_id INTEGER, \
        notes TEXT, \
        last_modified INTEGER \
      )'
    )
    db.commit()
    c.close()

  def add_record(self, description = '', priority_id = '', notes = '',
                 last_modified  = ''):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'INSERT INTO records( \
        description, \
        priority_id, \
        notes, \
        last_modified) \
        VALUES(?,?,?,?)',
      (description, str(priority_id), notes, str(last_modified))
    )
    db.commit()
    c.close()

  def delete_record(self, record_id):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'DELETE FROM records WHERE record_internal_id = ?', (str(record_id)))
    db.commit()
    c.close()

  def get_record(self, record_id):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'SELECT * FROM records WHERE record_internal_id = ?',
      (str(record_id))
    )
    records = c.fetchall()
    c.close()
    return records[0]

  def list_all_records(self):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute('SELECT * FROM records ORDER BY priority_id')
    records = c.fetchall()
    c.close()
    return records

  def update_record(self, record_id, description = '', priority_id = '',
                    notes = '', last_modified = ''):
    db = sqlite3.connect(self.dbfilename)
    c = db.cursor()
    c.execute(
      'UPDATE records SET \
        description = ?, \
        priority_id = ?, \
        notes = ? , \
        last_modified = ? \
      WHERE record_internal_id = ?',
      (description, str(priority_id), notes, str(last_modified), str(record_id))
    )
    db.commit()
    c.close()


class EditTodo(npyscreen.ActionForm):
  def create(self):
    self.value = None
    self.wgDescription = self.add(npyscreen.TitleText, name = 'Description:')
    self.wgLastModified = self.add(
      npyscreen.TitleFixedText,
      name = 'Last Modified:',
      editable = False,
      use_two_lines = False
    )
    self.wgPriority = self.add(
      npyscreen.TitleSelectOne,
      name = 'Priority:',
      values = ['P1 (Hi)', 'P2 (Med)', 'P3 (Low)'],
      max_height = 3,
      scroll_exit = True
    )
    self.add(npyscreen.TitleFixedText, name = 'Notes:', editable = False)
    self.wgNotes = self.add(npyscreen.MultiLineEdit)

  def beforeEditing(self):
    if self.value:
      todo = self.parentApp.todoDb.get_record(self.value)
      self.name = 'Todo id : %s' % todo[0]
      self.todo_id = todo[0]
      self.wgDescription.value = todo[1]
      self.wgPriority.value = todo[2]
      self.wgNotes.value = todo[3]
      self.wgLastModified.value = humanize.naturaltime(int(time()) - todo[4])
    else:
      self.name = 'New Todo'
      self.todo_id = ''
      self.wgDescription.value = ''
      self.wgPriority.value = 1
      self.wgNotes.value = ''
      self.wgLastModified.value = ''

  def on_ok(self):
    if self.todo_id:
      self.parentApp.todoDb.update_record(
        self.todo_id,
        description = self.wgDescription.value,
        priority_id = self.wgPriority.value[0],
        notes = self.wgNotes.value,
        last_modified = int(time())
      )
    else:
      self.parentApp.todoDb.add_record(
        description = self.wgDescription.value,
        priority_id = self.wgPriority.value[0],
        notes = self.wgNotes.value,
        last_modified = int(time())
      )
    self.parentApp.switchFormPrevious()

  def on_cancel(self):
    self.parentApp.switchFormPrevious()


class CompleteList(npyscreen.MultiLineAction):
  def __init__(self, *args, **keywords):
    super(CompleteList, self).__init__(*args, **keywords)
    self.add_handlers({
      'r': self.recover_todo,
      's': self.show_active,
      'd': self.delete_todo,
      'q': self.quit,
    })

  def display_value(self, vl):
    priority = vl[2] + 1
    last_mod = humanize.naturaltime(int(time()) - vl[4])
    last_mod_buf = ' ' * (15 - len(last_mod))
    last_mod = last_mod + last_mod_buf
    return ' P%d | %s | %s' % (priority, last_mod, vl[1])

  def delete_todo(self, *args, **keywords):
    self.parent.parentApp.completeDb.delete_record(
      self.values[self.cursor_line][0])
    self.parent.update_list()

  def quit(self, *args, **keywords):
    self.parent.parentApp.switchForm(None)

  def recover_todo(self, *args, **keywords):
    self.parent.parentApp.todoDb.add_record(
      description = self.values[self.cursor_line][1],
      priority_id = self.values[self.cursor_line][2],
      notes = self.values[self.cursor_line][3],
      last_modified = self.values[self.cursor_line][4],
    )
    self.parent.parentApp.completeDb.delete_record(
      self.values[self.cursor_line][0])
    self.parent.update_list()

  def show_active(self, *args, **keywords):
    self.parent.parentApp.switchForm('MAIN')


class TodoList(npyscreen.MultiLineAction):
  def __init__(self, *args, **keywords):
    super(TodoList, self).__init__(*args, **keywords)
    self.add_handlers({
      'a': self.add_todo,
      'c': self.complete_todo,
      's': self.show_complete,
      'd': self.delete_todo,
      'q': self.quit,
    })

  def display_value(self, vl):
    priority = vl[2] + 1
    last_mod = humanize.naturaltime(int(time()) - vl[4])
    last_mod_buf = ' ' * (15 - len(last_mod))
    last_mod = last_mod + last_mod_buf
    return ' P%d | %s | %s' % (priority, last_mod, vl[1])

  def actionHighlighted(self, act_on_this, keypress):
    self.parent.parentApp.getForm('EDITTODOFM').value = act_on_this[0]
    self.parent.parentApp.switchForm('EDITTODOFM')

  def add_todo(self, *args, **keywords):
    self.parent.parentApp.getForm('EDITTODOFM').value = None
    self.parent.parentApp.switchForm('EDITTODOFM')

  def complete_todo(self, *args, **keywords):
    self.parent.parentApp.completeDb.add_record(
      description = self.values[self.cursor_line][1],
      priority_id = self.values[self.cursor_line][2],
      notes = self.values[self.cursor_line][3],
      last_modified = self.values[self.cursor_line][4],
    )
    self.parent.parentApp.todoDb.delete_record(self.values[self.cursor_line][0])
    self.parent.update_list()

  def delete_todo(self, *args, **keywords):
    self.parent.parentApp.todoDb.delete_record(self.values[self.cursor_line][0])
    self.parent.update_list()

  def quit(self, *args, **keywords):
    self.parent.parentApp.switchForm(None)

  def show_complete(self, *args, **keywords):
    self.parent.parentApp.switchForm('COMPLETEFM')


class CompleteDisplay(npyscreen.FormMutt):
  MAIN_WIDGET_CLASS = CompleteList
  STATUS_WIDGET_CLASS = npyscreen.wgtextbox.Textfield
  COMMAND_WIDGET_CLASS = npyscreen.wgtextbox.Textfield

  def beforeEditing(self):
    self.update_list()

  def update_list(self):
    self.wStatus1.value = ' Pr | Last Modified   | Task '
    self.wMain.values = self.parentApp.completeDb.list_all_records()
    self.wStatus2.value = ' Pydo v0.1 '
    self.wCommand.value = '(r)ecover  (s)how_active  (d)elete  (q)uit'
    self.wMain.display()


class TodoListDisplay(npyscreen.FormMutt):
  MAIN_WIDGET_CLASS = TodoList
  STATUS_WIDGET_CLASS = npyscreen.wgtextbox.Textfield
  COMMAND_WIDGET_CLASS = npyscreen.wgtextbox.Textfield

  def beforeEditing(self):
    self.update_list()

  def update_list(self):
    self.wStatus1.value = ' Pr | Last Modified   | Task '
    self.wMain.values = self.parentApp.todoDb.list_all_records()
    self.wStatus2.value = ' Pydo v0.1 '
    self.wCommand.value = '(a)dd  (c)omplete  (s)how_complete  (d)elete  (q)uit'
    self.wMain.display()


class PydoApp(npyscreen.NPSAppManaged):
  def onStart(self):
    self.todoDb = DatabaseManager(TODO)
    self.completeDb = DatabaseManager(COMPLETE)
    self.addForm('MAIN', TodoListDisplay)
    self.addForm('COMPLETEFM', CompleteDisplay)
    self.addForm('EDITTODOFM', EditTodo)


if __name__ == '__main__':
  pydo = PydoApp()
  pydo.run()
