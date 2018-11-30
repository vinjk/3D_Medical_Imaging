# Author: Vineet Jacob Kuruvilla
# Date: 04/06/2018
# Modified: 05/06/2018

import vtk

# Read vtkImageData
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName('data/img.vti')
reader.Update()

#Thresholding using VTK
threshold = vtk.vtkImageThreshold ()
threshold.SetInputConnection(reader.GetOutputPort())
threshold.ThresholdBetween(450, 1000)  # remove all soft tissue
threshold.ReplaceInOn()
threshold.SetInValue(1)  # set all values below 490 and above 1000 to 0
threshold.ReplaceOutOn()
threshold.SetOutValue(0)  # set all values between 490 and 1000 to 1
threshold.Update()

print threshold

# Write vtkImageData to vti file to visualise slice-wise
# writer = vtk.vtkXMLImageDataWriter()
# writer.SetFileName('MethodB_threshold.vti')
# if vtk.VTK_MAJOR_VERSION <= 5:
#     writer.SetInputConnection(threshold.GetOutput())
# else:
#     writer.SetInputData(threshold.GetOutput())
# writer.Write()

# Extracting surface using Marching Cube algorithm
dmc = vtk.vtkMarchingCubes()
dmc.SetInputConnection(threshold.GetOutputPort())
dmc.GenerateValues(1, 1, 1)
dmc.Update()

writer = vtk.vtkSTLWriter()
writer.SetInputConnection(dmc.GetOutputPort())
writer.SetFileTypeToBinary()
writer.SetFileName("STL_MethodB.stl")
writer.Write()

