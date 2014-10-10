
ITK_SOURCE=/opt/apps/ITK/InsightToolkit-dev
ITK_DIR=/opt/apps/ITK/InsightToolkit-dev-gcc-4.4.3-dbg/lib/cmake/ITK-4.4

all: Makefile
	make -f Makefile
Makefile: 
	cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_VERBOSE_MAKEFILE=ON -DITK_DIR=$(ITK_DIR)
clean:
	rm -rf CMakeCache.txt Makefile CMakeFiles/ ITKIOFactoryRegistration/ cmake_install.cmake  
tags:
	ctags -R --langmap=c++:+.txx --langmap=c++:+.cl $(ITK_SOURCE) .

.PHONY: tags
