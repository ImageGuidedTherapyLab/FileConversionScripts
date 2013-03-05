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

for dirname, dirnames, filenames in os.walk(sys.argv[1]):
    # print path to all subdirectories first.
    for subdirname in dirnames:
        PathToSubDir = os.path.join(dirname, subdirname)
        print "working on: ",PathToSubDir  
        nameGenerator = itk.GDCMSeriesFileNames.New()
        nameGenerator.SetUseSeriesDetails( True ) 
        # os.walk will recursively look through directories
        nameGenerator.RecursiveOff() 
        nameGenerator.AddSeriesRestriction("0008|0021") 
        
        nameGenerator.SetDirectory( PathToSubDir ) 
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
               outfilename = "%s_%s_%s_%s" %(PathToSubDir,StudyDate,StudyTime,\
                      ''.join(e for e in SeriesDescription if e.isalnum())
                                      )
               print "writing:", outfilename
               # instantiate writer
               writer = itk.ImageFileWriter[ImageType].New()
               writer.SetInput( reader.GetOutput() )
               #TODO set vtk array name to the series description for ID
               #vtkvectorarray.SetName(SeriesDescription)
               writer.SetFileName( "%s.mha" % outfilename );
               writer.Update() 
               #TODO get pixel buffer and save as MATLAB :)
               #scipyio.savemat("%s.mat" % (outfilename), {'ImageData':Data,'HeaderInfo':dictionary} )
               scipyio.savemat("%s.mat" % (outfilename), {'HeaderInfo':dictionary.GetKeys()} )
           except Exception as inst:
             print "error reading: ", uid 
             print inst

    ## # print path to all filenames.
    ## for filename in filenames:
    ##     print os.path.join(dirname, filename)
