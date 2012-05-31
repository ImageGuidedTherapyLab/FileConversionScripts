# import vtk and numpy
import vtk, numpy
def CreateVTKImage(imageDimensions,imageSpacing,imageOrigin):
  # imports raw data and stores it.
  dataImporter = vtk.vtkImageImport()
  # array is converted to a string of chars and imported.
  # numpy array stored as ROW MAJOR
  # MUST write out in COLUMN MAJOR format to be the same as VTK
  data_string = numpy.zeros(imageDimensions,dtype=numpy.float,order='F').tostring(order='F')
  dataImporter.CopyImportVoidPointer(data_string, len(data_string))
  # The type of the newly imported data is set to unsigned char (uint8)
  dataImporter.SetDataScalarTypeToDouble()
  # Because the data that is imported only contains an intensity value (it isnt RGB-coded or someting similar), the importer
  # must be told this is the case.
  dataImporter.SetNumberOfScalarComponents(1)
  # The following two functions describe how the data is stored and the dimensions of the array it is stored in. For this
  # simple case, all axes are of length 75 and begins with the first element. For other data, this is probably not the case.
  # I have to admit however, that I honestly dont know the difference between SetDataExtent() and SetWholeExtent() although
  # VTK complains if not both are used.
  dataImporter.SetDataExtent( 0, imageDimensions[0]-1, 0, imageDimensions[1]-1, 0, imageDimensions[2]-1)
  dataImporter.SetWholeExtent(0, imageDimensions[0]-1, 0, imageDimensions[1]-1, 0, imageDimensions[2]-1)
  dataImporter.SetDataSpacing( imageSpacing )
  dataImporter.SetDataOrigin(  imageOrigin  )
  dataImporter.SetScalarArrayName(  "scalars" )
  dataImporter.Update()
  return dataImporter.GetOutput()
