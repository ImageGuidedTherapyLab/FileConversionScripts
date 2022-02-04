# Start from scratch
FROM ubuntu:20.04

# Set user as root for sufficient permissions
USER root

# Install dependencies
RUN echo "Installing dependencies..."
RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive"  apt-get install --fix-missing -y apt-utils \
                                                        dpkg \
                                                        curl \
                                                        bc \
                                                        libncurses5 \
                                                        libxext6 \
                                                        libxmu6 \
                                                        libxpm-dev \
                                                        libxt6 \
                                                        git-all \
                                                        unzip \
                                                        dc \
                                                        file \
                                                        libfontconfig1 \
                                                        libfreetype6 \
                                                        libgl1-mesa-dev \
                                                        libgl1-mesa-dri \
                                                        libglu1-mesa-dev \
                                                        libgomp1 \
                                                        libice6 \
                                                        libxcursor1 \
                                                        libxft2 \
                                                        libxinerama1 \
                                                        libxrandr2 \
                                                        libxrender1 \
                                                        libxt6 \
                                                        sudo \
                                                        wget \
                                                        ed \
                                                        gsl-bin \
                                                        libglib2.0-0 \
                                                        libglu1-mesa-dev \
                                                        libglw1-mesa \
                                                        libgomp1 \
                                                        libjpeg62 \
                                                        libnlopt-dev \
                                                        libxm4 \
                                                        netpbm \
                                                        r-base \
                                                        r-base-dev \
                                                        tcsh \
                                                        xfonts-base \
                                                        xvfb \
                                                        cmake \ 
                                                        nano \
                                                        vim \
                                                        libinsighttoolkit4.13 \
                                                        libinsighttoolkit4-dev 
                                                        
# docker disable documentation
# https://unix.stackexchange.com/questions/684774/missing-files-after-installing-package-on-nginx-docker-image
RUN sed -i 's/path-exclude=\/usr\/share\/doc/#path-exclude=\/usr\/share\/doc/g' /etc/dpkg/dpkg.cfg.d/excludes
RUN DEBIAN_FRONTEND="noninteractive"  apt-get install  -y insighttoolkit4-examples 

RUN mkdir /app
RUN gunzip -d -c /usr/share/doc/insighttoolkit4-examples/examples/IO/DicomSeriesReadImageWrite2.cxx.gz  > /app/DicomSeriesReadImageWrite2.cxx
ADD ./CMakeLists.txt /app
WORKDIR /app
RUN cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_VERBOSE_MAKEFILE=ON -DITK_DIR=/usr/lib/cmake/ITK-4.13/
RUN make 
RUN mkdir /data
RUN mkdir /out

ENTRYPOINT ["/app/DicomSeriesReadImageWrite2"]

