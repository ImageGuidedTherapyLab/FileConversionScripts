# This is the root ITK CMakeLists file.
cmake_minimum_required(VERSION 2.8.12)
if(COMMAND CMAKE_POLICY)
  cmake_policy(SET CMP0003 NEW)
endif()


# This project is designed to be built outside the Insight source tree.
project(dicomnifti)

# Find ITK.
find_package(ITK REQUIRED)
include(${ITK_USE_FILE})

add_executable(DicomSeriesReadImageWrite2 DicomSeriesReadImageWrite2.cxx )


target_link_libraries(DicomSeriesReadImageWrite2 ${ITK_LIBRARIES})
