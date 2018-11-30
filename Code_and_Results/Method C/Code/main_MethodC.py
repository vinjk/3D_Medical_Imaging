# Author: Vineet Jacob Kuruvilla
# Date: 04/06/2018
# Modified: 05/06/2018

# import cv2
from vmtk import vmtkscripts
import numpy as np
import matplotlib.pyplot as plt
from skimage import morphology
import vtk


def display_slices(path, fname, ncol = 5, for_every = 3):
    img = np.load(path+fname)
    images_num = int(img.shape[2]/for_every)

    # Number of rows in display
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


def read_vtifile(path):
    imageReader = vmtkscripts.vmtkImageReader()
    imageReader.InputFileName = path
    imageReader.Execute()

    return imageReader


def vtkImage2Numpy(imageReader):
    imageNumpyAdaptor = vmtkscripts.vmtkImageToNumpy()
    imageNumpyAdaptor.Image = imageReader.Image
    imageNumpyAdaptor.Execute()
    numpyImage = imageNumpyAdaptor.ArrayDict

    return numpyImage


def save_numpyarray(path, filename, array):
    np.save(path + filename +'.npy', array)


def surfextract(filt):
    vmc = vtk.vtkMarchingCubes()
    vmc.SetInputConnection(filt.GetOutputPort())
    vmc.GenerateValues(1, 1, 1)
    vmc.Update()

    return vmc


def saveSTL(polydata, filename):
    stlWriter2 = vtk.vtkSTLWriter()
    stlWriter2.SetInputConnection(polydata.GetOutputPort())
    stlWriter2.SetFileName(filename+".stl")
    stlWriter2.Write()


pdata_path = "/home/vjk/PycharmProjects/see-mode/smtech/processed/"

# Read vtkImageData
imageReader = read_vtifile('data/img.vti')

# Convert vtkImageData to numpy dictionary
numpyImage = vtkImage2Numpy(imageReader)

# print numpyImage
# print "Origin: ", np.array(numpyImage['Origin'])
# print "Spacing: ", np.array(numpyImage['Spacing'])

# Extract Image data from the numpy array dict
slices = numpyImage['PointData']['ImageScalars']
save_numpyarray(pdata_path, 'full_images', slices)
# display_slices(pdata_path, 'MethodC_full_images.npy', 5, 10)

# Make a copy of the slices
slices_cpy = np.copy(slices)

# Display first slice for roi selection using a single mouse click
# This point will also be used as seed point to extract desired volume
plt.imshow(slices_cpy[:, :, 0], cmap='gray')
plt.title("Select a point in the blood vessel region with a mouse click")
x = plt.ginput(show_clicks=True)
plt.show()

print "Clicked point: ", x
x = np.array(x, dtype='int')

# List for seed points for ImageThresholdConnectivity
pos_seed = []
idx_seed = []
idx_seed.append([x[0][1], x[0][0], 0])
# Compute position coordinates from voxel index, Origin coordinates and Voxel spacing
pos = np.array(numpyImage['Origin'])+np.array(idx_seed[0])*np.array(numpyImage['Spacing'])
pos_seed.append(pos)
# print "position: ", pos

# Define ROI based on selected point
roi = slices_cpy[:, :, 0][x[0][1]-3:x[0][1]+3, x[0][0]-3:x[0][0]+3]

# Compute mean and standard deviation of intensity in the ROI
thresh = np.mean(roi)
stdev = np.std(roi)
# print "Mean: ", thresh
# print "Std Dev: ", stdev

# mean+stdev was taken as threshold as mean tends to underestimate the value.
# Hence upper limit of the distribution was used.
slices_cpy[slices_cpy < thresh+stdev] = 0
slices_cpy[slices_cpy > thresh+stdev] = 1

# Erosion and Dilation of the threshold image to remove small specks from the image
s_erodilate = []
for i in range(slices_cpy.shape[2]):
    s = slices_cpy[:, :, i]
    eroded = morphology.erosion(s, np.ones([1,1]))
    dilation = morphology.dilation(eroded, np.ones([3,3]))
    s_erodilate.append(dilation)

stack_dilate = np.stack(s_erodilate,axis=2)

save_numpyarray(pdata_path, 'MethodC_thresh_images', stack_dilate)
display_slices(pdata_path, 'MethodC_thresh_images.npy', 5, 10)

# Convert Numpy array to vtkImageData
numpyImage['PointData']['ImageScalars'] = slices_cpy

imageVmtkAdaptor = vmtkscripts.vmtkNumpyToImage()
imageVmtkAdaptor.ArrayDict = numpyImage
imageVmtkAdaptor.Execute()

# Write vtkImageData to vti file
writer = vtk.vtkXMLImageDataWriter()
writer.SetFileName('myimg_MethodC.vti')
if vtk.VTK_MAJOR_VERSION <= 5:
    writer.SetInputConnection(imageVmtkAdaptor.Image.GetProducerPort())
else:
    writer.SetInputData(imageVmtkAdaptor.Image)
writer.Write()


# Read vtkImageData
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName('myimg_MethodC.vti')
reader.Update()

# Surface extraction using Marching Cube algorithm
vmc = surfextract(reader)

# Write to a STL file
saveSTL(vmc, "STL_MethodC")

