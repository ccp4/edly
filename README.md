# edly
Electron diffraction simulator web dashboard.

## Installation
### python dependencies
pip install flask plotly wheel tarikDrevonUtils

### Development environment
```
python3 -m venv .env
cd .env
source bin/activate
git clone git@github.com:ccp4/electron-diffraction.git
cd electron-diffraction
pip install -e .
```
Then a simple git pull on these dependencies will keep them up to date

### Installing the js dependencies
```
bower install jquery angular angular-aria angular-touch angular-bootstrap bootstrap-css bootstrap angular-chart jquery-ui plotly MathJax

cd static
ln -s ../bower_components .
mkdir css
wget -O css/all.css https://css.gg/css
```

<!-- ## Installing jsmol
```
cd static
wget https://sourceforge.net/projects/jmol/files/latest/download
unzip download
mv jmol<version> jmol
cd jmol;unzip jsmol -->


### installing the test dataset
```
cd static/data/; ln -s ../../test test
```

## Miscellaneous
### Clear a session info
They should be cleared every day but can be cleared manually with :
```
rm -rf static/data/tmp/<session_id>
```
