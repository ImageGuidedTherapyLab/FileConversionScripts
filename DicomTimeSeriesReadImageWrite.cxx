/*=========================================================================
 *
 *  Copyright Insight Software Consortium
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0.txt
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 *=========================================================================*/

//  Software Guide : BeginLatex
//
//  Probably the most common representation of datasets in clinical
//  applications is the one that uses sets of DICOM slices in order to compose
//  3-dimensional images. This is the case for CT, MRI and PET scanners. It is
//  very common therefore for image analysts to have to process volumetric
//  images stored in a set of DICOM files belonging to a
//  common DICOM series.
//
//  The following example illustrates how to use ITK functionalities in order
//  to read a DICOM series into a volume and then save this volume in another
//  file format.
//
//  The example begins by including the appropriate headers. In particular we
//  will need the \doxygen{GDCMImageIO} object in order to have access to the
//  capabilities of the GDCM library for reading DICOM files, and the
//  \doxygen{GDCMSeriesFileNames} object for generating the lists of filenames
//  identifying the slices of a common volumetric dataset.
//
//  \index{itk::ImageSeriesReader!header}
//  \index{itk::GDCMImageIO!header}
//  \index{itk::GDCMSeriesFileNames!header}
//  \index{itk::ImageFileWriter!header}
//
//  Software Guide : EndLatex

// Software Guide : BeginCodeSnippet
#include "itkImage.h"
#include "itkGDCMImageIO.h"
#include "itkGDCMSeriesFileNames.h"
#include "itkImageSeriesReader.h"
#include "itkImageFileWriter.h"
#include "itkMetaDataDictionary.h"
#include "itkComposeImageFilter.h"
#include "itkVectorImage.h"
#include "itkFileTools.h"
#include <stdlib.h>  // atoi
// Software Guide : EndCodeSnippet

#include "itkImageRegionIterator.h"
 
template<typename TImage>
void DeepCopy(typename TImage::Pointer input, typename TImage::Pointer output)
{
  output->SetRegions(input->GetLargestPossibleRegion());
  output->Allocate();
 
  itk::ImageRegionConstIterator<TImage> inputIterator(input, input->GetLargestPossibleRegion());
  itk::ImageRegionIterator<TImage> outputIterator(output, output->GetLargestPossibleRegion());
 
  while(!inputIterator.IsAtEnd())
    {
    outputIterator.Set(inputIterator.Get());
    ++inputIterator;
    ++outputIterator;
    }
}
 