####################################################################
def ProjectImagingMesh(ini_file):
  import vtk.util.numpy_support as vtkNumPy 
  import ConfigParser
  import scipy.io as scipyio
  # echo vtk version info
  print "using vtk version", vtk.vtkVersion.GetVTKVersion()
  # read config file
  config = ConfigParser.ConfigParser()
  config.add_section("imaging") 
  config.add_section("fem") 
  config.set("imaging","listoffset","[0]") 
  config.read(ini_file)
 
  # get work directory
  work_dir = config.get('fem','work_dir')

  # FIXME  notice that order of operations is IMPORTANT
  # FIXME   translation followed by rotation will give different results
  # FIXME   than rotation followed by translation
  # FIXME  Translate -> RotateZ -> RotateY -> RotateX -> Scale seems to be the order of paraview
  RotateX    = float(config.get('fem','rotatex'))
  RotateY    = float(config.get('fem','rotatey'))
  RotateZ    = float(config.get('fem','rotatez'))
  Translate  = eval(config.get('fem','translate'))
  Scale      = eval(config.get('fem','scale'))
  print "rotate", RotateX , RotateY , RotateZ ,"translate", Translate, "scale", Scale 
  
  # read imaging data geometry that will be used to project FEM data onto
  dimensions = eval(config.get('imaging','dimensions'))
  spacing    = eval(config.get('imaging','spacing'))
  origin     = eval(config.get('imaging','origin'))
  print spacing, origin, dimensions
  templateImage = CreateVTKImage(dimensions,spacing,origin)
  # write template image for position verification
  vtkTemplateWriter = vtk.vtkDataSetWriter()
  vtkTemplateWriter.SetFileName( "%s/imageTemplate.vtk" % work_dir )
  vtkTemplateWriter.SetInput( templateImage )
  vtkTemplateWriter.Update()

  #setup to interpolate at 5 points across axial dimension 
  TransformList = []
  listoffset = eval(config.get('imaging','listoffset'))
  naverage   = len(listoffset)
  try:
    subdistance = spacing[2] / (naverage-1)
  except ZeroDivisionError: 
    subdistance = 0.0 # default is not to offset
  print "listoffset",listoffset, "subspacing distance = ", subdistance
  for idtransform in listoffset: 
    AffineTransform = vtk.vtkTransform()
    AffineTransform.Translate( Translate[0],Translate[1],
                               Translate[2] + subdistance*idtransform )
    AffineTransform.RotateZ( RotateZ )
    AffineTransform.RotateY( RotateY )
    AffineTransform.RotateX( RotateX )
    AffineTransform.Scale(   Scale   )
    TransformList.append( AffineTransform )
    #laserTip         =  AffineTransform.TransformPoint(  laserTip )
    #laserOrientation =  AffineTransform.TransformVector( laserOrientation )

  # Interpolate FEM onto imaging data structures
  vtkExodusIIReader = vtk.vtkExodusIIReader()
  #vtkExodusIIReader.SetFileName( "%s/fem_stats.e" % work_dir )
  #vtkExodusIIReader.SetPointResultArrayStatus("Mean0",1)
  #vtkExodusIIReader.SetPointResultArrayStatus("StdDev0",1)
  #Timesteps  = 120
  meshFileList = eval(config.get('fem','mesh_files'))
  print meshFileList 
  for mesh_filename in meshFileList:
	  vtkExodusIIReader.SetFileName( "%s/%s" % (work_dir,mesh_filename) )
	  #vtkExodusIIReader.SetPointResultArrayStatus("Vard0Mean",1)
	  #vtkExodusIIReader.SetPointResultArrayStatus("Vard0Kurt",1)
	  vtkExodusIIReader.Update()	  
	  numberofresultarrays = vtkExodusIIReader.GetNumberOfPointResultArrays()
	  print numberofresultarrays
	  for resultarrayindex in range(numberofresultarrays):
		resultarrayname = vtkExodusIIReader.GetPointResultArrayName(resultarrayindex)
		vtkExodusIIReader.SetPointResultArrayStatus( "%s" % (resultarrayname),1)
		print resultarrayname
	  vtkExodusIIReader.Update()
	  ntime  = vtkExodusIIReader.GetNumberOfTimeSteps()
	  #print ntime
          #for timeID in range(69,70):
	  for timeID in range(ntime):
	    vtkExodusIIReader.SetTimeStep(timeID) 
	    vtkExodusIIReader.Update()
	    
	    # reflect
	    vtkReflectX = vtk.vtkReflectionFilter()
	    vtkReflectX.SetPlaneToXMin()
	    vtkReflectX.SetInput( vtkExodusIIReader.GetOutput() )
	    vtkReflectX.Update()

	    # reflect
	    vtkReflectY = vtk.vtkReflectionFilter()
	    vtkReflectY.SetPlaneToYMax()
	    vtkReflectY.SetInput( vtkReflectX.GetOutput() )
	    vtkReflectY.Update()

	    # apply the average of the transform
	    mean_array = numpy.zeros(dimensions[0]*dimensions[1]*dimensions[2])
	    std_array  = numpy.zeros(dimensions[0]*dimensions[1]*dimensions[2])
	    for affineFEMTranform in TransformList:
	      # get homogenius 4x4 matrix  of the form
	      #               A | b
	      #    matrix =   -----
	      #               0 | 1
	      #   
	      matrix = affineFEMTranform.GetConcatenatedTransform(0).GetMatrix()
	      #print matrix 
	      RotationMatrix = [[matrix.GetElement(0,0),matrix.GetElement(0,1),matrix.GetElement(0,2)],
				[matrix.GetElement(1,0),matrix.GetElement(1,1),matrix.GetElement(1,2)],
				[matrix.GetElement(2,0),matrix.GetElement(2,1),matrix.GetElement(2,2)]]
	      Translation =     [matrix.GetElement(0,3),matrix.GetElement(1,3),matrix.GetElement(2,3)] 
	      #print RotationMatrix 
	      print Translation 
	      TransformedFEMMesh = None
	      if vtkReflectY.GetOutput().IsA("vtkMultiBlockDataSet"):
		AppendBlocks = vtk.vtkAppendFilter()
		iter = vtkReflectY.GetOutput().NewIterator()
		iter.UnRegister(None)
		iter.InitTraversal()
		# loop over blocks...
		while not iter.IsDoneWithTraversal():
		    curInput = iter.GetCurrentDataObject()
		    vtkTransformFEMMesh = vtk.vtkTransformFilter()
		    vtkTransformFEMMesh.SetTransform( affineFEMTranform )
		    vtkTransformFEMMesh.SetInput( curInput )
		    vtkTransformFEMMesh.Update()
		    AppendBlocks.AddInput( vtkTransformFEMMesh.GetOutput() ) 
		    AppendBlocks.Update( ) 
		    iter.GoToNextItem();
		TransformedFEMMesh = AppendBlocks.GetOutput() 
	      else: 
		vtkTransformFEMMesh = vtk.vtkTransformFilter()
		vtkTransformFEMMesh.SetTransform( affineFEMTranform )
		vtkTransformFEMMesh.SetInput( vtkReflectY.GetOutput() )
		vtkTransformFEMMesh.Update()
		TransformedFEMMesh = vtkTransformFEMMesh.GetOutput() 

	      # reuse ShiftScale Geometry
	      vtkResample = vtk.vtkCompositeDataProbeFilter()
	      vtkResample.SetInput( templateImage )
	      vtkResample.SetSource( TransformedFEMMesh ) 
	      vtkResample.Update()
	      fem_point_data= vtkResample.GetOutput().GetPointData() 
	      #meantmp =  vtkNumPy.vtk_to_numpy(fem_point_data.GetArray('Vard0Mean')) 
	      #print meantmp.max()
	      #mean_array = mean_array + vtkNumPy.vtk_to_numpy(fem_point_data.GetArray('Vard0Mean')) 
	      #std_array  = std_array  + vtkNumPy.vtk_to_numpy(fem_point_data.GetArray('Vard0Kurt')) 
	      #print fem_array 
	      #print type(fem_array )

	    # average
	    #mean_array = mean_array/naverage
	    #print mean_array.max()
	    #std_array  = std_array /naverage 

	    # write numpy to disk in matlab
	    #scipyio.savemat("%s/modelstats.navg%d.%04d.mat" % (work_dir,naverage,timeID), {'spacing':spacing, 'origin':origin,'Vard0Mean':mean_array,'Vard0Kurt':std_array })

	  
	    # write output
	    print "writing ", timeID, mesh_filename, work_dir
	    vtkStatsWriter = vtk.vtkDataSetWriter()
	    vtkStatsWriter.SetFileTypeToBinary()
	    vtkStatsWriter.SetFileName("%s/modelstats.navg%d.%s.%04d.vtk"%(work_dir,naverage,mesh_filename,timeID))
	    vtkStatsWriter.SetInput(vtkResample.GetOutput())
	    vtkStatsWriter.Update()

# setup command line parser to control execution
from optparse import OptionParser
parser = OptionParser()
parser.add_option( "--ini_file",
                  action="store", dest="ini_file", default=None,
                  help="parse ini file to convert exodus FILE to matlab/imaging", metavar = "FILE")
(options, args) = parser.parse_args()
if (options.ini_file):
  ProjectImagingMesh(options.ini_file)
else:
  parser.print_help()
  print options
