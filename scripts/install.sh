bash miniconda.sh -b -p $HOME/miniconda;
export PATH="$HOME/miniconda:$HOME/miniconda/bin:$PATH";
hash -r;
conda config --set always_yes yes --set changeps1 no;
conda update -q conda;
echo $TRAVIS_OS_NAME;
echo $TRAVIS_PYTHON_VERSION;
conda env create python=$TRAVIS_PYTHON_VERSION -f environment.yml;
source activate pybcli;
