import vtk
# echo vtk version info
print "using vtk version", vtk.vtkVersion.GetVTKVersion()
import os

####################################################################
def ConvertVTKDirectory(work_dir,output_dir):
  # list the directory
  directoryList = os.listdir(work_dir)
  # build the list of vtk and vti files
  files = filter(lambda x:os.path.isfile("%s/%s" % (work_dir,x) ),directoryList)
  vtiFiles = filter(lambda x: x.split(".").pop() == "vti" ,files)
  vtkFiles = filter(lambda x: x.split(".").pop() == "vtk" ,files)
  filenames = vtiFiles + vtkFiles
  # loop over list of files and convert to matlab
  for idlist, fileID in enumerate( filenames):
    CurrentInFileName  = "%s/%s" % (work_dir,fileID)
    CurrentOutFileName = "%s/%s.mat" % (output_dir,fileID.split('.').pop(0),)
    ConvertVTKMatlab( CurrentInFileName , CurrentOutFileName )
    print "%d of %d:read %s wrote %s" % (idlist,len(filenames),CurrentInFileName,CurrentOutFileName)

####################################################################
def ConvertVTKMatlab(input_filename,output_filename):
  import vtk.util.numpy_support as vtkNumPy 
  import numpy
  import scipy.io as scipyio
 
  extension = input_filename.split('.').pop()
  vtkReader = None
  if extension == 'vtk':
    vtkReader = vtk.vtkDataSetReader() 
  elif extension == 'vti':
    vtkReader = vtk.vtkXMLImageDataReader() 
  else:
    raise RuntimeError('unknown file type %s ' % input_filename)
  vtkReader.SetFileName( "%s" % (input_filename) ) 
  vtkReader.Update()
  imageDataVTK = vtkReader.GetOutput()
  dimensions = imageDataVTK.GetDimensions()
  spacing = imageDataVTK.GetSpacing()
  origin  = imageDataVTK.GetOrigin()
  print spacing, origin, dimensions
  #fem.SetImagingDimensions( dimensions ,origin,spacing) 

  image_point_data = imageDataVTK.GetPointData() 
  image_data       = vtkNumPy.vtk_to_numpy( image_point_data.GetArray(0) ) 
  # write numpy to disk in matlab
  scipyio.savemat( output_filename, {'dimensions':dimensions,'spacing':spacing, 'origin':origin,'image':image_data})

  
# setup command line parser to control execution
from optparse import OptionParser
parser = OptionParser()
parser.add_option( "--file_name",
                  action="store", dest="file_name", default=None,
                  help="converting/this/file.vtk to converting/this/file.mat", metavar = "FILE")
parser.add_option( "--file_dir",
                  action="store", dest="file_dir", default=None,
                  help="convert .vtk and .vti files in this directory to .mat files", metavar = "DIR")
parser.add_option( "--output_dir",
                  action="store", dest="output_dir", default=None,
                  help="output files to this directory", metavar = "DIR")
(options, args) = parser.parse_args()
if (options.file_name):
  ConvertVTKMatlab(options.file_name)
elif (options.file_dir):
  # default output directory to input directory is not set
  OutputDirectory = options.file_dir
  if (options.output_dir):
    OutputDirectory = options.output_dir
  ConvertVTKDirectory(options.file_dir,OutputDirectory)
else:
  parser.print_help()
  print options
