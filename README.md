to run dicom server:
 python DicomSeriesReadImageWrite.py --server=innovador.ini

storescp obtained from Slicer4

 http://support.dcmtk.org/docs/storescp.html

python vtk bindings obtained from EPD 7.3.1

python itk bindings build with:

 cmake -DCMAKE_CXX_COMPILER=/usr/bin/g++-4.4 -DCMAKE_C_COMPILER=/usr/bin/gcc-4.4 -DBUILD_SHARED_LIBS=ON  -DCMAKE_BUILD_TYPE=Debug -DBUILD_EXAMPLES=ON -DBUILD_TESTING=OFF -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_INSTALL_PREFIX=$ITK_HOME -DITK_WRAP_PYTHON=ON -DINSTALL_WRAP_ITK_COMPATIBILITY=OFF -DITK_WRAP_double=ON -DITK_USE_SYSTEM_SWIG=ON -DPYTHON_EXECUTABLE=$EPD_ROOT/bin/python -DPYTHON_INCLUDE_DIR=$EPD_ROOT/include/python2.7 -DPYTHON_LIBRARY=$EPD_ROOT/lib/libpython2.7.so ../InsightToolkit-4.3.1




simple file conversion:
 python convertExodusToMatlab.py --ini_file=dog1.ini

all mesh file names, imaging parameters, and affine transformation parameters should be in the ini file

and example ini file is given in dog1.ini:
 adjust work_dir, mesh_filenames, etc accordingly

