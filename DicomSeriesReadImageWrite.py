#==========================================================================
#
#   Copyright Insight Software Consortium
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0.txt
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#==========================================================================*/

#
#  Example on the use of Dicom Reader 
#

import os
import sys
import subprocess
## parser
import ConfigParser
## python itk bindings
import itk
# python vtk bindings
import vtk
import vtk.util.numpy_support as vtkNumPy 
import numpy
# used scipy to write matlab files
import scipy.io as scipyio
# write tar files
import tarfile

# define image type
ImageType  = itk.Image.SS3

####################################################################
def ConvertVTKMatlab(input_filename,output_filename,headerinfo):
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
  # notice the row/column major orientation
  # SCRGP2$ python
  # Enthought Python Distribution -- www.enthought.com
  # Version: 7.3-1 (64-bit)
  # 
  # Python 2.7.3 |EPD 7.3-1 (64-bit)| (default, Apr 11 2012, 17:52:16)
  # [GCC 4.1.2 20080704 (Red Hat 4.1.2-44)] on linux2
  # Type "credits", "demo" or "enthought" for more information.
  # >>> import numpy
  # >>> import scipy.io as scipyio
  # >>> numpytest = numpy.arange(30).reshape(2,3,5)
  # >>> numpytest
  # array([[[ 0,  1,  2,  3,  4],
  #         [ 5,  6,  7,  8,  9],
  #         [10, 11, 12, 13, 14]],
  # 
  #        [[15, 16, 17, 18, 19],
  #         [20, 21, 22, 23, 24],
  #         [25, 26, 27, 28, 29]]])
  # >>> scipyio.savemat( 'test.mat', {'numpytest':numpytest})
  # /opt/apps/EPD/epd-7.3-1-rh5-x86_64/lib/python2.7/site-packages/scipy/io/matlab/mio.py:266: FutureWarning: Using oned_as default value ('column') This will change to 'row' in future versions
  #   oned_as=oned_as)
  #SCRGP2$ matlab -nodesktop
  #Warning: No display specified.  You will not be able to display graphics on the screen.
  #Warning: No window system found.  Java option 'MWT' ignored
  #
  #                                                                                                                            < M A T L A B (R) >
  #                                                                                                                  Copyright 1984-2010 The MathWorks, Inc.
  #                                                                                                               Version 7.12.0.635 (R2011a) 64-bit (glnxa64)
  #                                                                                                                              March 18, 2011
  #
  #
  #  To get started, type one of these: helpwin, helpdesk, or demo.
  #  For product information, visit www.mathworks.com.
  #
  #>> load test.mat
  #>> numpytest
  #
  #numpytest(:,:,1) =
  #
  #                    0                    5                   10
  #                   15                   20                   25
  #
  #
  #numpytest(:,:,2) =
  #
  #                    1                    6                   11
  #                   16                   21                   26
  #
  #
  #numpytest(:,:,3) =
  #
  #                    2                    7                   12
  #                   17                   22                   27
  #
  #
  #numpytest(:,:,4) =
  #
  #                    3                    8                   13
  #                   18                   23                   28
  #
  #
  #numpytest(:,:,5) =
  #
  #                    4                    9                   14
  #                   19                   24                   29
  #>> numpytest(:)
  #
  #ans =
  #
  #                    0
  #                   15
  #                    5
  #                   20
  #                   10
  #                   25
  #                    1
  #                   16
  #                    6
  #                   21
  #                   11
  #                   26
  #                    2
  #                   17
  #                    7
  #                   22
  #                   12
  #                   27
  #                    3
  #                   18
  #                    8
  #                   23
  #                   13
  #                   28
  #                    4
  #                   19
  #                    9
  #                   24
  #                   14
  #                   29
  #save matlab file
  #  indexing is painful.... reshape to dimensions and transpose 2d dimensions only
  scipyio.savemat( output_filename, {'spacing':spacing, 'origin':origin,'image':image_data.reshape(dimensions,order='F').transpose(1,0,2),'HeaderInfo':headerinfo})

####################################################################

