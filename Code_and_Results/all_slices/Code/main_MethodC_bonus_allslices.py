# See-Mode Technologies
# Author: Vineet Jacob Kuruvilla
# Date: 04/06/2018
# Modified: 06/06/2018

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
imageReader = read_vtifile('data/img1.vti')

# Convert vtkImageData to numpy dictionary
numpyImage = vtkImage2Numpy(imageReader)

# print numpyImage
# print "Origin: ", np.array(numpyImage['Origin'])
# print "Spacing: ", np.array(numpyImage['Spacing'])

# Extract Image data from the numpy array dict
slices = numpyImage['PointData']['ImageScalars']
save_numpyarray(pdata_path, 'Bonus_full_images', slices)
# display_slices(pdata_path, 'Bonus_full_images.npy', 5, 10)

# Make a copy of the slices
slices_cpy = np.copy(slices)

# Display first slice for roi selection using a single mouse click
# This point will also be used as seed point to extract desired volume
# The user can enter the number of seed points required
seed_num = int(raw_input("Enter number of seed points: "))

# First slice for seed point selection
pos_seed = []
idx_seed = []
nbd_width = 6
roi = np.zeros((2*nbd_width, 2*nbd_width))
print type(roi)
if seed_num == 1:
    plt.imshow(slices_cpy[:, :, int(slices_cpy.shape[2]/2)], cmap='gray')
    plt.title("Select a point in the blood vessel region with a mouse click")
    x = plt.ginput(show_clicks=True)
    plt.show()

    idx_seed.append([x[0][1], x[0][0], int(slices_cpy.shape[2]/2)])
    # Compute position coordinates from voxel index, Origin coordinates and Voxel spacing
    pos = np.array(numpyImage['Origin'])+np.array(idx_seed[0])*np.array(numpyImage['Spacing'])
    pos_seed.append(pos)

    # Define ROI based on selected point
    roi = slices_cpy[:, :, int(slices_cpy.shape[2]/2)][x[0][1]-nbd_width:x[0][1]+nbd_width, x[0][0]-nbd_width:x[0][0]+nbd_width]
else:
    step_size = int(slices.shape[2]/seed_num)
    cnt = 0
    for i in range(seed_num):
        slice_num = i * step_size
        plt.imshow(slices[:, :, slice_num], cmap='gray')
        plt.title("Select point #%d in the blood vessel region with a mouse click" %(cnt+1))
        x = plt.ginput(show_clicks=True)
        plt.show()

        print "Clicked point: ", x
        x = np.array(x, dtype='int')

        idx_seed.append([x[0][1], x[0][0], slice_num])
        pos = np.array(numpyImage['Origin'])+np.array(idx_seed[cnt])*np.array(numpyImage['Spacing'])
        pos_seed.append(pos)

        roi += slices_cpy[:, :, slice_num][x[0][1] - nbd_width:x[0][1] + nbd_width, x[0][0] - nbd_width:x[0][0] + nbd_width]

        cnt += 1

# Compute mean and standard deviation of intensity in the ROI
thresh = np.mean(roi/seed_num)
stdev = np.std(roi/seed_num)
# print "Mean: ", thresh
# print "Std Dev: ", stdev

# mean+stdev was taken as threshold as mean tends to underestimate the value.
# Hence upper limit of the distribution was used.
slices_cpy[slices_cpy < thresh-stdev] = 0
slices_cpy[slices_cpy > thresh-stdev] = 1

# Erosion and Dilation of the threshold image to remove small specks from the image
s_erodilate = []
for i in range(slices_cpy.shape[2]):
    s = slices_cpy[:, :, i]
    eroded = morphology.erosion(s, np.ones([1,1]))
    dilation = morphology.dilation(eroded, np.ones([3,3]))
    s_erodilate.append(dilation)

stack_dilate = np.stack(s_erodilate,axis=2)

save_numpyarray(pdata_path, 'thresh_Bonus', stack_dilate)
display_slices(pdata_path, 'thresh_Bonus.npy', 5, 10)

# Convert Numpy array to vtkImageData
numpyImage['PointData']['ImageScalars'] = slices_cpy

imageVmtkAdaptor = vmtkscripts.vmtkNumpyToImage()
imageVmtkAdaptor.ArrayDict = numpyImage
imageVmtkAdaptor.Execute()

# Write vtkImageData to vti file
writer = vtk.vtkXMLImageDataWriter()
writer.SetFileName('myimg_Bonus.vti')
if vtk.VTK_MAJOR_VERSION <= 5:
    writer.SetInputConnection(imageVmtkAdaptor.Image.GetProducerPort())
else:
    writer.SetInputData(imageVmtkAdaptor.Image)
writer.Write()


# Read vtkImageData
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName('myimg_Bonus.vti')
reader.Update()

# Surface extraction using Marching Cube algorithm
vmc = surfextract(reader)

# Write to a STL file
saveSTL(vmc, "Bonus_img")

# Region Growing - 2

# Print idx and seed position coordinates
print "idx: ", idx_seed
print "seed position: ",pos_seed

# Seed input
seed = vtk.vtkPoints()
for i in range(len(pos_seed)):
    ix = pos_seed[i][0]
    iy = pos_seed[i][1]
    iz = pos_seed[i][2]
    seed.InsertNextPoint([ix, iy, iz])

# Image Threshold Connectivity
connectivityFilter = vtk.vtkImageThresholdConnectivity()
connectivityFilter.SetInputConnection(reader.GetOutputPort())
connectivityFilter.SetSeedPoints(seed)
connectivityFilter.ThresholdByUpper(1)
connectivityFilter.ReplaceInOn()
connectivityFilter.SetInValue(1)
connectivityFilter.ReplaceOutOn()
connectivityFilter.SetOutValue(0)
connectivityFilter.Update()

# Surface extraction using Marching Cube algorithm
vmc2 = surfextract(connectivityFilter)

# Write output as STL file
saveSTL(vmc2, "bonus_connectivity_imgthresh")

