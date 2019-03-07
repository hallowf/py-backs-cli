mkdir UPX && cd UPX && export UPX_PATH=$PWD &&
curl -sL -o upx.txz https://github.com/upx/upx/releases/download/v3.95/upx-3.95-amd64_linux.tar.xz
tar -xvf upx.txz
cd ..
