#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

Resources used:
general: https://tkdocs.com/tutorial/
for dir treeview: https://stackoverflow.com/questions/16746387/display-directory-content-with-tkinter-treeview-widget
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from abc import ABC, abstractmethod
import os
import time
import geoDataManager.Controller.mvc_exc as mvc_exc


class view(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def start(self,startupfolders=None):
        pass


class ViewTkinter(view):

    def __init__(self):
        super().__init__()
        self.window = None
        self.main_frame = None
        self.controller = None
        # left pane
        self.frame = None
        self.tree = None
        self.buttonFolder = None
        # right pane
        self.frame2 = None
        self.table = None
        self.tag_enter = None
        self.metadata_pane = None
        self.detached_items = []


    def call_back(self, controller):
        """bind controller object instance that created the view"""
        self.controller = controller

    def loadFolders(self, startup):
        """Populate the directory tree for all folders that are already connected on startup"""
        if startup == [[]] or startup  ==[]:
            print('No saved folders to load')
        elif startup == None:
            print('No database to load')
        else:
            for item in startup:
                print('...populating ',item)
                #self.tree.insert('','end', item, text=item)
                # TODO finish populating with items
                files, subfolders = self.controller.getFolder(item)
                self._populateTree(item,files,subfolders)

    def addFolder(self):
        """Action for pressing the add folder button. Adds folder to database and populates the connected folders tree"""
        try:
            folder = tk.filedialog.askdirectory(mustexist=True)
            files, subfolders = self.controller.addFolder(folder)
            if files == None:
                raise mvc_exc.FolderNotFound
            self._populateTree(folder, files, subfolders)
            self.filterList()
        except (TypeError, NotADirectoryError, mvc_exc.FolderAlreadyAdded) as e:
            print('Error: ', e)

    def _populateTree(self, folder, files, subfolders):
        """Append parent folder, and child files to the Connected Folders tree (self.tree)."""
        try:
            self.tree.insert('', 'end', folder, text=folder)
        except tk.TclError:
            print("folder already exists")
        # TODO condition to italicize non geospatial files and add subdirectories
        for file in files:
            #Todo add option to exclude non-geo
            shortname = os.path.basename(file)
            metadata = self.controller.getMetadata(file)
            if metadata.type == 'Not Supported':
                self.tree.insert(folder, 'end', text=shortname, tags=('file', file, 'nonGeo'))
                self.tree.tag_bind(file, '<ButtonRelease-1>', self.getMetadata)
            else:
                self.tree.insert(folder, 'end', text=shortname, tags=('file', file, 'geo'))
                self.tree.tag_bind(file, '<ButtonRelease-1>', self.getMetadata)
        for folder in subfolders:
            #print('ignoring subfolder: ',folder)
            # TODO handle subfolders
            pass

    def getMetadata(self, event):
        """Fetch the metadata for the selected file when its highlighted in Current Folders tree"""
        self.loadMetadata()

    def loadMetadata(self):
        fileid = self.tree.focus()
        try:
            info = self.tree.item(fileid)
            # get filepath which was added as a tag to the tree element
            file = info['tags'][1]
            # fetch file dictionary from controller
            fileobject = self.controller.getMetadata(file)
            # first clear the table
            self.clearTable()
            # Populate the metadata table and text box
            try:
                # print(fileobject.mdata)
                for label, value in fileobject.__dict__.items():
                    # print(label)
                    if label == ('mdata'):
                        for label2, value2 in value.items():
                            # handle the gdal metadata values
                            if label2 in ['bounds', 'layers']:
                                self.table.insert('', 'end', text=label2.title(), values=[str(value2)])
                            elif label2 in ['CRS']:
                                try:
                                    self.table.insert('', 'end', text='Coordinate Reference: ', values=value2.GetName())
                                except AttributeError as e:
                                    print("Not a geospatial file. No CRS")
                            elif label2 == 'infoDump':
                                print('FOUND GEOSPATIAL INFO')
                                self.metadata_pane.configure(state='normal')
                                # print(self.metadata_pane['state'])
                                self.metadata_pane.insert('1.0', value2)
                                self.metadata_pane.configure(state='disabled')
                            else:
                                pass
                                # print('other mdata: ', label2, value2)
                    elif label in ['size']:
                        # convert size
                        # print('Size',str(value))
                        if value / (1024 * 1024) > 1:
                            self.table.insert('', 'end', text='Size (MB)', values=(str(round(value / (1024 * 1024)))))
                        else:
                            self.table.insert('', 'end', text='Size (KB)', values=str(round(value)))
                    elif label in ['dateModified', 'dateAdded']:
                        # convert string to date
                        label_pretty = label[:4] + " " + label[4:]
                        changedate = time.ctime(value)
                        # print(str(changedate))
                        self.table.insert('', 'end', text=label_pretty.title(), values=[(str(changedate))])
                    elif label in ['tags']:
                        self.table.insert('', 'end', text=label.title(), values=[value])
                    elif label in ['path']:
                        self.table.insert('', 'end', text=label.title(), values=str(value))
            except RuntimeError as e:
                print('Unable to insert file: ',fileid, e)
        except RuntimeError as e:
            print(e)

    def addTag(self):
        tag = self.tag_enter.get()
        fileid = self.tree.focus()
        try:
            info = self.tree.item(fileid)
            file = info['tags'][1]
        except (RuntimeError, IndexError):
            print('No File Selected in Folder Tree')
        self.controller.addTag(tag,file)
        print('Added tag')
        update = self.controller.getMetadata(file)
        #print(update.__dict__)
        self.loadMetadata()

    def filterList(self):
        print('Filtering ',self.filefilter.get())
        if self.filefilter.get() == 'geo':
            hideList = self.tree.tag_has('nonGeo')
            for item in hideList:
                parent = self.tree.parent(item)
                index = self.tree.index(item)
                self.tree.detach(item)
                self.detached_items.append([item,parent,index])

        if self.filefilter.get()=='all':
            # print(self.detached_items)
            for item in self.detached_items:
                self.tree.reattach(item[0],item[1],item[2])


    def clearTable(self):
        """Clears the metadata table (self.table) and geospatial metadata text box (self.metadata_pane) to the right of the application. """
        for item in self.table.get_children():
            self.table.delete(item)
        self.metadata_pane.configure(state='normal')
        # text=self.metadata_pane.get('1.0','end')
        self.metadata_pane.delete('1.0', 'end')
        self.metadata_pane.configure(state='disabled')
        # self.metadata_pane.del
        # self.metadata_pane=

    def start(self,startupfolders):
        """Start tkinter and build the application elements"""
        self.window = tk.Tk()
        self.window.title("GeoData Manager")
        # self.window.geometry("800x600")

        # create main content frame
        self.main_frame = ttk.Frame(self.window, relief="ridge", padding=(3, 3, 12, 12))
        self.main_frame.grid(column=0, row=0, sticky='nsew')

        # create subframes
        self.frame = ttk.LabelFrame(self.main_frame, text="Connected Folders: ", borderwidth=2, relief='sunken')
        self._create_file_pane()
        self.frame2 = ttk.LabelFrame(self.main_frame, text="Metadata", borderwidth=2, relief='sunken')
        self._create_metadata_pane()

        # place elements
        self.frame.grid(column=0, row=0, sticky='nsew')
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.buttonFolder.grid(row=2, column=0, padx=15, pady=15, sticky='s')
        self.geoOnly.grid(row=3, column=0, sticky='s')

        self.frame2.grid(row=0, column=1, sticky='nsew')
        self.table.grid(row=0, column=0, sticky='nsew')
        self.frame3.grid(row=1, column=0, sticky='e')
        self.tag_entry.grid(row=0, column=0, sticky='e')
        self.buttonTag.grid(row=0, column=0, sticky='e')
        self.metadata_pane.grid(row=2, column=0, sticky='nwe')

        # handle expansion
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=2)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=5)
        self.frame2.columnconfigure(0, weight=1)
        self.frame2.rowconfigure(1, weight=0)
        self.frame2.rowconfigure(2, weight=3)
        self.main_frame.rowconfigure(0, weight=1)

        # print(self.main_frame.grid_slaves())
        #populate tree with files from database:
        startup = startupfolders
        self.loadFolders(startup)
        # handle events
        self.window.mainloop()

    def _create_file_pane(self):
        """Create treeview for Connected Folders and subfiles """
        self.tree = ttk.Treeview(self.frame, show='tree')
        self.tree.column("#0", minwidth=300)
        ysb = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        self.tree.heading('#0', text="Connected Folders: ", anchor='w')
        self.tree.tag_configure('nonGeo', font=('Arial',9,'normal','italic'))
        self.tree.tag_configure('geo', font=('Arial',9,'bold','normal'))
        self.buttonFolder = tk.Button(self.frame, text="+Connect to folder", command=self.addFolder)
        self.filefilter = tk.StringVar(value='all')
        self.geoOnly = tk.Checkbutton(self.frame, text="Geospatial Only", command=self.filterList, variable=self.filefilter, onvalue='geo', offvalue='all')

    def _create_metadata_pane(self):
        """Create treeview for metadata table"""
        self.table = ttk.Treeview(self.frame2, columns=('Value'), show='tree')
        self.table.column('#0', width=120)
        self.frame3 = ttk.Frame(self.frame2, padding=(3, 3, 12, 12))
        self.tag_enter = tk.StringVar()
        self.tag_entry = tk.Entry(self.frame3, textvariable=self.tag_enter)
        self.buttonTag = tk.Button(self.frame3, text ="Add Tag", command=self.addTag)
        self.metadata_pane = tk.Text(self.frame2, height=40)
        self.metadata_pane.insert('1.0', 'Geospatial Metadata')
        # self.metadata_pane['state']='disabled'


def main():
    appInstance = ViewTkinter()
    appInstance.start(None)


if __name__ == '__main__':
    main()
