#!/usr/bin/python
# -*- coding: utf-8 -*-
import geoDataManager.Model.modelcsv as model
import geoDataManager.View.view as view


class Controller:
    def __init__(self, model1, view1) -> object:
        self.model = model1
        startup_folders = self.model.getFolders()
        self.view = view1
        # if view is of type Tkinter view:
        self.view.call_back(self)
        # has to be last method
        self.view.start(startup_folders)

    def addFolder(self, folder):
        """gets new folder from view and passes to model"""
        try:
            files, folders = self.model.addFolder(path=folder)
            print('Added ', len(files), ' files')
            return files, folders
        except NotADirectoryError as e:
            print('No Directory Selected.', e)
            return NotADirectoryError
        except TypeError as e:
            print('controller caught typeError: ', e)

    def getFolder(self, folder):
        """Get all the files in a folder that has already been connected to"""
        files = self.model.getFileList(folder[0])
        return files

    def getMetadata(self, file):
        """returns metadata object for the selected file"""
        # print('controller:',file)
        file_dict = self.model.getFile(file)
        return file_dict

    def addTag(self,tag,filepath):
        """Add tag to the current file"""
        self.model.addTag(tag,filepath)

    def removeFolder (self,path):
        self.model.removeFolder(path)

def main():
    c = Controller(model.ModelCsv, view.ViewTkinter)
    #c.addFolder("C:\\Users\\kschw\\documents\\mapping")
    c.removeFolder('C:/Users/kschw/Documents/mapping')


if __name__ == '__main__':
    main()
