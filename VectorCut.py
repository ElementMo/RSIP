# -*- coding: utf-8 -*-  
""" 
@author 王墨白
@date 2018-04-14 
@brief SHP-栅格影像裁剪
"""  
  
from osgeo import gdal, gdalnumeric, ogr, gdal_array
from PIL import Image, ImageDraw
import os
import operator
from functools import reduce
import cv2

gdal.UseExceptions()

# This function will convert the rasterized clipper shapefile  
# to a mask for use within GDAL.
def imageToArray(img):
    """ 
    将 PIL.Image 转换为 gdalnumeric array 格式\n
    参数：\n
    img - (PIL.Image)输入图片\n
    返回值：\n
    
    """  
    array = gdalnumeric.fromstring(img.tobytes(),'b')
    array.shape = img.im.size[1], img.im.size[0]
    return array
  
def arrayToImage(a):
    """ 
    Converts a gdalnumeric array to a 
    Python Imaging Library Image.
    """  
    i = Image.frombytes('L',(a.shape[1],a.shape[0]), (a.astype('b')).tobytes())
    return i  
  
def world2Pixel(geoMatrix, x, y):
    """ 
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate 
    the pixel location of a geospatial coordinate 
    """  
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    pixel = int((x - ulX) / xDist)
    line = int((ulY - y) / xDist)
    return (pixel, line)
  
#  
#  EDIT: this is basically an overloaded  
#  version of the gdal_array.OpenArray passing in xoff, yoff explicitly  
#  so we can pass these params off to CopyDatasetInfo  
#  
def OpenArray( array, prototype_ds = None, xoff=0, yoff=0):
    ds = gdal_array.OpenArray( gdalnumeric.GetArrayFilename(array) )  
  
    if ds is not None and prototype_ds is not None:
        if type(prototype_ds).__name__ == 'str':
            prototype_ds = gdal_array.OpenArray( prototype_ds)
        if prototype_ds is not None:
            gdalnumeric.CopyDatasetInfo( prototype_ds, ds, xoff=xoff, yoff=yoff)
    return ds
  
def histogram(a, bins=range(0,256)):
    """ 
    Histogram function for multi-dimensional array. 
    a = array 
    bins = range of numbers to match 
    """  
    fa = a.flat
    n = gdalnumeric.searchsorted(gdalnumeric.sort(fa), bins)
    n = gdalnumeric.concatenate([n, [len(fa)]])
    hist = n[1:]-n[:-1]
    return hist

def stretch(a):
    """ 
    Performs a histogram stretch on a gdalnumeric array image. 
    """  
    hist = histogram(a)
    im = arrayToImage(a)
    lut = []
    for b in range(0, len(hist), 256):
        # step size
        step = reduce(operator.add, hist[b:b+256]) / 255
        # create equalization lookup table
        n = 0
        for i in range(256):
            lut.append(n / step)
            n = n + hist[i+b]
        im = im.point(lut)
    return imageToArray(im)
  
def main( shapefile_path, raster_path, fileName):
    # 读取栅格影像路径
    srcArray = gdalnumeric.LoadFile(raster_path)
    # 读取栅格据
    srcImage = gdal.Open(raster_path)
    geoTrans = srcImage.GetGeoTransform()
    # 读取矢量图形数据路径
    shapef = ogr.Open(shapefile_path)
    lyr = shapef.GetLayer( os.path.split( os.path.splitext( shapefile_path )[0])[1])
    poly = lyr.GetNextFeature()
    # 矢量图形坐标换算
    minX, maxX, minY, maxY = lyr.GetExtent()
    ulX, ulY = world2Pixel(geoTrans, minX, maxY)
    lrX, lrY = world2Pixel(geoTrans, maxX, minY)
    # 计算新生成图像大小
    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)
    clip = srcArray[:, ulY:lrY, ulX:lrX]
    xoffset = ulX
    yoffset = ulY
    print("Xoffset, Yoffset = ( %f, %f )" % (xoffset, yoffset))
    # 创建geomatrix
    geoTrans = list(geoTrans)
    geoTrans[0] = minX
    geoTrans[3] = maxY
    # 创建一张黑白遮罩图像，将矢量点集映射到像素上
    points = []
    pixels = []
    geom = poly.GetGeometryRef()
    pts = geom.GetGeometryRef(0)
    for p in range(pts.GetPointCount()):
      points.append((pts.GetX(p), pts.GetY(p)))
    for p in points:
      pixels.append(world2Pixel(geoTrans, p[0], p[1]))
    rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
    rasterize = ImageDraw.Draw(rasterPoly)
    rasterize.polygon(pixels, 0)
    mask = imageToArray(rasterPoly)
    # 裁剪遮罩
    clip = gdalnumeric.choose(mask, (clip, 0)).astype(gdalnumeric.int16)
    clip = clip.astype(gdalnumeric.int16)
    #加载GTiff驱动，存储结果为tiff图像
    gtiffDriver = gdal.GetDriverByName('GTiff')
    if gtiffDriver is None:
        raise ValueError("Can't load GeoTiff Driver")
    print(type(clip))
    gdalnumeric.SaveArray(clip, fileName, format="GTiff")
    print("裁剪完毕")
    gdal.ErrorReset()
  
  
if __name__ == '__main__':  
    shapefile_path = r'Assets/kaifeng.shp'
    # raster_path = r'Assets/B4.tif'
    main(shapefile_path, r'Assets/B3.tif', "Assets/kfb3.tif")
    main(shapefile_path, r'Assets/B4.tif', "Assets/kfb4.tif")
    main(shapefile_path, r'Assets/B5.tif', "Assets/kfb5.tif")
    main(shapefile_path, r'Assets/B6.tif', "Assets/kfb6.tif")