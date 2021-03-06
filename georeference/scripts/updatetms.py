'''
Created on Jul 21, 2014

@author: mendt
'''
import argparse
import os
import shutil
import subprocess
import sys
from PIL import Image

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
BASE_PATH_PARENT = os.path.abspath(os.path.join(BASE_PATH, os.pardir))
sys.path.insert(0, BASE_PATH)
sys.path.append(BASE_PATH_PARENT)

TMP_DIR = '/tmp'

def buildTMSCache(source_path, target_dir, srs = 4314):
    """ Functions calculates a Tile Map Service cache for a given georeferenced source file.

    :param str: source_path Path to georeference image file
    :param str: target_dir Path to the directory where the cache should be placed
    :param int: srs SRS of the given source file
    :return: str  """
    print('------------------------------------------------------------------')
    file_name, file_extension = os.path.splitext(os.path.basename(source_path))
    
    # check if target dir extist
    tms_target_dir = os.path.join(target_dir, file_name)
    if os.path.exists(tms_target_dir):
        print('Remove old tsm cache directory ...')
        shutil.rmtree(tms_target_dir)
                  
    os.makedirs(tms_target_dir)
    command = 'gdal2tiles.py -z 1-15 -w none -s EPSG:%s %s %s'%(srs, source_path, tms_target_dir)

    print('Execute - %s'%command)
    subprocess.call(command, shell = True)
    print('------------------------------------------------------------------')

    return tms_target_dir

def calculateCompressedTMS(inputImage, targetDir, epsgCode):
    """ The following functions computes a compressed version of TMS cache.

    :type str: inputImage
    :type str: targetDir
    :type int: epsgCode
    :return:
    """
    print('Calculate tms cache ...')
    tmpCacheDir = buildTMSCache(inputImage, TMP_DIR, epsgCode)

    print('Compress cache ...')
    compressTMSCache(tmpCacheDir)

    # check if the target dir exits, if yes remove it
    if os.path.exists(os.path.join(targetDir, os.path.basename(inputImage).split('.')[0])):
        print('Remove old target dir ...')
        shutil.rmtree(os.path.join(targetDir, os.path.basename(inputImage).split('.')[0]))

    print('Copy compressed cache to target dir ...')
    subprocess.call(['rsync', '-rI', tmpCacheDir, targetDir])

    print('Clean up ...')
    shutil.rmtree(tmpCacheDir)

def compressTMSCache(path):
    """ Functions runs a pngs compression on the given tms cache.

    :type str: path
    :return:
    """
    print 'Run png compression on %s ...' % path
    pngs = getImageFilesInDirTree(path, 'png')
    for png in pngs:
        Image.open(png).convert('RGBA').quantize(method=2).save(png)

def getImageFilesInDirTree(baseDir, imageExtension):
    """ Functions iteratore of the baseDir and the subdirectory tree and and returns a list of image files paths found
        in the directory structure.

        :type str: baseDir
        :type str: imageExtension
        :return: list<str>
    """
    def getAllImagesFromFilesList(baseDir, files, imageExtension):
        """ Functions returns all images within a files list.

            :type str: baseDir
            :type list<str>: files
            :type str: imageExtension
            :return: list<str>
        """
        pngs = []
        for file in files:
            if os.path.splitext(file)[1][1:] == str(imageExtension).lower():
                pngs.append(os.path.join(baseDir, file))
        return pngs

    images = []
    for root, dirs, files in os.walk(baseDir):
        # first check that directory doesn't start with "."
        dirName = str(root).rsplit('/')[-1]
        # only look in directories which doesn't start with "."
        if dirName[0] is not '.':
            images.extend(getAllImagesFromFilesList(root, files, imageExtension))
    return images



""" Main """    
if __name__ == '__main__':
    script_name = 'updatetms.py'
    parser = argparse.ArgumentParser(description = 'Scripts tooks a input dir and processes for all tiff images within the \
        directory a TMS cache in the output dir.', prog = 'Script %s'%script_name)
    parser.add_argument('--target_dir', help='Directory where the TMS directories should be placed.')
    parser.add_argument('--source_dir', help='Source directory') 
    arguments = parser.parse_args()
    
    # updateTMSCache(arguments.source_dir, arguments.target_dir,logger)
