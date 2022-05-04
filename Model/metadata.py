#!/usr/bin/python
# -*- coding: utf-8 -*-
from osgeo import gdal, ogr, osr
from osgeo_utils.samples import ogrinfo
import geoDataManager.Controller.mvc_exc as mvc_exc

gdal.UseExceptions()
ogr.UseExceptions()


class metadata:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filetype = None
        self.getDriver()
        self.infoDump = None
        if self.filetype is not None:
            self.driverpackage = None
            self.layers = None
            self.bounds = None
            self.featureCount = None
            self.open()
        else:
            raise mvc_exc.NotGeospatialFile


    def getDriver(self):
        # map extensions to driver names
        try:
            driver = gdal.IdentifyDriver(self.filepath)
        except RuntimeError as e:
            print("Issue with the driver for this file", e)
            driver = None
        # print("matched:" + driver.ShortName)
        if driver is not None:
            self.filetype = driver.ShortName

    def open(self):
        # driver = gdal.GetDriverByName(self.filetype)
        try:
            #try to open as raster
            dataset = gdal.Open(self.filepath)
            self.driverpackage = 'gdal'
            try:
                self.infoDump = gdal.Info(dataset, options='string')
                self.bounds = dataset.GetGeoTransform()
                self.CRS = dataset.GetSpatialRef()
            except Exception as e:
                print(e)
        except RuntimeError:
            # open as vector
            dataset = ogr.Open(self.filepath)
            # self.infoDump=dataset.__repr__
            self.driverpackage = 'ogr'

        # check to see if its layered (i.e. vector)
        self.layers = dataset.GetLayerCount()

        if self.layers > 0:
            # print("layers: "+ str(self.layers))
            layer = dataset.GetLayer(0)
            self.infoDump = ogr.MajorObject.GetDescription(layer)
            self.bounds = layer.GetExtent()
            self.CRS = layer.GetSpatialRef()
            self.featureCount = [layer.GetFeatureCount()]
            self.infoDump = str(
                'Driver: ' + self.filetype + '\nMain File: ' + self.filepath + '\nFeature Count: ' + str(
                    layer.GetFeatureCount()) + '\nCoordinate System is: ' + str(self.CRS))

    def checkBound(self, bounds):
        pass #TODO check if the file overlaps the specified bounds

    def Display(self):
        for key in self.__dict__:
            print(key, ": ", str(self.__dict__[key]))
        print()


class Drivers():
    def __init__(self):
        self.drivers_ogr = None
        self.drivers_gdal = None
        self.ogr_formats = []
        self.gdal_formats = []
        self.supportedFormats()

    def supportedFormats(self):
        self.drivers_ogr = ogr.GetDriverCount()
        # print("OGR (vector) drivers: " + str(drivers_ogr))
        i = 0
        self.ogr_formats = []
        while i < self.drivers_ogr:
            driver = ogr.GetDriver(i)
            self.ogr_formats.append(driver.name)
            i += 1
        # print(ogr_formats)

        self.drivers_gdal = gdal.GetDriverCount()
        # print("GDAL (raster) drivers: "+ str(drivers_gdal))
        self.gdal_formats = []
        i = 0
        while i < self.drivers_gdal:
            driver = gdal.GetDriver(i)
            self.gdal_formats.append(driver.ShortName)
            i += 1
        # print(gdal_formats)

def main():
    gdal.PushErrorHandler()
    # testfile = metadata(input("full file path for test file: "),input("ext: "))
    test = metadata("C:\\Users\\kschw\\Documents\\mapping\\hydro.gml")
    test2 = metadata("C:\\Users\\kschw\\Documents\\mapping\\trail_data_kat7_26.shp")
    test3 = metadata("C:\\Users\\kschw\\Documents\\mapping\\hallowell_2013_ortho.tif")
    drivers = Drivers()
    # print(drivers.gdal_formats)
    # print(drivers.ogr_formats)
    print(test.__dict__)
    print(test2.__dict__)
    print(test3.__dict__)


    # for items in [test.__dict__.items(),test2.__dict__.items(),test3.__dict__.items()]:
    #    for key,value in items:
    #        if key=='infoDump':
    #            print(key,value)


if __name__ == '__main__':
    main()
