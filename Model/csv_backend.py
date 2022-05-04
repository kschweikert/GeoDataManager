#!/usr/bin/python
#-*- coding: utf-8 -*-
import csv
import geoDataManager.Controller.mvc_exc as mvc_exc

class CsvObject:
    def __init__(self, csvfile):
        self.csvfile = csvfile

    def loadData(self):
        # Read data out of CSV and add to returned list
        items = list()
        try:
            with open(self.csvfile, "r+", newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    items.append(row)
                    print(row)
            #print(items)
            return items
        except (FileNotFoundError) as e:
            print('database not found: ', e)
            #raise mvc_exc.DatabaseNotFound

    def appendData(self,item):
        # Append an item to the end of the  file
        with open(self.csvfile, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([item])

    def writeData(self,list):
        # Overwrite the inventory with the existing in memory inventory list
        with open(self.csvfile, "w", newline='') as f:
            writer = csv.writer(f)
            for item in list:
                writer.writerow(item)

class CsvFolderList(CsvObject):
    pass

class CsvFileMetadata(CsvObject):
    #dataOrder = ['filename','folder','ext', 'root', 'type', 'size', 'dateModified', 'dateAdded','tags','path']
    dataOrder = ['path','tags','type']
    def loadData(self):
        # Read data out of CSV and add to returned list as dictionary
        items = list()
        try:
            with open(self.csvfile, "r+", newline='') as f:
                reader = csv.DictReader(f, fieldnames=CsvFileMetadata.dataOrder, quotechar='|')
                for row in reader:
                    items.append(row)
            return items
        except (Exception,FileNotFoundError) as e:
            print('database not found', e)
            raise mvc_exc.DatabaseNotFound

    def appendData(self, metadataDict):
        '''Append an item to the end of the  file'''
        values = metadataDict
        try:
            with open(self.csvfile, "a", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=CsvFileMetadata.dataOrder, quotechar='|')
                #print(self, values)
                writer.writerow(values)
        except Exception as e:
            print("can't write data", e)

    def writeData(self, filelist):
        '''Overwrite the inventory with the existing in memory inventory list'''
        try:
            with open(self.csvfile, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=CsvFileMetadata.dataOrder, quotechar='|')
                #writer.writeheader()
                for item in filelist:
                    writer.writerow(item)
        except Exception as e:
            print('csv_backend: ', e)

def main():
    test = CsvObject("test.csv")
    test.writeData(["1","2","3"])
    #test_db = CsvObject("../folders.csv")
    #folders = test_db.loadData()
    #print(folders)
    test_file=CsvFileMetadata("dictionary.csv")
    test_file.writeData([{'path':'file/path/', 'tags': ['test','tag2'],'type':'Not Supported'}])

if __name__ == '__main__':
    main()