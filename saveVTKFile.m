function saveVTKFile(filename,varname, data, spacing)
%SAVEVTKFILE Save data to VTK file.
%   Save 2D or 3D data to VTK file. The given header infomation needs to be
%   output of 'dicominfo'.
%
%   This code is based on a script written by Erik Vidholm (2006) and
%   modified by Joshua Yung (2010).
%
%   filename:   Filename of VTK file.
%   data:       2D or 3D data array, e.g. 'float' or 'double'.
%   header:     DICOM header (output of dicominfo).


    %% Set image dimensions.
    dimensions = zeros(1,3);
    dimensions(1) = size(data,1);
    dimensions(2) = size(data,2);
    dimensions(3) = size(data,3);
    
    %% error check spacing
    if(size(spacing) ~= 3)
      disp('incorrect spacing input');
      disp('expecting 3d data ');
      disp(' -or-  2d with one slice ');
      return
    end

    %% Image position.
    origin = zeros(1,3);
    %origin(1) = header.ImagePositionPatient(1);
    %origin(2) = header.ImagePositionPatient(2);
    %origin(3) = header.ImagePositionPatient(3);

    %% Image orientation.
    %orientationX = zeros(1,3);
    %orientationX(1) = header.ImageOrientationPatient(1);
    %orientationX(2) = header.ImageOrientationPatient(2);
    %orientationX(3) = header.ImageOrientationPatient(3);
    %orientationY = zeros(1,3);
    %orientationY(1) = header.ImageOrientationPatient(4);
    %orientationY(2) = header.ImageOrientationPatient(5);
    %orientationY(3) = header.ImageOrientationPatient(6);
    %normal = cross(orientationX,orientationY);

    %% Open VTK file.
    fid = fopen(filename, 'w', 'b');

    %% Write VTK header
    fprintf(fid, '# vtk DataFile Version 3.6\n');
    fprintf(fid, 'Created by saveVTKFile for MRTI data.\n');
    fprintf(fid, 'BINARY\n');  
    fprintf(fid, 'DATASET STRUCTURED_POINTS\n');  
    fprintf(fid, 'DIMENSIONS %d %d %d\n', dimensions(1), dimensions(2), dimensions(3));
    fprintf(fid, 'ORIGIN %f %f %f\n', origin(1), origin(2), origin(3));
    fprintf(fid, 'SPACING %.4f %.4f %.4f\n', spacing(1), spacing(2), spacing(3)); 
    fprintf(fid, 'POINT_DATA %d\n', dimensions(1)*dimensions(2)*dimensions(3));

    switch(class(data))
        case 'uint8'
            datatype = 'unsigned_char';
        case 'int8'
            datatype = 'char';
        case 'uint16'
            datatype = 'unsigned_short';
        case 'int16'
            datatype = 'short';
        case 'uint32'
            datatype = 'unsigned_int';
        case 'int32'
            datatype = 'int';
        case 'single'
            datatype = 'float';
        case 'double'
            datatype = 'double';
    end
    
    fprintf(fid, 'SCALARS %s %s 1\n', varname, datatype);
    fprintf(fid, 'LOOKUP_TABLE default\n');

    %% Write data.
    fwrite(fid, data, class(data));

    %% Close file.
    fclose(fid);

end
