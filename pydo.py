#!/usr/bin/env python3
#
# Basic todo list app.
#

__author__ = 'austen0'

__version__ = 0.1


import npyscreen


class PydoApp(npyscreen.NPSApp):
  def main(self):
    F = npyscreen.Form(name = 'Pydo v0.1')
    F.edit()


if __name__ == '__main__':
  pydo = PydoApp()
  pydo.run()
