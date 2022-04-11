# edly

pip install flask plotly wheel tarikDrevonUtils tarikED==1.0.7rc0

## development environment
git clone https://github.com/ronandrevon/debloch
git clone https://github.com/ronandrevon/debloch
pip install -e .

## Installing the js dependencies
bower install jquery angular angular-aria angular-touch angular-bootstrap bootstrap-css bootstrap angular-chart plotly
```
cd static
ln -s ../bower_components .
```

## Installing jsmol
```
cd static
wget https://sourceforge.net/projects/jmol/files/latest/download
unzip download
mv jmol<version> jmol
cd jmol;unzip jsmol
```

```
wget -O static/css/all.css https://css.gg/css
```

### installing the test dataset
```
cd static/data/; ln -s ../../test test
```

### Clear a session info
They should be cleared every day but can be cleared manually with :
```
rm -rf static/data/tmp/<session_id>
```
