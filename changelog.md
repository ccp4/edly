## 0.0.1
## issue#5 (Sun  3 Apr 19:12:17 BST 2022)
- add all parameters inputs to Bloch solver
- import processed data
- update u,keV


## issue#3 (Sat  2 Apr 11:41:22 BST 2022)
- button JSmol to visualise the structure
- buttons (with popups):
    - upload : exp tiffs data
    - upload : simulated data  
    - upload : pets/dials processed data

### issue#4 (Thu 31 Mar 15:58:14 BST 2022)
- simu vs exp avec refl side by side
- toggle button to pass to single analysis mode
- added cif file to bloch solver
- split update_zmax for exp/sim frame
- added project/molecule row in html
- added default data for test structure
    - to install it : ```cd static/data/; ln -s ../../test test```
- clear a session : ```rm -rf static/data/tmp/<session_id> ```
- initial bloch param setup

# issue#2
- update zmax

# issue#1
- visualisation de df_G.[I,Swa,Vga]

### resave png image when updating zmax ('Tue Mar 29 18:56:50 2022')
- server must now be run with  `./serve.py` (`bw_app` registered with  `Blueprint`)
- introduced sessions to be cleaner
- split in app.js `update` into `update_bloch` and `update_img`
