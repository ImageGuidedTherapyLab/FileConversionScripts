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

import sys
# python itk bindings
import itk
# used scipy to write matlab files
import scipy.io as scipyio

if len(sys.argv) < 1:
    print('Usage: ' + sys.argv[0] + ' DicomDirectory')
    sys.exit(1)

#
# Reads a 3D image in with signed short (16bits/pixel) pixel type
# and save it
#
ImageType  = itk.Image.SS3

nameGenerator = itk.GDCMSeriesFileNames.New()
nameGenerator.SetUseSeriesDetails( True ) 
nameGenerator.AddSeriesRestriction("0008|0021") 

nameGenerator.SetDirectory( sys.argv[1]) 
seriesUID = nameGenerator.GetSeriesUIDs() 

for uid in seriesUID:
   # get file names
   fileNames = nameGenerator.GetFileNames( uid ) 
   print "reading:", uid
   # read
   reader = itk.ImageSeriesReader[ImageType].New()
   dicomIO = itk.GDCMImageIO.New()
   reader.SetImageIO( dicomIO )
   reader.SetFileNames( fileNames )
   reader.Update( )
   # get dictionary info
   dictionary = dicomIO.GetMetaDataDictionary()
   PrintAllKeysInDictionary = False
   if(PrintAllKeysInDictionary): 
     for key in dictionary.GetKeys():
       print key, dictionary[key]
   # parse header SeriesDescription for t1 t2 flair
   WriteThisUID = False
   SeriesDescription = dictionary['0008|103e']
   StudyDate         = dictionary['0008|0020']
   SeriesDate        = dictionary['0008|0021']
   AcquisitionDate   = dictionary['0008|0022']
   ContentDate       = dictionary['0008|0023']
   StudyTime         = dictionary['0008|0030']
   for searchheader in ['T1','T2','FLAIR']:
    if(SeriesDescription.upper().find(searchheader) != -1):
      WriteThisUID = True
      print "writing:", SeriesDescription
   # write
   if(WriteThisUID):
     # tag file name with dicom header info to id
     filename = "%d_%d_%s" %(StudyDate,StudyTime,SeriesDescription.replace(' ',''))
     # instantiate writer
     writer = itk.ImageFileWriter[ImageType].New()
     writer.SetInput( reader.GetOutput() )
     #TODO set vtk array name to the series description for ID
     #vtkvectorarray.SetName(SeriesDescription)
     writer.SetFileName( "%s.mha" % filename );
     writer.Update() 
     #TODO get pixel buffer and save as MATLAB :)
     #scipyio.savemat("%s.mat" % (filename), {'ImageData':Data,'HeaderInfo':dictionary} )
     scipyio.savemat("%s.mat" % (filename), {'HeaderInfo':dictionary.GetKeys()} )
