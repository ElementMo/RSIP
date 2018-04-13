from osgeo import gdal_array as ga
import RasterCalculationTools as rc
import numpy as np
from PIL import Image
import cv2

###################    读取TIF文件，并转换为灰度图   ####################

mask = cv2.imread("Assets/Mask.tif")
maskArea = rc.pixelToArea(rc.binaryPixels(rc.imgToBinary(mask, 100), 255)) #遮罩区域面积
maskedOutArea = rc.pixelToArea(rc.binaryPixels(rc.imgToBinary(mask, 100), 0))  #遮罩外部面积

blue = cv2.imread("Assets/SHP2Raster2.tif")  # Band2
blue = cv2.cvtColor(blue, cv2.COLOR_BGR2GRAY)
green = cv2.imread("Assets/SHP2Raster3.tif")  # Band3
green = cv2.cvtColor(green, cv2.COLOR_BGR2GRAY)
red = cv2.imread("Assets/SHP2Raster4.tif")  # Band4
red = cv2.cvtColor(red, cv2.COLOR_BGR2GRAY)
nir = cv2.imread("Assets/SHP2Raster5.tif")  # Band5
nir = cv2.cvtColor(nir, cv2.COLOR_BGR2GRAY)
swir1 = cv2.imread("Assets/SHP2Raster6.tif")  # Band6
swir1 = cv2.cvtColor(swir1, cv2.COLOR_BGR2GRAY)
swir2 = cv2.imread("Assets/SHP2Raster7.tif")  # Band7
swir2 = cv2.cvtColor(swir2, cv2.COLOR_BGR2GRAY)


ga.numpy.seterr(all="ignore")

ndvi = ((nir-red)*1.0) / ((nir+red)*1.0)
rc.fixAnomoly(ndvi)
ndbi = ((swir1-nir)*1.0) / ((swir1+nir)*1.0)
rc.fixAnomoly(ndbi)
ndwi = ((green-nir)*1.0) / ((green+nir)*1.0)
rc.fixAnomoly(ndwi)

ndvi = rc.stretchEnhance(ndvi)
ndbi = rc.stretchEnhance(ndbi)
ndwi = rc.stretchEnhance(ndwi)


# intndvi = np.around(ndvi, decimals=0)
intndvi = ndvi.astype(int)
intndbi = ndbi.astype(int)
intndwi = ndwi.astype(int)

cv2.imwrite("img/NDVI.TIF", intndvi)
cv2.imwrite("img/NDBI.TIF", intndbi)
cv2.imwrite("img/NDWI.TIF", intndwi)