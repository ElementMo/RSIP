from osgeo import gdal_array as ga
import RasterCalculationTools as rc
import numpy as np
from PIL import Image
import cv2

###################    读取TIF文件，并转换为灰度图   ####################


# blue = rc.loadBand("Assets/kfb2.tif")  # Band2
green = rc.loadBand("Assets/kfb3.tif")  # Band3
red = rc.loadBand("Assets/kfb4.tif")  # Band4
nir = rc.loadBand("Assets/kfb5.tif")  # Band5
swir1 = rc.loadBand("Assets/kfb6.tif")  # Band6
# swir2 = rc.loadBand("Assets/kfb7.tif")  # Band7


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

# ndvi = ndvi.astype(int)
# ndbi = ndbi.astype(int)
# ndwi = ndwi.astype(int)

cv2.imwrite("img/NDVI.TIF", ndvi)
cv2.imwrite("img/NDBI.TIF", ndbi)
cv2.imwrite("img/NDWI.TIF", ndwi)



mask = cv2.imread("Assets/kfb3.tif")
maskArea = rc.pixelToArea(rc.binaryPixels(rc.imgToBinary(mask, 1), 255))
print("KaiFeng Area: "+str(maskArea/1000000)+" km^2")
maskedOutArea = rc.pixelToArea(rc.binaryPixels(rc.imgToBinary(mask, 1), 0))


NDBIArea = rc.pixelToArea(rc.binaryPixels(rc.imgToBinary(ndbi, 200), 0)) - maskedOutArea
print("Building Area: "+str(NDBIArea/1000000)+" km^2")

NDWIArea = rc.pixelToArea(rc.binaryPixels(rc.imgToBinary(ndwi, 200), 0)) - maskedOutArea
print("Water Area: "+str(NDWIArea/1000000)+" km^2")

cv2.imshow("BI",rc.imgToBinary(ndbi, 160))
cv2.imshow("WI",rc.imgToBinary(ndwi, 160))
cv2.waitKey()