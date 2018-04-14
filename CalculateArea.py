import RasterCalculationTools as rc
import cv2

mask = cv2.imread("Assets/Mask.tif")
maskArea = rc.pixelToArea(rc.binaryPixels(rc.imgToBinary(mask, 100), 255))
print("KaiFeng Area: "+str(maskArea/1000000)+" km^2")
maskedOutArea = rc.pixelToArea(rc.binaryPixels(rc.imgToBinary(mask, 100), 0))


ndbi = cv2.imread("img/NDBI.TIF")
NDBIArea = rc.pixelToArea(rc.binaryPixels(rc.imgToBinary(ndbi, 200), 0)) - maskedOutArea
print("Building Area: "+str(NDBIArea/1000000)+" km^2")

ndwi = cv2.imread("img/NDWI.TIF")
NDWIArea = rc.pixelToArea(rc.binaryPixels(rc.imgToBinary(ndwi, 200), 0)) - maskedOutArea
print("Water Area: "+str(NDWIArea/1000000)+" km^2")

cv2.imwrite("TestNDBIbina.tif", rc.imgToBinary(ndbi, 200))
cv2.imwrite("TestNDWIbina.tif", rc.imgToBinary(ndwi, 200))