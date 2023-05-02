#! /bin/bash
version=$(grep "## [0-9]" changelog.md  | head -n1 | cut -d" " -f2)
echo $version

python3 -m venv .env
pip install flask plotly wheel tarikDrevonUtils ccp4ED==1.0.9
cd .env
source bin/activate

if [ $1 -eq dev ];then
  git clone git@github.com:ccp4/electron-diffraction.git
  cd electron-diffraction
  pip install -e .
fi


bower install jquery angular angular-aria angular-touch angular-bootstrap bootstrap-css bootstrap angular-chart jquery-ui plotly MathJax
cd static
ln -s ../bower_components .