int main( int argc, char* argv[] )
{

  if( argc < 3 )
    {
    std::cerr << "Usage: need itk 4.7.2 " << std::endl;
    std::cerr << argv[0] << " DicomDirectory  outputFileName  [stack split tag]"
              << std::endl;
    return EXIT_FAILURE;
    }

  // output directory
  //itk::FileTools::CreateDirectory( argv[2] );
       
// Software Guide : BeginLatex
//
// We define the pixel type and dimension of the image to be read. In this
// particular case, the dimensionality of the image is 3, and we assume a
// \code{signed short} pixel type that is commonly used for X-Rays CT scanners.
//
// The image orientation information contained in the direction cosines
// of the DICOM header are read in and passed correctly down the image processing
// pipeline.
//
// Software Guide : EndLatex

// Software Guide : BeginCodeSnippet
  typedef signed short    PixelType;
  const unsigned int      Dimension = 3;

  typedef itk::Image< PixelType, Dimension >         ImageType;

  // compose 4d series as vector image
  typedef itk::ComposeImageFilter< ImageType >      VectorImageFilterType;
  typedef itk::VectorImage< PixelType, Dimension >  VectorImageType;
  VectorImageFilterType::Pointer vectorFilter = VectorImageFilterType::New();

// Software Guide : EndCodeSnippet

// Software Guide : BeginLatex
//
// We use the image type for instantiating the type of the series reader and
// for constructing one object of its type.
//
// Software Guide : EndLatex

// Software Guide : BeginCodeSnippet
  typedef itk::ImageSeriesReader< ImageType >        ReaderType;
  ReaderType::Pointer reader = ReaderType::New();
// Software Guide : EndCodeSnippet

// Software Guide : BeginLatex
//
// A GDCMImageIO object is created and connected to the reader. This object is
// the one that is aware of the internal intricacies of the DICOM format.
//
// Software Guide : EndLatex

// Software Guide : BeginCodeSnippet
  typedef itk::GDCMImageIO       ImageIOType;
  ImageIOType::Pointer dicomIO = ImageIOType::New();

  reader->SetImageIO( dicomIO );
// Software Guide : EndCodeSnippet

// Software Guide : BeginLatex
//
// Now we face one of the main challenges of the process of reading a DICOM
// series: to identify from a given directory the set of filenames
// that belong together to the same volumetric image. Fortunately for us, GDCM
// offers functionalities for solving this problem and we just need to invoke
// those functionalities through an ITK class that encapsulates a communication
// with GDCM classes. This ITK object is the GDCMSeriesFileNames. Conveniently,
// we only need to pass to this class the name of the directory where
// the DICOM slices are stored. This is done with the \code{SetDirectory()}
// method. The GDCMSeriesFileNames object will explore the directory and will
// generate a sequence of filenames for DICOM files for one study/series.
// In this example, we also call the \code{SetUseSeriesDetails(true)} function
// that tells the GDCMSeriesFileNames object to use additional DICOM
// information to distinguish unique volumes within the directory.  This is
// useful, for example, if a DICOM device assigns the same SeriesID to
// a scout scan and its 3D volume; by using additional DICOM information
// the scout scan will not be included as part of the 3D volume.  Note that
// \code{SetUseSeriesDetails(true)} must be called prior to calling
// \code{SetDirectory()}. By default \code{SetUseSeriesDetails(true)} will use
// the following DICOM tags to sub-refine a set of files into multiple series:
//
// \begin{description}
// \item[0020 0011] Series Number
// \item[0018 0024] Sequence Name
// \item[0018 0050] Slice Thickness
// \item[0028 0010] Rows
// \item[0028 0011] Columns
// \end{description}
//
// If this is not enough for your specific case you can always add some more
// restrictions using the \code{AddSeriesRestriction()} method. In this example we will use
// the DICOM Tag: 0008 0021 DA 1 Series Date, to sub-refine each series. The format
// for passing the argument is a string containing first the group then the element
// of the DICOM tag, separated by a pipe ($|$) sign.
//
//
// \index{itk::GDCMSeriesFileNames!SetDirectory()}
//
// Software Guide : EndLatex

// Software Guide : BeginCodeSnippet
  typedef itk::GDCMSeriesFileNames NamesGeneratorType;
  NamesGeneratorType::Pointer nameGenerator = NamesGeneratorType::New();

  nameGenerator->SetUseSeriesDetails( true );
  nameGenerator->AddSeriesRestriction("0008|0021" );   // Series Date
  //nameGenerator->AddSeriesRestriction("0020|1041" ); // slice location

  std::string entryId = "0020|0012" ; // acquisition number
  if( argc > 3 ) // change the stack break criteria
    {
    entryId = argv[3];
    }
  std::string labelId;
  if( itk::GDCMImageIO::GetLabelFromTag( entryId , labelId ) )
    {
    std::cout << labelId << " (" << entryId << "): ";
    }
  else
    {
    std::cerr << "Trying to access inexistant DICOM tag." << entryId<< std::endl;
    return EXIT_FAILURE;
    }

  nameGenerator->AddSeriesRestriction(entryId  ); 
  nameGenerator->SetDirectory( argv[1] );
// Software Guide : EndCodeSnippet

  // deep copy image pointers
  std::vector<ImageType::Pointer> imagepointerarray;

  // header info
  std::string ValueEchoTime         ;
  std::string ValueFlipAngle        ;
  std::string ValueRepetitionTime   ;
  std::string FrameIdentifyingDICOMTagName;
  std::string FrameIdentifyingDICOMTagUnits = "ms";
  std::string ValueIdentifyTime ;
  std::map<int,float > TimingArray;


  try
    {
    std::cout << std::endl << "The directory: " << std::endl;
    std::cout << std::endl << argv[1] << std::endl << std::endl;
    std::cout << "Contains the following DICOM Series: ";
    std::cout << std::endl << std::endl;


// Software Guide : BeginLatex
//
// The GDCMSeriesFileNames object first identifies the list of DICOM series
// present in the given directory. We receive that list in a reference
// to a container of strings and then we can do things like print out all
// the series identifiers that the generator had found. Since the process of
// finding the series identifiers can potentially throw exceptions, it is
// wise to put this code inside a \code{try/catch} block.
//
// Software Guide : EndLatex

// Software Guide : BeginCodeSnippet
    typedef std::vector< std::string >    SeriesIdContainer;

    const SeriesIdContainer & seriesUID = nameGenerator->GetSeriesUIDs();

    SeriesIdContainer::const_iterator seriesItr = seriesUID.begin();
    SeriesIdContainer::const_iterator seriesEnd = seriesUID.end();
    int idtime = 0 ;
    while( seriesItr != seriesEnd  )
      {
      std::string seriesIdentifier = seriesItr->c_str();
      std::cout << std::endl << std::endl;
      std::cout << "Now reading series: " << std::endl << std::endl;
      std::cout << seriesIdentifier  << std::endl;
      std::cout << std::endl << std::endl;


// Software Guide : BeginLatex
//
// Given that it is common to find multiple DICOM series in the same directory,
// we must tell the GDCM classes what specific series we want to read. In
// this example we do this by checking first if the user has provided a series
// identifier in the command line arguments. If no series identifier has been
// passed, then we simply use the first series found during the exploration of
// the directory.
//
// Software Guide : EndLatex

// Software Guide : BeginCodeSnippet

// Software Guide : EndCodeSnippet



// Software Guide : BeginLatex
//
// We pass the series identifier to the name generator and ask for all the
// filenames associated to that series. This list is returned in a container of
// strings by the \code{GetFileNames()} method.
//
// \index{itk::GDCMSeriesFileNames!GetFileNames()}
//
// Software Guide : EndLatex

// Software Guide : BeginCodeSnippet
         typedef std::vector< std::string >   FileNamesContainer;
         FileNamesContainer fileNames;
     
         fileNames = nameGenerator->GetFileNames( seriesIdentifier );
// Software Guide : EndCodeSnippet

// Software Guide : BeginLatex
//
//
// The list of filenames can now be passed to the \doxygen{ImageSeriesReader}
// using the \code{SetFileNames()} method.
//
//  \index{itk::ImageSeriesReader!SetFileNames()}
//
// Software Guide : EndLatex

// Software Guide : BeginCodeSnippet
         reader->SetFileNames( fileNames );
// Software Guide : EndCodeSnippet

// Software Guide : BeginLatex
//
// Finally we can trigger the reading process by invoking the \code{Update()}
// method in the reader. This call as usual is placed inside a \code{try/catch}
// block.
//
// Software Guide : EndLatex

// Software Guide : BeginCodeSnippet
         try
           {
           reader->Update();
           }
         catch (itk::ExceptionObject &ex)
           {
           std::cout << "unable to read"<< seriesIdentifier << std::endl;
           std::cout << ex << std::endl;
           ++seriesItr;
           continue;
           //return EXIT_FAILURE;
           }
// Software Guide : EndCodeSnippet
     
     
     typedef itk::MetaDataDictionary   DictionaryType;
     const  DictionaryType & dictionary = dicomIO->GetMetaDataDictionary();
     DictionaryType::ConstIterator tagItr = dictionary.Find( entryId );
     DictionaryType::ConstIterator dictend = dictionary.End();

     if( tagItr == dictend )
       {
       std::cerr << "Tag " << entryId;
       std::cerr << " not found in the DICOM header" << std::endl;
       return EXIT_FAILURE;
       }
// Software Guide : EndCodeSnippet

//
// Since the entry may or may not be of string type we must again use a
// \code{dynamic\_cast} in order to attempt to convert it to a string dictionary
// entry. If the conversion is successful, we can then print out its content.
//
// Software Guide : EndLatex

// Software Guide : BeginCodeSnippet
     typedef itk::MetaDataObject< std::string > MetaDataStringType;
     MetaDataStringType::ConstPointer entryvalue =
       dynamic_cast<const MetaDataStringType *>( tagItr->second.GetPointer() );

     std::ostringstream outputfilename ;
     if( entryvalue )
       {
       std::string tagvalue = entryvalue->GetMetaDataObjectValue();
       idtime = atoi(tagvalue.c_str());
       outputfilename << argv[2] << "/" << std::setfill('0') << std::setw(5) << idtime  << ".nhdr";
       }
     else
       {
       std::cerr << "Entry was not of string type" << std::endl;
       return EXIT_FAILURE;
       }
     std::string outputfile= outputfilename.str();
     
     // find additional meta data
     std::string TagTriggerTime      = "0018|1060";
     std::string TagAcquisitionTime  = "0008|0032";
     std::string TagSeriesTime       = "0008|0031";
     std::string TagRepetitionTime   = "0018|0080";
     std::string TagEchoTime         = "0018|0081";
     std::string TagFlipAngle        = "0018|1314";


     // get dictionary data
     DictionaryType::ConstIterator tagItrTriggerTime      = dictionary.Find( TagTriggerTime     );
     DictionaryType::ConstIterator tagItrAcquisitionTime  = dictionary.Find( TagAcquisitionTime );
     DictionaryType::ConstIterator tagItrSeriesTime       = dictionary.Find( TagSeriesTime      );
     if( tagItrTriggerTime != dictend )
       {
       FrameIdentifyingDICOMTagName = "TriggerTime";
       entryvalue = dynamic_cast<const MetaDataStringType *>( tagItrTriggerTime->second.GetPointer() );
       }
     else if( tagItrAcquisitionTime  != dictend )
       {
       FrameIdentifyingDICOMTagName = "AcquisitionTime";
       entryvalue = dynamic_cast<const MetaDataStringType *>( tagItrAcquisitionTime->second.GetPointer() );
       }
     else if( tagItrSeriesTime       != dictend )
       {
       FrameIdentifyingDICOMTagName = "SeriesTime";
       entryvalue = dynamic_cast<const MetaDataStringType *>( tagItrSeriesTime->second.GetPointer() );
       }
     else 
       {
       std::cerr << " Timing info not found in the DICOM header" << std::endl;
       return EXIT_FAILURE;
       }

     if( entryvalue )
       {
       ValueIdentifyTime   = entryvalue->GetMetaDataObjectValue();
       std::cout << FrameIdentifyingDICOMTagName << " " << ValueIdentifyTime  << std::endl;
       }
     else
       {
       std::cerr << "Entry was not of string type" << std::endl;
       return EXIT_FAILURE;
       }

     // sequence info
     DictionaryType::ConstIterator tagItrRepetitionTime   = dictionary.Find( TagRepetitionTime  );
     DictionaryType::ConstIterator tagItrEchoTime         = dictionary.Find( TagEchoTime        );
     DictionaryType::ConstIterator tagItrFlipAngle        = dictionary.Find( TagFlipAngle       );
     if( tagItrRepetitionTime == dictend )
       {
       std::cerr << TagRepetitionTime << "  not found in the DICOM header" << std::endl;
       return EXIT_FAILURE;
       }
     entryvalue = dynamic_cast<const MetaDataStringType *>( tagItrRepetitionTime->second.GetPointer() );
     if( entryvalue )
       {
       ValueRepetitionTime   = entryvalue->GetMetaDataObjectValue();
       std::cout << TagRepetitionTime  << " " << ValueRepetitionTime   << std::endl;
       }
     else
       {
       std::cerr << "Entry was not of string type" << std::endl;
       return EXIT_FAILURE;
       }

     if( tagItrEchoTime       == dictend )
       {
       std::cerr << TagEchoTime       << "  not found in the DICOM header" << std::endl;
       return EXIT_FAILURE;
       }
     entryvalue = dynamic_cast<const MetaDataStringType *>( tagItrEchoTime->second.GetPointer() );
     if( entryvalue )
       {
       ValueEchoTime   = entryvalue->GetMetaDataObjectValue();
       std::cout << TagEchoTime  << " " << ValueEchoTime   << std::endl;
       }
     else
       {
       std::cerr << "Entry was not of string type" << std::endl;
       return EXIT_FAILURE;
       }


     if( tagItrFlipAngle      == dictend )
       {
       std::cerr << TagFlipAngle      << "  not found in the DICOM header" << std::endl;
       return EXIT_FAILURE;
       }
     entryvalue = dynamic_cast<const MetaDataStringType *>( tagItrFlipAngle->second.GetPointer() );
     if( entryvalue )
       {
       ValueFlipAngle   = entryvalue->GetMetaDataObjectValue();
       std::cout << TagFlipAngle  << " " << ValueFlipAngle   << std::endl;
       }
     else
       {
       std::cerr << "Entry was not of string type" << std::endl;
       return EXIT_FAILURE;
       }

// Software Guide : BeginLatex
// Software Guide : EndCodeSnippet
// Software Guide : BeginLatex
//
// At this point, we have a volumetric image in memory that we can access by
// invoking the \code{GetOutput()} method of the reader.
//
// Software Guide : EndLatex

// Software Guide : BeginLatex
//
// We proceed now to save the volumetric image in another file, as specified by
// the user in the command line arguments of this program. Thanks to the
// ImageIO factory mechanism, only the filename extension is needed to identify
// the file format in this case.
//
// Software Guide : EndLatex

// Software Guide : BeginCodeSnippet
         typedef itk::ImageFileWriter< ImageType > WriterType;
         WriterType::Pointer writer = WriterType::New();

         writer->SetFileName( outputfile );
         writer->SetInput( reader->GetOutput() );
         // Software Guide : EndCodeSnippet
     
         std::cout  << "Writing the image as " << std::endl << std::endl;
         std::cout  << outputfile  << std::endl << std::endl;
     
// Software Guide : BeginLatex
//
// The process of writing the image is initiated by invoking the
// \code{Update()} method of the writer.
//
// Software Guide : EndLatex
     
         try
           {
// Software Guide : BeginCodeSnippet
           //writer->Update();
           reader->Update();

           // append time instance
           ImageType::Pointer imagecopy = ImageType::New();
           DeepCopy<ImageType>(reader->GetOutput() , imagecopy );
         
           // FIXME - use pointer array to hold all image in memory for write
           imagepointerarray.push_back( imagecopy  );
           vectorFilter->SetInput( idtime-1,imagecopy  );
           TimingArray[idtime-1] =  1000. * atof( ValueIdentifyTime.c_str() ); // ms

// Software Guide : EndCodeSnippet
           }
         catch (itk::ExceptionObject &ex)
           {
           std::cout << ex << std::endl;
           return EXIT_FAILURE;
           }
         ++seriesItr;
         }
     
    // write 4d data as vector image
    vectorFilter->Update();
    VectorImageType::Pointer vectorimage = vectorFilter->GetOutput();

    std::ostringstream TimingArrayValues ;
    TimingArrayValues <<  "0.0" ; 
    for ( int iii =1 ; iii< TimingArray.size() ; iii++)
       TimingArrayValues << "," << TimingArray[iii] - TimingArray[0] ; 


    // add key value pairs
    itk::MetaDataDictionary &                       thisDic = vectorimage->GetMetaDataDictionary();
    itk::EncapsulateMetaData< std::string >( thisDic, "MultiVolume.DICOM.EchoTime"               , ValueEchoTime                 );
    itk::EncapsulateMetaData< std::string >( thisDic, "MultiVolume.DICOM.FlipAngle"              , ValueFlipAngle                );
    itk::EncapsulateMetaData< std::string >( thisDic, "MultiVolume.DICOM.RepetitionTime"         , ValueRepetitionTime           );
    itk::EncapsulateMetaData< std::string >( thisDic, "MultiVolume.FrameIdentifyingDICOMTagName" , FrameIdentifyingDICOMTagName  );
    itk::EncapsulateMetaData< std::string >( thisDic, "MultiVolume.FrameLabels"                  , TimingArrayValues.str()       );
    itk::EncapsulateMetaData< std::string >( thisDic, "MultiVolume.FrameIdentifyingDICOMTagUnits", FrameIdentifyingDICOMTagUnits );


    typedef itk::ImageFileWriter< VectorImageType > VectorWriterType;
    VectorWriterType::Pointer vectorwriter = VectorWriterType::New();
    std::ostringstream output4dfilename ;
    output4dfilename << argv[2] << ".nrrd";
    vectorwriter->SetFileName( output4dfilename.str()  );
    vectorwriter->SetInput( vectorFilter->GetOutput() );
    vectorwriter->Update( );

// Software Guide : BeginLatex
//
// Note that in addition to writing the volumetric image to a file we could
// have used it as the input for any 3D processing pipeline. Keep in mind that
// DICOM is simply a file format and a network protocol. Once the image data
// has been loaded into memory, it behaves as any other volumetric dataset that
// you could have loaded from any other file format.
//
// Software Guide : EndLatex

      }
    catch (itk::ExceptionObject &ex)
      {
      std::cout << ex << std::endl;
      return EXIT_FAILURE;
      }
// Software Guide : EndCodeSnippet



  return EXIT_SUCCESS;
}
