# Version log
## 0.0.7dev
###Thu  1 Jun 17:30:09 BST 2023
- issue#27 : hkl to shelx
    - script
    - download button
    test
###Thu 1 Jun 10:54:33 BST 2023
- issue#29:bloch rock
  - enable exp/sim rocking curves option
  - axis option to frame/index/Sw when show rocking curve
  - record `rock_frames` when simulated experimental frames
- fix minor bug when switching to structure with no exp data while `bloch['u0']=auto`
- fix `get_rock_sim` callback when switching to rock mode with no simulation data   
- changed the `info.graphs` structure
- get automatic reflection selection in rock mode when refreshing
- `clear` flag in `update_refl` callback when clearing table

## 0.0.6
###Wed 31 May 22:10:13 BST 2023
- issue#29 : bloch rock
  - change axis from Sw to Frame  
###Wed 31 May 12:34:51 BST 2023
- created file `static/views/main.html` for main layout
- template dependent variables present in header and footer still in `templates/main.html`  
- minor bug fix
###Wed 31 May 11:16:35 BST 2023
- issue#24: simulated integration
  - button to integrate at all thicknesses
  - show integrated reflections across thickness
### Wed 31 May 09:38:41 BST 2023
- minor fix in pixel range

### Tue 30 May 13:23:20 BST 2023
- issue#29 :bloch rock
  - modified `modes['u']` modes into single,rock,lacbed with corresponding buttons
  - created `modes['u0']` modes as auto,move,edit with corresponding buttons when `modes['u']=='single'`
  - removed `modes['manual']`
  - changed `set_u_mode` into `set_mode(key,val)` which dispatches to `set_u_mode(val)` and `set_u0_mode(val)`
  - first and last frame automatic retrieval
### Tue 30 May 10:43:38 BST 2023
- added fast forward and fast backward to exp data frame
- fix minor bug when new session
### Fri 26 May 14:11:29 BST 2023
- issue#36 : diff pattern axis
  - Enable passing from pixels to rec angstrom
  - change yaxis orientation up/down

### Thu 25 May 21:19:49 BST 2023
- issue#33 : show Nmax and dmin

### Thu 25 May 20:45:34 BST 2023
- issue#23 : import exp data auto orientation
  - works for dials(spot location wrong though)
  - wavelength retrieval
  - fix xds file should be a .HKL extension
- issue#35 refactor import dataset
  - dials and xds have a base class
  - pets has a common interface but does not inherit base class yet
### Thu 25 May 04:23:52 BST 2023
- issue#23 : auto orientation
  - works for pets
  - works for xds
- issue#35 refactor import dataset
  - unifying the data process interface with info : npx,rpl,cen
  - function hkl_to_pixels(hkl,frame) to obtain pixel locations from miller indices
  - partially removed the omega feature
  - modified pets so that its uvw is already correctly oriented and should not need a negative sign in edly
- fix bug frames panel not available when only the processed data exist
- fix error pets_file when no .pts present
- implemented a,w,s,d hotkeys for moving in rotation tweaking mode
- added some basic Mathjax ready startup stuffs

### Tue 23 May 17:21:28 BST 2023
- issue#37 : space group info
  - display space group, lattice system and number of atoms.
  - provide link to ucl chem space group info page
  - obtained a dictionary to pass from space group it number to hm symbol and vice versa
### Tue 23 May 01:25:24 BST 2023
- issue#29 : rocking curve
  - active simulation updated properly when passing from rock to other mode
  - u_sim orientation permanently above the mode options
  - rock solve button with the normal bloch solve button
  - solve rock available again when changing simulation parameters
  - rock solve should always complete properly now

### Mon 22 May 18:15:19 BST 2023
- moved omega parameter into frames panel
- bundled omega and offset into a settings expand menu.
###Mon 22 May 17:11:53 BST 2023
- issue#29 : rocking curve
  - put the u_sim orientation permanently on top of solve panel   
  - fixed bugs in updating u for sim and frames

### Fri 19 May 16:30:12 BST 2023
- issue#34 : bloch frames
  - put the u_frame in the frames panel
- cosmetic :(color,padding,etc...)
- fixed some bugs when session cookies are deleted
###Fri 19 May 10:54:33 BST 2023
- issue#33 : pass from resolution to index
- issue#30 : updating graph even when deleting reflections

### Thu 18 May 15:19:40 BST 2023
- issue#29 : rocking curve
  - automatically solve for rocking curve
  - fixed bugs solve rock
  - fixed wrong sign pinned orientation value
- fixed bug manual and single modes  
- changed init bug setTimeOut with interval cancelled only after `$scope.init=true`
### Thu 18 May 11:50:13 BST 2023
- issue#28 : tweak orientation
### Thu 18 May 11:15:52 BST 2023
- issue#21 : resolution rings bugs
  - bug with hiding data when no rings present
  - bug hiding rings does not always work for all rings
  - setting rings spacing to 0 result in no rings at all now

### Wed 17 May 17:18:48 BST 2023
- might have fixed initialization error bug with setTimeOut
### Wed 17 May 16:16:34 BST 2023
- issue#30 reflections :
  - clear button
  - put the automatically selected reflections in the table
  - automatic refresh option
- try fixing bug key error data['bloch'] at refresh(due to `init` occasionally called after `init_bloch_panel` )

### Wed 17 May 13:15:26 BST 2023
- issue#29 : Bloch experimental rocking curves
- fixed switching u modes bug

### Tue 16 May 19:12:01 BST 2023
- issue#35 refactor import dataset :
  - datasets loaded in `in_out.py`ff
- issue#31 :
  - enable reading exp frames without `cif_file`
  - disable solvers if `cif_file` not provided
- modified naming for nb_frames
- added cbf reader
- cleaned code

### Tue 16 May 13:32:48 BST 2023
- issue#34 :
  - fixed bloch frame overflow (pets.uvw does not contain the 5 last tiff images )
  - bloch not recalculated if the frame actually did not change
  - heatmap option only shown when in frames mode
  - bloch does not recalculate when switching mode if frame has not changed (repaced ng-switch directive with ng-show and moved controllers div outside of the ng-show directive so initialization does not happen every time the div is shown)

### Mon 15 May 20:11:43 BST 2023
- issue#34 : implemented canvas
- fixed bug with chemical formula was not fully working
- fixed bug with frame overflow and frame numbering (biotin starts at 0, glycine starts at 1)

## 0.0.5
### (Fri 28 Apr 17:44:15 BST 2023)
- remove (0,0,0) dials exp reflections
- fix omega bug when using `pred_info` with dials

### (Thu 28 Jul 15:33:06 BST 2022)
- enabled display pattern in pixels (stable for all dials/pets/no_data)
- enable to choose between pixel and rec space

### (Tue 19 Jul 18:19:22 BST 2022)
- implement tab index for frames
- moved bloch related calls to bloch.py
- reactivated modes.single (other modes are still buggy)

### (Tue 19 Jul 17:08:56 BST 2022)
- changed felix path to dedicated directory
- added more attempts in load_b0
- added lacbed option only if available in felix
- retractable frame offset
- biotin dataset imported with pets

### Fri 15 Jul 20:19:58 BST 2022
- fixed bug reload image when changing frames
- fixed bug reload frames when switching to frames
- fixed init bug for structures with no available images  
- fixed bug with update_visible
- fixed omega update bug
- dials import functionalities
- fixed bloch init session data
- image toggle reload button

### (Tue Jul 12 15:50:46 2022 +0100)
- added felix support
- lacbed patterns

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
- issue#15 : help menu links

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