def ParseDicomDirectoryAndWrite(DicomDirectory,ProcessDirectory):
   print "working on: ",DicomDirectory  
   nameGenerator = itk.GDCMSeriesFileNames.New()
   nameGenerator.SetUseSeriesDetails( True ) 
   # os.walk will recursively look through directories
   nameGenerator.RecursiveOff() 
   nameGenerator.AddSeriesRestriction("0008|0021") 
   
   nameGenerator.SetDirectory( DicomDirectory ) 
   seriesUID = nameGenerator.GetSeriesUIDs() 
   for uid in seriesUID:
      # get file names
      fileNames = nameGenerator.GetFileNames( uid ) 

      try:
        # read
        reader = itk.ImageSeriesReader[ImageType].New()
        dicomIO = itk.GDCMImageIO.New()
        reader.SetImageIO( dicomIO )
        reader.SetFileNames( fileNames )
        reader.Update( )
        # get dictionary info
        dictionary = dicomIO.GetMetaDataDictionary()
        # FIXME: SCIPY bug will not write dict
        # DicomDictionary = dict([ (key, dictionary[key]) for key in dictionary.GetKeys() ])
        DicomDictionary = [ key+' : '+dictionary[key] for key in dictionary.GetKeys() ]
        # TODO: add labels to tags
        # itk.GDCMImageIO.GetLabelFromTag(['0008|1030',label])
        # parse header SeriesDescription for t1 t2 flair
        WriteThisUID = False
        try: 
          StudyDescription  = dictionary['0008|1030']
        except:
          StudyDescription  = 'UnknownStudy'
        try: 
          SeriesDescription = dictionary['0008|103e']
        except:
          SeriesDescription = 'UnknownSeriesDescription'
        try: 
          StudyDate         = dictionary['0008|0020']
        except:
          StudyDate         = 'UnknownStudyDate'
        try: 
          SeriesDate        = dictionary['0008|0021']
        except:
          SeriesDate        = 'UnknownSeriesDate'
        try: 
          AcquisitionDate   = dictionary['0008|0022']
        except:
          AcquisitionDate   = 'UnknownAcquisitionDate'
        try: 
          ContentDate       = dictionary['0008|0023']
        except:
          ContentDate       = 'UnknownContent'
        try: 
          StudyTime         = dictionary['0008|0030']
        except:
          StudyTime         = 'UnknownStudyTime'
        try: 
          Modality          = dictionary['0008|0060']
        except:
          Modality          = 'UnknownModality'
        try: 
          PatientID         = dictionary['0010|0020']
        except:
          PatientID         = 'UnknownPatient'
        try: 
          SeriesNumber      = dictionary['0020|0011']
        except:
          SeriesNumber      = 'UnknownSeriesNumber'


        WriteThisUID = True
        # TODO: do we need to filter on anything ? 
        ## for searchheader in ['T1','T2','FLAIR']:
        ##  if(SeriesDescription.upper().find(searchheader) != -1):
        ##    WriteThisUID = True
        # write
        if(WriteThisUID):
          ## str.isalnum is used to remove special characters:
          ## 
          ## S.isalnum() -> bool
          ## 
          ## Return True if all characters in S are alphanumeric
          ## and there is at least one character in S, False otherwise.
          ##
          ##
          ## >>> string = "Special $#! characters   spaces 888323"
          ## >>> ''.join(e for e in string if e.isalnum())
          ## 'Specialcharactersspaces888323'

          # tag file name with dicom header info to id
          outfilename = "%s/StudyDate%sSeriesNumber%s_%s_%sPatientID%s_%s" %(ProcessDirectory,StudyDate,\
                 ''.join(e for e in SeriesNumber      if e.isalnum()),\
                 ''.join(e for e in SeriesDescription if e.isalnum()),\
                 ''.join(e for e in StudyDescription  if e.isalnum()),\
                 ''.join(e for e in PatientID         if e.isalnum()),\
                                    Modality )
          print "writing:", outfilename
          # instantiate writer
          vtkwriter = itk.ImageFileWriter[ImageType].New()
          vtkwriter.SetInput( reader.GetOutput() )
          #TODO set vtk array name to the series description for ID
          #vtkvectorarray.SetName(SeriesDescription)
          vtkwriter.SetFileName( "%s.vtk" % outfilename );
          vtkwriter.Update() 
          hdrwriter = itk.ImageFileWriter[ImageType].New()
          hdrwriter.SetInput( reader.GetOutput() )
          #TODO set vtk array name to the series description for ID
          #vtkvectorarray.SetName(SeriesDescription)
          hdrwriter.SetFileName( "%s.hdr" % outfilename );
          hdrwriter.Update() 
          #get pixel buffer and save as MATLAB :)
          ConvertVTKMatlab( "%s.vtk" % (outfilename),"%s.mat" % (outfilename),DicomDictionary )
          #write tarfile with original dicom
          with tarfile.open("%s.tar" % (outfilename), "w") as tar:
              for name in fileNames:
                  tar.add(name,arcname=name.split("/").pop())

      except Exception as inst:
        print "error reading: ", uid 
        print inst

# setup command line parser to control execution
from optparse import OptionParser
parser = OptionParser()
parser.add_option( "--dicom_dir",
                  action="store", dest="dicom_dir", default=None,
                  help="recursively convert .vtk and .vti files in this directory to .mat files", metavar = "DIR")
parser.add_option( "--server",
                  action="store", dest="server", default=None,
                  help="setup server with ini file", metavar = "INI FILE")
(options, args) = parser.parse_args()
if (options.dicom_dir):
  for dirname, dirnames, filenames in os.walk(options.dicom_dir):
    # print path to all subdirectories first.
    if (len(dirnames)):
        for subdirname in dirnames:
            PathToSubDir = os.path.join(dirname, subdirname)
            ParseDicomDirectoryAndWrite(PathToSubDir,PathToSubDir)
        ## # print path to all filenames.
        ## for filename in filenames:
        ##     print os.path.join(dirname, filename)
    # no directories to recurse
    else: 
        ParseDicomDirectoryAndWrite(dirname,dirname)
elif (options.server):
  # configure server
  config = ConfigParser.ConfigParser()
  config.read(options.server) 
  storescpEXE = config.get('dcmtk','storescp')
  AETitle     = config.get('dcmtk','aetitle')
  outputdir   = config.get('dcmtk','outputdir')
  ProcessDir  = config.get('dcmtk','processdir')
  portnumber  = config.getint('dcmtk','port')
  timeout     = config.getint('dcmtk','tos')
  # build server command
  listenerCMD = "%s -xs -fe .dcm -sp  -aet %s --output-directory %s  --exec-on-reception 'echo #f 1>&2' --exec-on-eostudy 'echo  #p' --eostudy-timeout %d %d" % (storescpEXE,AETitle,outputdir,timeout,portnumber) 
  print "starting..."
  print listenerCMD 
  # setup server
  listenerProcess = subprocess.Popen(listenerCMD,shell=True,stdout=subprocess.PIPE )
  while ( listenerProcess.poll() == None ):
          PathToSubDir = listenerProcess.stdout.readline().strip('\n')
          PathToOuputProcessDir = "%s/%s" %(ProcessDir,PathToSubDir.split("/").pop())
          os.mkdir(PathToOuputProcessDir)
          ParseDicomDirectoryAndWrite(PathToSubDir,PathToOuputProcessDir)
else:
  parser.print_help()
  print options
