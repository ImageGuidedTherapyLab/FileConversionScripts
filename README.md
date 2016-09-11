MATLAB Code Repository
----------------------

This repository stores various file conversion scripts 

## to run dicom server:
 python DicomSeriesReadImageWrite.py --server=innovador.ini

* storescp obtained from Slicer4
* http://support.dcmtk.org/docs/storescp.html
* python vtk bindings obtained from EPD 7.3.1

## python itk bindings build with

 cmake -DCMAKE_CXX_COMPILER=/usr/bin/g++-4.4 -DCMAKE_C_COMPILER=/usr/bin/gcc-4.4 -DBUILD_SHARED_LIBS=ON  -DCMAKE_BUILD_TYPE=Debug -DBUILD_EXAMPLES=ON -DBUILD_TESTING=OFF -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_INSTALL_PREFIX=$ITK_HOME -DITK_WRAP_PYTHON=ON -DINSTALL_WRAP_ITK_COMPATIBILITY=OFF -DITK_WRAP_double=ON -DITK_USE_SYSTEM_SWIG=ON -DPYTHON_EXECUTABLE=$EPD_ROOT/bin/python -DPYTHON_INCLUDE_DIR=$EPD_ROOT/include/python2.7 -DPYTHON_LIBRARY=$EPD_ROOT/lib/libpython2.7.so ../InsightToolkit-4.3.1



## dicom transfer

findscu    -P  -k 0008,0052=STUDY   -aet <AET> -aec <AEC> IPAddress Port# -k 0010,0020=<MRN>  -k 0020,000d -k 0008,1030 -k 0008,0020 -k 0008,0050
findscu    -S  -k 0008,0052=SERIES  -aet <AET> -aec <AEC> IPAddress Port# -k 0020,000D=<StudyUID> -k 0020,000E -k 0008,0060 -k 0010,0020=<MRN> -k 0008,103e
movescu -v -S  -k 0008,0052=SERIES  -aet <AET> -aec <AEC> IPAddress Port# -k 0020,000D=<StudyUID> -k 0020,000e=<SeriesUID>




## simple file conversion:
 python convertExodusToMatlab.py --ini_file=dog1.ini

all mesh file names, imaging parameters, and affine transformation parameters should be in the ini file

and example ini file is given in dog1.ini:
 adjust work_dir, mesh_filenames, etc accordingly

Standard prefixes for commit messages
-------------------------------------

following - http://www.itk.org/Wiki/ITK/Git/Develop

 *  BUG: Fix for runtime crash or incorrect result
 *  COMP: Compiler error or warning fix
 *  DOC: Documentation change
 *  ENH: New functionality
 *  PERF: Performance improvement
 *  STYLE: No logic impact (indentation, comments)
 *  WIP: Work In Progress not ready for merge 


Naming Conventions
------------------

following - `http://www.itk.org/Wiki/ITK/Coding_Style_Guide#Naming_Conventions`

 * Names are constructed by using case change to indicate separate words, as in TimeStamp (versus Time Stamp).
 * Underscores are not used.
 * Variable names are chosen carefully with the intention to convey the meaning behind the code.
 * Names are generally spelled out
 * Use of abbreviations is discouraged. (Abbreviation are allowable when in common use, and should be in uppercase as in RGB.) While this does result in long names, it self-documents the code.
 * If you learn how to use name completion in your editor (e.g.,Vim, Emacs), this inconvenience can be minimized. 

Submodules
----------

http://git-scm.com/book/en/Git-Tools-Submodules
http://stackoverflow.com/questions/3796927/how-to-git-clone-including-submodules

    $ git submodule update --init --recursive
    Submodule 'projects/CurveFit' (git@github.com:ImageGuidedTherapyLab/MatlabCurveFit.git) registered for path 'projects/CurveFit'
    Cloning into 'projects/CurveFit'...
    remote: Counting objects: 401, done.
    remote: Total 401 (delta 0), reused 0 (delta 0)
    Receiving objects: 100% (401/401), 1.67 MiB | 1.72 MiB/s, done.
    Resolving deltas: 100% (178/178), done.
    Submodule path 'projects/CurveFit': checked out '109825540c0790b3a949f77661a59410fbafb133'


refresh all remotes' branches, adding new ones and deleting removed ones.
----------

    git remote update --prune

remove large file from history
----------
https://help.github.com/articles/remove-sensitive-data/

 * run from top of repo and push changes

    git filter-branch --force --index-filter  'git rm --cached --ignore-unmatch path/to/largefiles/*' --prune-empty --tag-name-filter cat -- --all
    git push origin --force --all

 * other forks/branchnes need to rebase to the master... dangerous ?  (http://git-scm.com/book/en/v2/Git-Branching-Rebasing)

    git pull --rebase origin master


extract a subdirectory as a new repo
----------
https://help.github.com/articles/splitting-a-subfolder-out-into-a-new-repository/

 * git filter-branch --prune-empty --subdirectory-filter YOUR_FOLDER_NAME master
 * git push my-new-repo -f .


Merging Repos
----------

http://stackoverflow.com/questions/13040958/merge-two-git-repositories-without-breaking-file-history

Here's a way that doesn't rewrite any history, so all commit IDs will remain valid. The end-result is that the second repo's files will end up in a subdirectory.

1. Add the second repo as a remote:

   cd firstgitrepo/
   git remote add -f secondrepo username@servername:andsoon

2. Create a local branch from the second repo's branch:

   git branch branchfromsecondrepo secondrepo/master; git checkout branchfromsecondrepo

3. Move all its files into a subdirectory:

   mkdir subdir/
   git ls-tree -z --name-only HEAD | xargs -0 -I {} git mv {} subdir/

4.  Merge the second branch into the first repo's master branch:

   git commit -m "STYLE: organizing files"; git checkout master; git merge branchfromsecondrepo

5. clean up

   git branch -D branchfromsecondrepo; git remote rm secondrepo

6. git log --follow file

   Continue listing the history of a file beyond renames (works only for a single file).
