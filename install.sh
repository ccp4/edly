#! /bin/bash
version=$(grep "## [0-9]" changelog.md  | head -n1 | cut -d" " -f2)
echo $version

python3 -m venv .env
source bin/activate
.env/bin/pip install flask plotly wheel opencv-python tarikDrevonUtils
# cd .env

if [ $1 -eq dev ];then
  git clone git@github.com:ccp4/electron-diffraction.git
  git switch exp
  git checkout acbd992
  cd electron-diffraction
  pip install -e .
else
  .env/bin/pip install ccp4ED==1.1.0
fi


cd edly
bower install jquery angular angular-aria angular-touch angular-bootstrap bootstrap-css bootstrap angular-chart jquery-ui plotly MathJax
cd static
ln -s ../bower_components .


###
if [ $2 -eq test ];then
  pip install selenium==4.9.1 pytest-html
  if [ $(chromium.chromedriver --version | cut -d" " -f2) == "114.0.5735.106"];then
    echo ok
  fi
fi
