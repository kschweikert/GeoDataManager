#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from geoDataManager.Controller import mvc_exc
import geoDataManager.Model.file as file
import geoDataManager.Model.csv_backend as csv


class ModelCsv():
    """Maintains a list of added folders and dictionary of contained file objects"""

    def __init__(self):
        self._folderList = []
        self._fileDict = {}
        self._fileTags = []
        self.folderCsv = csv.CsvObject('folders.csv')
        self.fileCsv = file.File.fileCsv
        self.readFolderDB()


    def readFolderDB(self):
        """Get list of folders from the folder database
        """
        print('Reading ', self.folderCsv.csvfile)
        try:
            self._folderList = self.folderCsv.loadData()
        except FileNotFoundError:
            print("No database to load")
        self.readFilesDB()
        #check for new files
        for folder in self._folderList:
            print(folder[0])
            files = os.listdir(folder[0])
            for f in files:
                fullpath = str(folder[0]) + "/" + str(f)
                if not fullpath in self._fileDict:
                    if os.path.isfile(fullpath):
                        print('Adding ', fullpath)
                        file.File(f)

    def readFilesDB(self):
        """Get list of files from the files database"""
        print('Reading ', self.fileCsv.csvfile)
        try:
            file_list = self.fileCsv.loadData()
            for item in file_list:
                if item != []:
                    try:
                        fname = item['path']
                        tags = item['tags']
                        tags=tags.strip('[]')
                        tags_list = tags.split(",")
                        # create file object
                        f_object = file.File(fname, tags=[tags_list])
                        #if tags != []: print(f_object.__dict__['tags'])
                        self._fileDict.update({fname: f_object})
                    except (FileNotFoundError):
                        print("Unable to read file", item)
        except (mvc_exc.DatabaseNotFound):
            print("Database file not found.")

    def addFolder(self, path):
        """add a folder to the list of data folders. this builds the metadata info and returns """
        # check folder has not already been added
        if (path in self._folderList):
            raise mvc_exc.FolderAlreadyAdded
        else:
            print('Adding', path)
            self._folderList.append(path)
            if not os.path.exists(path):
                raise NotADirectoryError
            # scan folder
            try:
                files, subfolders = self.addFiles(path)
                # save folder to csv list
                self.folderCsv.appendData(path)
                return files, subfolders
            except TypeError:
                print('Error adding files')

    def readFolders(self, ):
        return self._folderList

    def removeFolder(self, path):
        found = False
        for i in range(len(self._folderList)):
            # print(self._folderList[i])
            if self._folderList[i] == path:
                del self._folderList[i]
                found = True
            # TODO also delete all the file objects
            for p, fileobj in self._fileDict.items():
                if fileobj.folder == path:
                    del fileobj
        if not found:
            print(self._folderList)
            raise mvc_exc.FolderNotFound("Can't delete folder that has not been connected: " + path)

    def addFiles(self, directory):
        """Add all files in a directory to the database. This fetches the metadata for every subfile in the specified folder and adds it to file dictionary.
        Returns a list of the added folder and a list of all subdirectories"""
        dir_list = os.listdir(directory)
        file_list = []
        subdirectory_list = []
        for f in dir_list:
            fullpath = str(directory) + "/" + str(f)
            if os.path.isfile(fullpath):
                # create file object and populate with metadata
                f_index = file.File(fullpath)
                # add file object to dict with filename as key
                self._fileDict[f_index.path] = f_index
                file_list.append(fullpath)
            elif os.path.isdir(fullpath):
                # TODO option to include recursively
                # print("---- passing on subdirectory " + str(f))
                subdirectory_list.append(fullpath)
        # write updated info to csv
        self.writeFiles()
        return file_list, subdirectory_list

    def getFiles(self):
        """Get all metadata for all files. Returns nested dictionary containing file key and metadata dictionary values"""
        return self._fileDict

    def getFolders(self):
        return self._folderList

    def getFileList(self, folder):
        """Get the list of all file names that have metadata stored. Returns list of filepaths"""
        all = self._fileDict.keys()
        filelist = []
        for files in all:
            folder2, filename = os.path.split(files)
            if folder2 == folder:
                filelist.append(files)
        subfolders=[]
        return filelist, subfolders

    def getFile(self, filepath):
        """Get the metadata for a single file by path. Returns nested dictionary of metadata"""
        return self._fileDict[filepath]

    def addTag(self, tag, filepath):
        """Add tag to list and pass tag to the file object"""
        if not (tag in self._fileTags):
            self._fileTags.append(tag)
            print("tag added to list: ", tag)
        fileobject = self._fileDict[filepath]
        fileobject.addTag(tag)
        self.writeFiles()

    def writeFiles(self):
        # print(self._fileDict)
        keys_to_extract = ['path', 'tags', 'type']
        file_list = []
        for fname, fobject in self._fileDict.items():
            # for each file object, create a dictionary with only keys_to_extract
            metadata_subset = {key: fobject.__dict__[key] for key in keys_to_extract}
            file_list.append(metadata_subset)
        file.File.fileCsv.writeData(file_list)


def main():
    # create model
    test = ModelCsv()
    print(test._folderList)
    # add folder
    path1 = input("path to test folder:")
    test.addFolder(str(path1))

    # read list of folders
    print(test.readFolders())

    # add and remove folder
    # test.addFolder("C:\\Users")
    # print(test.readFolders())
    # test.removeFolder("C:\\Users")
    # print(test.readFolders())
    try:
        test.removeFolder("C:\\Users")
    except mvc_exc.FolderNotFound:
        print("caught exception on delete")

    # getFiles in a folder

    # files = test.addFiles(path1)
    # print(files)
    # print(files[0])
    # fileDetail = test.getFiles()
    # print(fileDetail)
    # filelist= test.getFileList()
    # print(filelist)


if __name__ == '__main__':
    main()
