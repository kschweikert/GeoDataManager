#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import geoDataManager.Model.metadata as metadata
import geoDataManager.Controller.mvc_exc as mvc_exc
import geoDataManager.Model.csv_backend as csv

class File():
    fileCsv = csv.CsvFileMetadata('files.csv')
    def __init__(self, path, tags=''):
        self.path = path
        self.tags = tags if tags is not '' else []
        if os.path.exists(path):
            self._getDetails()
            self.getMetadata()
        else:
            raise FileNotFoundError

    def getMetadata(self):
        """get values from GDAL/OGR"""
        try:
            self.mdata = vars(metadata.metadata(self.path))
            self.type = self.mdata.get('filetype')
        except mvc_exc.NotGeospatialFile:
            # print("No geospatial metadata for this file")
            self.type = 'Not Supported'


    def addTag(self, tag):
        print(self.tags)
        if self.tags == '[]':
            self.tags = []
        self.tags.append(tag)

    def _getDetails(self):
        self.dateModified = os.path.getmtime(self.path)
        self.dateAdded = os.path.getctime(self.path)
        self.folder, self.filename = os.path.split(self.path)
        # get filesize in MB
        self.size = ((os.path.getsize(self.path)))
        self.root, self.ext = os.path.splitext(self.path)

    def display(self):
        return (vars(self))

   #def appendMetadata(self):
   #    keys_to_extract = ['path','tags','type']
   #    metadata_subset ={key:self.__dict__[key] for key in keys_to_extract}
   #    if hasattr(self,'mdata'):
   #        geodata = self.mdata
   #        #print(geodata)
   #    File.fileCsv.appendData(metadata_subset)

    def updateFile(self):
        pass #Todo function to refresh metadata for changes while application is open


def main():
    testfile = File(input("full file path for test file: "))
    print(testfile.display())


if __name__ == '__main__':
    main()
