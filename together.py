from PIL import Image
import os
import py360convert
import cv2
import time


def 横向拼接(imagesList):
    # 检查图像高度是否一致
    # 方法是生成高度列表并和另一个内部元素完全是和第一个一样的列表相比较
    heights = list(map(lambda image: image.size[1], imagesList))
    isHeightEqual = [heights[0] for x in range(len(imagesList))] == heights
    if not isHeightEqual:
        raise Exception('高度不匹配')

    widths = tuple(map(lambda image: image.size[0], imagesList))
    # 新建画布
    imageBig = Image.new(mode='RGB', size = (sum(widths), heights[0]))
    # 开始逐个粘贴
    for i in range(len(imagesList)):
        image  = imagesList[i]
        imageBig.paste(image, (sum(widths[:i]), 0, sum(widths[:i+1]), image.size[1]))
    return imageBig

def 竖向拼接(imagesList):
    # 检查图像宽度是否一致
    widths = list(map(lambda image: image.size[0], imagesList))
    isWidthsEqual = [widths[0] for x in range(len(imagesList))] == widths
    if not isWidthsEqual:
        raise Exception('宽度不匹配')

    heights = tuple(map(lambda image: image.size[1], imagesList))
    # 新建画布
    imageBig = Image.new( mode='RGB', size = (widths[0], sum(heights)) )
    # 开始逐个粘贴
    for i in range(len(imagesList)):
        image  = imagesList[i]
        imageBig.paste(image, (0, sum(heights[:i]), image.size[0], sum(heights[:i+1])))

    return imageBig

# matrixD 矩阵维度元组
# flatImagesList 用于拼接的扁平化的图像列表
def 矩阵拼接(matrixD, flatImagesList):
    if matrixD[0] * matrixD[1] != len(flatImagesList):
        raise Exception("给定矩阵尺寸与得到的图像个数不符。")

    imagesLines = list()
    # 拼接所有行
    for lineIndex in range(matrixD[0]):
        imagesLines.append(横向拼接(flatImagesList[lineIndex * matrixD[1] : (lineIndex + 1) * matrixD[1]]))
    
    # 竖向拼接
    return 竖向拼接(imagesLines)

def 拼接所有(path,title,base_url):
    import os
    import math
    fileNames = os.listdir(path)

    # 按文件名整理各个面的文件名到一个字典中
    sixFaceDict = {}
    for fileName in fileNames:
        sixFaceDict[fileName[3]] = sixFaceDict.get(fileName[3], list())
        sixFaceDict[fileName[3]].append(path + fileName)

    # 按路径全部替换成image
    for face in sixFaceDict:
        for i in range(len(sixFaceDict[face])):
            sixFaceDict[face][i] = Image.open(sixFaceDict[face][i]) 
    
    # 拼接
    for face in sixFaceDict:
        linesNum = int(math.sqrt(len(sixFaceDict[face])))
        sixFaceDict[face] = 矩阵拼接((linesNum, linesNum), sixFaceDict[face])

    # 输出宽度
    print("pano width should be: {}".format(
        sixFaceDict['f'].size[0] +
        sixFaceDict['b'].size[0] +
        sixFaceDict['l'].size[0] +
        sixFaceDict['r'].size[0]
    ))

    # 保存
    for face in sixFaceDict:
        sixFaceDict[face].save('result/'+ face + '.jpg')
    string = ""
    while string != 'y':
        string = input("输入y后按回车键开始拼接")
    a(title,base_url)
def  a(title,base_url):
    
    #合并为全景图
    print("开始合并全景图")
    time_start = time.time()

    target_size_w = 13672
    target_size_h = target_size_w // 2
    
    cube_dice0 = cv2.imread(
        os.path.join('result/f.jpg'))
    cube_dice1 = cv2.imread(
        os.path.join('result/r.jpg'))
    cube_dice2 = cv2.imread(
        os.path.join('result/b.jpg'))
    cube_dice3 = cv2.imread(
        os.path.join('result/l.jpg'))
    cube_dice4 = cv2.imread(
        os.path.join('result/u.jpg'))
    cube_dice5 = cv2.imread(
        os.path.join('result/d.jpg'))
    cube_dice1 = cv2.flip(cube_dice1, 1)
    cube_dice2 = cv2.flip(cube_dice2, 1)
    cube_dice4 = cv2.flip(cube_dice4, 0)

    res = py360convert.c2e(
        [cube_dice0, cube_dice1, cube_dice2, cube_dice3, cube_dice4,
            cube_dice5], target_size_h, target_size_w, cube_format='list')
    cv2.imwrite(os.path.join('panorama.jpg'),res)
    time_end = time.time()

    print("合并完成,用时",str(int(time_end - time_start))+"s")