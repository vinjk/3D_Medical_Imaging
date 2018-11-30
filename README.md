# Segmentation of Blood Vessels from 3D Medical Image

## Objective

To segment the desired blood vessels from a 3D medical image (in vti format) using thresholding and to export it as STL or VTP file
Segment one of the two blood vessels by allowing the user to select one or more seed point. The segmentation should be done without any explicit input for the threshold value from the user

## Summary

For objective 1, three different approaches were explored and implemented:
A) Numpy & Manual Thresholding- The vti file was read and image was converted to numpy dictionary and processed. The image threshold to extract the blood vessels were given as input by the user. The threshold value was decided based on values in the blood vessel region observed on multiple slices.
B) VTK & Manual Thresholding- In this method, the data was processed as a vtkImageData itself. There was no conversion to numpy or any outside format. The thresholding was also done in VTK using vtkImageThreshold. Here again, the threshold value was decided based on observations from image slices.
C) Numpy & Threshold value based on seed point- In this method, the image was processed as numpy array as described in method (a). But the threshold value was not set by the user. Here, the user is shown the first slice (or any slice) in the medical image and is asked to make a single click in the blood vessel region. The threshold value is computed based on the intensity values in a small ROI around that point and is then used to threshold the image. This seed point is used not just for discovering the threshold value but is also used in the next bonus task to segment one of the blood vessel.

In all three method, the segmented blood vessels are converted to a PolyData and then exported as STL file, which can be viewed using ParaView software. In all three method, some noise/extraneous elements are visible in the STL data. Least noise was observed in Method C. Based on performance and ease of use, Method C is considered the best among the three methods. The bonus task was built upon the this method. 
A fourth method was also looked into. It is a modification of Method C. It is mentioned in Additional Study section, point 5.

For objective 2, only one method was implemented. For this task one or more seed points can be given by user and this is then used to segment one of the two blood vessels present in the 3D medical data. I have used the vtkImageThresholdConnectivity for this task. This method flood fills an image based on the upper and lower threshold values using the seed points to stick to a continuous region. In my implementation, I have used 6 seed points but one well placed seed point (for example, somewhere in the midsection of the volume) can give the exact result. The program was able to accurate segment the blood vessel and discard all other parts in the 3D volume.

## Dependencies
1. Python 2.7
2. Numpy 1.11
3. scikit-image 0.13.0
4. matplotlib 1.5.1
5. vmtk 1.4.0
6. vtk 8.5.1

Dependencies 1-4 was installed from Anaconda Distribution. The installation file and instruction can be found here.
Dependencies 5 -6 were also installed from Anaconda Distribution. The instructions can be obtained here.

Operating System used was Ubuntu 16.04

IDE used was PyCharm Community Edition 2018.1

The results were viewed using ParaView 64-bit version 5.0.1
