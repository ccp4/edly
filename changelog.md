# Version log

## 0.0.4
### Mon 23 May 10:46:46 BST 2022
- Vga and Sw legendonly at start
- lock u switching to glycine
- created `set_viewer` with url parameters
- introduced server dependent home url
- added version number

## 0.0.3
### issue#18 (Sat 21 May 17:44:05 BST 2022)
- Use gemmi
- use resolution dmin instead of Nmax
- changed import style when doing new structure(pdb saved to file now)  
- create object at `init_mol` and only `update` it after


### issue#12 FELIX option (Fri 20 May 13:24:16 BST 2022)
- enable solve from Felix with `bloch_state` recording
- felix widget with `nbeams` parameter
- added rings step
- changed cif file handling due to crystals lib pbs
- minor change on get_frame
- left/right for large thickness stepping
- automatic reflection expand on select and thickness on solved

## 0.0.2
### Thu 19 May 12:08:35 BST 2022
- fixed bug updating thickness for rocking curve simu
- updating rocking curves thickness
- fixed graph rock session saved
- fixed occasional bug at end of rock simulations

### Wed 18 May 15:01:58 BST 2022
- fixed bug not re updating when changing structure
- fixed bug re initializing all arguments when changing structure
- scattering factors viewer
- added solver state `bloch_state`
- added resolution rings
- graph fig2 saved in session

### Tue 17 May 17:40:15 BST 2022
- added username info

### Tue 17 May 11:19:21 BST 2022
- Solve bloch state created to prevent solving when already being solved
- interval rock not working on VM : get('/') fixed  
- rocking curve error : `thick` taken from `session['bloch']`
- rocking curve orientations error : needed calling `get_uvw_cont`

### issue#15 help menu links
#### (Tue 26 Apr 09:51:41 BST 2022)
- hide error after closing dialog
- import cif
- added links
- fixed frame enter issue due to ng-if

#### (Tue 26 Apr 00:58:23 BST 2022)
- projects (new, other projects, ...)
- links : (theory,documentation,tests)
- help
- pets orientation vector u
- y range goes from xm to -xm
- set_intensities with FELIX convention
- import crambin

### issue#16 miller indices table (Fri 22 Apr 20:26:20 BST 2022)
- highlight on hover
- removed update when changing analysis mode

### issue#11 rocking curve  (Fri 22 Apr 16:03:47 BST 2022)
- use arrows or select frame
- set u from frame
- I_pets updated from current frame  in rock_mode
- max res input
- added footer copyright
- expandable structure parameters
- added info for miller table
- created tabs for modes['analysis'] preparing for multislice

### (Thu 21 Apr 16:24:22 BST 2022)
- rock graph only available in rock mode  
- update reflection table in session

## 0.0.1
### issue#9 ( Thu 21 Apr 16:24:22 BST 2022)
- graph selector
- plotly menu for the curves to show
- use `b0_path` to fix beam_vs_thickness update in rock mode
- `show_u` includes all orientation in auto mode (very slow)
- click enter on rock frame for specifying input
- change graphs layout to align dropdown menu nicely

### issue#6 (Tue 19 Apr 15:42:37 BST 2022)
- beam selection from plotly
- add rpx,rpy,Ipets data to the plotly graph
- show miller indices when hovering over data points
- add a callback which adds/removes in a javascript array the selected hkl
- use and show proper markers
- add a background color (light blue) to the graph
- persistent xylims
- persistent data visibility
- adding MathJax dependency
- added structure info in `crys`
- bloch solver layout with expandable parameters
- added rotation parameter omega
- added selected beams to rocking curve and thickness dep
- bug fix when updating frame orientation vector  

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
