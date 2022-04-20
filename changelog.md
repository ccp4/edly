# Version log

## 0.0.1
### issue#6 (Tue 19 Apr 15:42:37 BST 2022)
- beam selection from plotly
- add rpx,rpy,Ipets data to the plotly graph
- show miller indices when hovering over data points
- add a callback which adds/removes in a javascript array the selected hkl
- use and show proper markers
- add a background color (light blue) to the graph
- add px and py labels to the axes
- persistent xylims
- persistent data visibility
- adding MathJax dependency
- added structure info in `crys`
- bloch solver layout with expandable parameters
- bug fix when updating frame orientation vector  
- added rotation parameter omega
- added selected beams to rocking curve and thickness dep

### issue#8 (Mon 11 Apr 16:53:08 BST 2022)
- Rocking curve
- [x] compute and display rocking curve in side figure
- [x] add panel for rocking curve parameters
- [x] show computation evolution
- [x] go through rocking patterns
- [x] toggle rocking/overlay images
- [x] add figure for showing 3d orientation
- created in_out.py
- added gg-icons.css
- use `modes['u']` to str (move,edit,rock)

### issue#7 (Fri  8 Apr 12:38:20 BST 2022)
- display b0.beam_vs_thickness in either another window or aside of analysis
- toggle button for dual view
- updates on press enter for `thickness`, `range`, `u` inputs
- arrows for changing `thickness` and dthick
- grouped `show_molecule`,`analysis_mode`... into `session['modes'][mode]` for better control over saving session state and toggles
- split `solve_bloch`  into `update_bloch` and `bloch_fig` for better update of `update_thick`


### issue#10 (Thu  7 Apr 14:46:11 BST 2022)
- created `rotation_mode`
- bw_app.py:solve_bloch split into 2 functions to accommodate for `bloch_rotation`
- pets data loaded when sessions are created
- arrows can be used to change orientation when the rotation panel is focused
- library bloch.py modified to include `I` key even when not solved.

### issue#5 (Sun  3 Apr 19:12:17 BST 2022)
- add all parameters inputs to Bloch solver
- import processed data
- update u,keV

### issue#3 (Sat  2 Apr 11:41:22 BST 2022)
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

###  issue#2 ('Tue Mar 29 18:56:50 2022')
- resave png image when updating zmax
- server must now be run with  `./serve.py` (`bw_app` registered with  `Blueprint`)
- introduced sessions to be cleaner
- split in app.js `update` into `update_bloch` and `update_img`

### issue#1
- visualisation de df_G.[I,Swa,Vga]
