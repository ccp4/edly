# edly

pip install flask plotly tarikDrevonUtils tarikED==1.0.7rc0 wheel  

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
unzip jmol
cd jmol;unzip jsmol
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
