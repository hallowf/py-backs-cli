if [ "$TRAVIS_OS_NAME" == "linux" ]; then
  wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
elif  [ "$TRAVIS_OS_NAME" == "osx" ]; then
  wget https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O miniconda.sh;
elif  [ "$TRAVIS_OS_NAME" == "windows" ]; then
  choco install python && ;
  mkdir UPX && cd UPX && export UPX_PATH=$(PWD) && ;
  curl https://github.com/upx/upx/releases/download/v3.95/upx-3.95-win64.zip -J -L --output UPX.zip && ;
  7z e -y UPX.zip -o"." upx-3.95-win64\*.exe && ;
  cd .. ;
fi
