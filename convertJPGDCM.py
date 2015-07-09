import vtk
# echo vtk version info
print "using vtk version", vtk.vtkVersion.GetVTKVersion()
import os

####################################################################
def ConvertJPGDirectory(work_dir,output_dir):
  # list the directory
  directoryList = os.listdir(work_dir)
  # build the list of vtk and vti files
  files = filter(lambda x:os.path.isfile("%s/%s" % (work_dir,x) ),directoryList)
  jpgFiles = filter(lambda x: x.split(".").pop() == "jpg" ,files)
  filenames = jpgFiles 
  # loop over list of files and convert to matlab
  for idlist, fileID in enumerate( filenames):
    CurrentInFileName  = "%s/%s" % (work_dir  ,fileID)
    CurrentOutFileName = "%s/%s" % (output_dir,fileID.replace("jpg","dcm"))
    convertcmd = "c3d -mcs %s -type uchar -omc %s" % (CurrentInFileName, CurrentOutFileName )
    print convertcmd 
    os.system(convertcmd )
    swapheaderdmc = "DicomImageReadChangeHeaderWrite %s  %s '0008|0090' wolfpac" % (CurrentOutFileName, CurrentOutFileName)
    print swapheaderdmc 
    print "%d of %d:read %s wrote %s" % (idlist,len(filenames),CurrentInFileName,CurrentOutFileName)

  
# setup command line parser to control execution
from optparse import OptionParser
parser = OptionParser()
parser.add_option( "--file_dir",
                  action="store", dest="file_dir", default=None,
                  help="convert .jpg files in this directory to .dcm files", metavar = "DIR")
parser.add_option( "--output_dir",
                  action="store", dest="output_dir", default=None,
                  help="output files to this directory", metavar = "DIR")
(options, args) = parser.parse_args()
if (options.file_dir):
  # default output directory to input directory is not set
  OutputDirectory = options.file_dir
  if (options.output_dir):
    OutputDirectory = options.output_dir
    os.system("mkdir -p %s" % OutputDirectory )
  ConvertJPGDirectory(options.file_dir,OutputDirectory)
else:
  parser.print_help()
  print options
