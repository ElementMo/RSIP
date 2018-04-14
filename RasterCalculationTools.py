# -*- coding: utf-8 -*-  
"""
本项目运行环境为\n
python3.5.4-amd64,\n
opencv_python-3.4.0-cp35-win_amd64,\n
gdal-2.2.4-cp35-win-amd64\n

@author 王墨白
@date 2018-04-15 
@brief 遥感栅格图像计算库
"""

from osgeo import gdal_array as ga
import numpy as np
from PIL import Image, ImageEnhance
import cv2

def loadBand(fileName):
    """
    读取波段图像，并进行灰度处理为单通道图像\n
    参数：\n
    fileName - (str)文件名 包含路径\n
    返回值：\n
    (ndarray)灰度图像数组
    """
    band = cv2.imread(fileName)
    if(len(band.shape)==3):
        band = cv2.cvtColor(band, cv2.COLOR_BGR2GRAY)
    # band = cv2.resize(band, (800,800))
    return band

def saveGTiff(ndarray, fileName):
    """
    ndarray保存为GTiff格式图片\n
    参数：\n
    ndarray - (ndarray)图片\n
    fileName - (str)文件名\n
    返回值：\n
    None
    """
    ga.SaveArray(ndarray, fileName, format="GTiff")
    return

def fixAnomoly(ndarray):
    """
    修复数组运算中的NaN与Infinite错误\n
    将NDVI中的NaN与Infinite设置为-1\n
    参数：\n
    ndarray - 图像数组\n
    返回值：\n
    (float64)(ndarray)处理过异常值的图像数组
    """
    # ndarray = ga.numpy.nan_to_num(ndarray, copy=False)
    where_are_nan = np.isnan(ndarray)
    where_are_inf = np.isinf(ndarray)
    ndarray[where_are_nan] = -1.0
    ndarray[where_are_inf] = -1.0
    return ndarray
    
def stretchEnhance(ndarray):
    """
    图像颜色范围拉伸函数\n
    将NDVI处理后的[-1,1]区间的值映射为[0,255]\n
    返回值：\n
    (Float64)(ndarray)
    """
    return ((1.0+ndarray)*0.5)*255.0

def PILEnhance(ndarray, color, contrast):
    """
    使用PIL库进行图像色度和对比度增强\n
    参数:\n
    ndarray - 数组形式图像\n
    color - (int)色度增强指数\n
    contrast - (int)对比度增强\n
    返回值：\n
    (ndarray)图片数组
    """
    PILImage = Image.fromarray(ndarray)

    enh_col = ImageEnhance.Color(PILImage)  
    image_colored = enh_col.enhance(color)
    enh_con = ImageEnhance.Contrast(image_colored)  
    image_contrasted = enh_con.enhance(contrast)  
    
    outndarray = np.array(image_contrasted)
    return outndarray


def float64ToInt(ndarray):
    return ndarray.astype(int)



def binaryPixels(ndarray, color):
    """
    计算二值化后图像目标区域像素点数\n
    参数：\n
    ndarray - (ndarray)二值化图像的数组\n
    color - (int)需要提取面积的颜色(0 或 255)\n
    返回值：\n
    (int)像素个数\n
    下一步可用：\n
    pixelToArea() 将像素转换为面积
    """
    area = 0
    info = ndarray.shape
    # print(height, width)
    for i in range(info[0]):
        for j in range(info[1]):
            if (ndarray[i, j] == int(color)):
                area += 1
    return area

def imgToBinary(img, threshold):
    """
    将cv2读取到的图像(ndarray格式)处理成二值图像\n
    参数：\n
    img - (ndarray)格式的图像(可彩可灰)\n
    threshold - (int)二值化的阈值\n
    返回值：\n
    (ndarray)二值化处理后的图像\n
    下一步可用：\n
    binaryPixels() 计算二值化目标像素点个数
    """
    if(len(img.shape)==3):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ret, bi = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    return bi

def bandMerge(red, green, blue, fileName):
    """
    以RGB形式融合波段，并写入文件\n
    参数：\n
    red - 存储为红通道\n
    green - 存储为绿通道\n
    blue - 存储为蓝通道\n
    fileName - 文件名(str)\n
    返回值：\n
    (ndarray[[[0..0]]])merged - 通道融合后的影像;
    """
    merged = cv2.merge([blue, green, red])
    cv2.imwrite(fileName, merged)
    return merged

def pixelToArea(binaryPixels):
    """
    将像素点数转化为面积(m^2), 根据landsat8数据可知分辨率为30米\n
    参数：\n
    binaryPixels - 可直接传入binaryPixels函数的返回值,并与imgToBinary连用\n
    返回值：\n
    (int)面积(单位：平方米)\n
    用法：\n
    Area = pixelToArea(binaryPixels(imgToBinary(img, 51), 0))\n
    Area = pixelToArea(binaryPixels(imgToBinary(img, 125), 255))\n
    """
    return binaryPixels*900