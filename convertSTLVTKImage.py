import vtk
import numpy
# echo vtk version info
print "using vtk version", vtk.vtkVersion.GetVTKVersion()
import os

##################################################################
##################################################################
class STLImageHelper:
  """ Class for output of Image from STL ...  """
  def __init__(self,InputImageFileName ):
    print " class constructor called \n\n"
    # damage paramters

    # open stl and extract VOI for a reference
    stlReader = vtk.vtkSTLReader() 
    stlReader.SetFileName( InputImageFileName ) 
    stlReader.Update()
    self.stlData = stlReader.GetOutput()
    stlpoints = self.stlData.GetPoints() 

    # VOI Origin should be at the lower bound
    VOIBounds                 = self.stlData.GetBounds()
    self.origin               = (VOIBounds[0]-1.,VOIBounds[2]-1.,VOIBounds[4]-1.)
    self.dimensions           = (256,256,100,1)
    self.spacing              = ((VOIBounds[1]+1. - self.origin[0])/self.dimensions[0],
                                 (VOIBounds[3]+1. - self.origin[1])/self.dimensions[1],
                                 (VOIBounds[5]+1. - self.origin[2])/self.dimensions[2])
    numpyimagesize = self.dimensions[0]*self.dimensions[1]*self.dimensions[2]
    # store as double precision
    self.ImageFile = numpy.zeros( numpyimagesize, dtype=numpy.float32 )
    for ipoint in range(stlpoints.GetNumberOfPoints() ):
        CurrentPoint = stlpoints.GetPoint(ipoint)
        XIndex       = int( ( CurrentPoint[0]-self.origin[0])/ self.spacing[0] ) 
        YIndex       = int( ( CurrentPoint[1]-self.origin[1])/ self.spacing[1] ) 
        ZIndex       = int( ( CurrentPoint[2]-self.origin[2])/ self.spacing[2] ) 
        CurrentIndex =   XIndex   \
                       + YIndex * self.dimensions[0] \
                       + ZIndex * self.dimensions[0] * self.dimensions[1]
        self.ImageFile[CurrentIndex ] = 1.

  # write a numpy data to disk in vtk format
  def ConvertNumpyVTKImage(self,NumpyImageData):
    # Create initial image
    dim = self.dimensions
    # imports raw data and stores it.
    dataImporter = vtk.vtkImageImport()
    # array is converted to a string of chars and imported.
    data_string = NumpyImageData.tostring()
    dataImporter.CopyImportVoidPointer(data_string, len(data_string))
    # The type of the newly imported data is set to unsigned char (uint8)
    dataImporter.SetDataScalarTypeToFloat()
    # Because the data that is imported only contains an intensity value (it isnt RGB-coded or someting similar), the importer
    # must be told this is the case.
    dataImporter.SetNumberOfScalarComponents(dim[3])
    # The following two functions describe how the data is stored and the dimensions of the array it is stored in. For this
    # simple case, all axes are of length 75 and begins with the first element. For other data, this is probably not the case.
    # I have to admit however, that I honestly dont know the difference between SetDataExtent() and SetWholeExtent() although
    # VTK complains if not both are used.
    dataImporter.SetDataExtent( 0, dim[0]-1, 0, dim[1]-1, 0, dim[2]-1)
    dataImporter.SetWholeExtent(0, dim[0]-1, 0, dim[1]-1, 0, dim[2]-1)
    dataImporter.SetDataSpacing( self.spacing )
    dataImporter.SetDataOrigin(  self.origin )
    dataImporter.Update()
    return dataImporter.GetOutput()

 


# setup command line parser to control execution
from optparse import OptionParser
parser = OptionParser()
parser.add_option( "--file_name",
                  action="store", dest="file_name", default=None,
                  help="converting/this/file.stl to converting/this/file.vtk", metavar = "FILE")
(options, args) = parser.parse_args()
if (options.file_name):
  OutputFileName = options.file_name.split('.').pop(0) + '.vtk'
  stlHelper = STLImageHelper(options.file_name)
  vtkImage  = stlHelper.ConvertNumpyVTKImage(stlHelper.ImageFile) 
  
  ##print "resampling"
  ##vtkResample = vtk.vtkCompositeDataProbeFilter()
  ##vtkResample.SetSource( stlHelper.stlData )
  ##vtkResample.SetInput(  vtkImage  )
  ##vtkResample.Update()
  ##print vtkResample.GetOutput()

  vtkImageDataWriter = vtk.vtkDataSetWriter()
  vtkImageDataWriter.SetFileTypeToBinary()
  print "writing ", OutputFileName 
  vtkImageDataWriter.SetFileName( OutputFileName )
  ##vtkImageDataWriter.SetInput(vtkResample.GetOutput())
  vtkImageDataWriter.SetInput(vtkImage  )
  vtkImageDataWriter.Update()

else:
  parser.print_help()
  print options
