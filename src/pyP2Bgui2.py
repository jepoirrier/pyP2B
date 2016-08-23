#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retrieve PubMed reference from its PMID given as last argument
Copyright (C) 2006-2007 Jean-Etienne Poirrier

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

WARNING: no check for duplicate references (just add the ref)
TODO: all exception handling
INFOS: http://www.poirrier.be/~jean-etienne/software/pyp2b/
E-MAIL: jepoirrier@gmail.com
With excellent support and addition from Michel Veret!

To use under window type the comma d :
chcp 65001
in the command window (invite de commande)
"""

from pyP2Bclass import pyP2B
from tkinter.scrolledtext import *
from tkinter import *
from tkinter import messagebox

class App:

    def __init__(self, master):

        def saisie():
            pmid = valeur.get()
            resultBox.delete("1.0", END)
            if (len(pmid) > 0 ):
                print("===|{0}|===".format(pmid))
                myref = pyP2B()
                resultBox.insert('end', myref.getPubmedReference(pmid))
            else:
                messagebox.showinfo("Alerte", "PMID Vide...")
                resultBox.insert("end", "PMID non transmis...")


        valeur = StringVar()

        frame = Frame(master)
        frame.pack()

        queryFrame = Frame(frame)
        queryFrame.pack(fill=X)

        label = Label(queryFrame, text="PMID: ")
        label.pack(side=LEFT)

        entry = Entry(queryFrame, textvariable=valeur, text='        ')
        entry.pack(side=LEFT)

        okButton = Button(queryFrame, text="OK", command=saisie)
        okButton.pack(side=LEFT)

        resultFrame = Frame(frame)
#        resultFrame.pack(fill=X)
# From : http://stackoverflow.com/questions/29966805/fill-space-with-widgets-on-resize
        resultFrame.pack(fill=BOTH, expand=True)

        resultBox = ScrolledText(resultFrame)
        resultBox.pack(side=LEFT)

root = Tk()
root.title('pyP2B GUI - Search by PMID')
root.resizable(1,1)

app = App(master=root)
root.mainloop()

# app = App(root)

# root.mainloop()
