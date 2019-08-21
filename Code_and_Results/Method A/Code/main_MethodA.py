# Author: Vineet Jacob Kuruvilla
# Date: 04/06/2018
# Modified: 05/06/2018

# import cv2
from vmtk import vmtkscripts
import numpy as np
import matplotlib.pyplot as plt
from skimage import morphology
from skimage.filters import threshold_otsu
import vtk

def display_slices(path, fname, ncol = 5, for_every = 3):
    img = np.load(pdata_path+fname)

    images_num = int(img.shape[2]/for_every)

    if ((img.shape[2] % for_every) != 0):
        nrow = int(images_num/ncol) + 1
    else:
        nrow = int(images_num/ncol)

    fig, ax = plt.subplots(nrow, ncol, figsize=[50,50])

    r = -1
    cnt = 0
    for i in range(0, img.shape[2], for_every):

        if cnt % ncol == 0:
            r += 1

        ax[r, int(cnt % ncol)].set_title('Slice %d' % i)
        ax[r, int(cnt % ncol)].imshow(img[:, :, i], cmap='gray')
        ax[r, int(cnt % ncol)].axis('off')

        cnt += 1

    plt.show()


pdata_path = "/home/vjk/PycharmProjects/smtech/processed/"


# Read vtkImageData
imageReader = vmtkscripts.vmtkImageReader()
imageReader.InputFileName = 'data/img.vti'
imageReader.Execute()

# Convert vtkImageData to numpy dictionary
imageNumpyAdaptor = vmtkscripts.vmtkImageToNumpy()
imageNumpyAdaptor.Image = imageReader.Image
imageNumpyAdaptor.Execute()
numpyImage = imageNumpyAdaptor.ArrayDict

slices = numpyImage['PointData']['ImageScalars']
np.save(pdata_path+'MethodA_full_images.npy', slices)
display_slices(pdata_path, 'MethodA_full_images.npy', 5, 10)

# Thresholding of Slices. Threshold value was determined manually
slices_cpy = np.copy(slices)
slices_cpy[slices_cpy < 450] = 0
slices_cpy[slices_cpy > 1000] = 0
slices_cpy[slices_cpy > 0] = 1
np.save(pdata_path+'MethodA_thresh_images.npy', slices_cpy)
display_slices(pdata_path, 'MethodA_thresh_images.npy', 5, 10)

# Erode and dilate to remove small specks and recover from important boundaries
s_erodilate = []
for i in range(slices_cpy.shape[2]):
    s = slices_cpy[:, :, i]
    eroded = morphology.erosion(s, np.ones([3,3]))
    dilation = morphology.dilation(eroded, np.ones([3,3]))
    s_erodilate.append(dilation)

stack_dilate = np.stack(s_erodilate,axis=2)
np.save(pdata_path+'MethodA_dilated_thresh_images.npy', stack_dilate)
display_slices(pdata_path, 'MethodA_dilated_thresh_images.npy', 5, 10)


# Convert Numpy array to vtkImageData
numpyImage['PointData']['ImageScalars'] = stack_dilate

imageVmtkAdaptor = vmtkscripts.vmtkNumpyToImage()
imageVmtkAdaptor.ArrayDict = numpyImage
imageVmtkAdaptor.Execute()

# Write vtkImageData to vti file
writer = vtk.vtkXMLImageDataWriter()
writer.SetFileName('myimg_MethodA.vti')
if vtk.VTK_MAJOR_VERSION <= 5:
    writer.SetInputConnection(imageVmtkAdaptor.Image.GetProducerPort())
else:
    writer.SetInputData(imageVmtkAdaptor.Image)
writer.Write()

print imageVmtkAdaptor.Image

# Read vtkImageData
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName('myimg_MethodA.vti')
reader.Update()

# Surface extraction using Marching Cube algorithm
dmc = vtk.vtkMarchingCubes()
dmc.SetInputConnection(reader.GetOutputPort())
dmc.GenerateValues(1, 1, 1)
dmc.Update()

# Write to a STL file
writer = vtk.vtkSTLWriter()
writer.SetInputConnection(dmc.GetOutputPort())
writer.SetFileTypeToBinary()
writer.SetFileName("STL_MethodA.stl")
writer.Write()

