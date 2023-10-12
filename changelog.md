# Version log
## 0.0.7dev
### Thu 12 Oct 13:11:11 BST 2023
- issue#62 : delete frames
  - simple new feature

### Wed 11 Oct 19:06:36 BST 2023
- issue#63 : cancel download
  - added ids to relevant html DOM
  - link is updated only when clicking back on the set_link button
  - added `download.downloading` in *mainCtrl.js*
  - download jobs have an ID
- test :
  - added download/cancel download and manipulate zenodo entries
- update README

### Mon  9 Oct 20:45:54 BST 2023
- added test option to run only specific files as `run_tests.sh -m 'frames'`
- login and close are run no matter what
- browser creation is a global fixture defined in *conftest.py*
- removed *test_base.py*

### Thu  5 Oct 17:26:24 BST2023
- reports of tests sent by email

### Wed 27 Sep 13:31:28 BST 2023
- added test_frames to automatically test frame import and navigation

### Mon 25 Sep 17:07:56 BST 2023
- issue#61 :
  - fix empty database error at init
- ccp4ED version : `exp 7759eca`

### Tue 19 Sep 17:39:04 BST 2023
- issue#55 :
  - fixed create new project errors

### Tue 18 Jul 17:56:01 BST 2023
- rocking curve :
  - delete option
  - get info on load change
  - new_rock

### Tue 18 Jul 14:09:27 BST 2023
- issue#52 : fix pets import
- added rock_frames to old simus
- ED version : exp 7759eca

### Thu  6 Jul 09:08:32 BST 2023
- issue#51
  - enter simu number messes up the frame number
  - full rock reflection selection in Io vs Ic
  - `show_rock` display both exp and simu rocking curve
  - changed exp integration to only cover simulated frames
  - save `rock_frames` info into `Rock` object to retrieve at anytime
  - fixed automatic rock_name selection at startup
  - button sync frame and simu nb
  - green saved button
### Fri 30 Jun 17:50:41 BST 2023
- issue#49 : rock curves and IovsIc bugs
  - fix update rock curves bug when in IovsIc mode
  - properly update IovsIc curve when changing thickness
  - reflections index shown on IovsIc
  - clickable reflections on IovsIc graph
  - fix available  graphs bugs at refresh
- removed structure links in navigation
- tests :
  - added code coverage support

### Wed 28 Jun 16:34:17 BST 2023
- bug fixes :
  - remove try except `init_structure()`
  - removed trailing '/' in replace database_path
- tests:
  - run_test uses getopts with simplified flag options
  - added report,dev,lvl flags to run_tests
  - added level markers to tests

### Tue 27 Jun 21:11:03 BST 2023
- bug fixes :
  - check pets key before loading it
  - check `df_G` in dict for `beam_vs_thick`
  - update `session['crys']` when importing `cif_file`
  - fix popup not showing for some buttons
  - increased popup timer to allow smooth button selection
- tests :
  - added lots of ids
  - added selenium_utils files for function callbacks
  - new passing test :  `import dat`,
  - new passing test `frames_mode`(click_nav, key_nav, input_nav, br, heat)
  - new passing test `bloch_mode` (single,thick,thicks,rock_solve,save, rock_curves, integrate)
- note :
  - app does not display fine in offline mode
  - version : electron-diffraction commit : exp 347da7c

### Mon 26 Jun 20:15:58 BST 2023
- bug fixes :
  - do not display bloch or frames if not available
  - do not display import options if no structure is selected
  - update display if deleting structure was the active structure
  - full frames folder path removing database path
  - create database link and folder if not present
  - added submit functions to all dialog forms
  - fix ng-style bug on delete_dialog element
- tests :
  - added ids to lots of widgets
  - failing in headless mode
  - added `.send_keys()`/`.click()` for `focus`/`upload_file` interactions
  - new test :  `new_structure` passing
  - new test :  `import_cif`    passing
  - new test :  `import_frames` passing
  - new test :  `delete_struct` passing

### Mon 26 Jun 10:15:37 BST 2023
- enhancement:
   - added create and delete structure buttons
   - display stuff
   - full link for frames folder
   - confirmation delete dialog
   - ng-blur and ng-focus on search input boxes
### Mon 26 Jun 08:47:56 BST 2023
- bug fix :  
  - fixed folder name in `data_path`
- cosmetic :
  - `fetch` flag when updating zenodo so it only does it on cloud request
  - minor display stuff

### Wed 21 Jun 14:55:31 BST 2023
- issue#44 import info:
  - added update zenodo functionality although does not work in headless
  - added zenodo.py file
  - not fully tested
- enhancement :
  - added search frames in local database functionality
  - switch from local to zenodo database
  - click to edit frames link (default non editable)
- bug fixes :
  - fix dl_state stall and extracting msg
  - fix frame folders with some image formats not detected
  - fix bug when downloading with custom link
- refactor :
  - changed `/import_frames` as `/check_dl_format`
  - changed `/create_sym_link` as  `load_frames`
  - created `download` structure in mainCtrl
  - cosmetic html changes

### Tue 20 Jun 16:06:12 BST 2023
- bug fixes

### Tue 20 Jun 13:09:46 BST 2023
- refactor
  - modified sim frame panel to be the same as exp
  - frames mode only available when frames are present
- bug fixes :
  - sanity check to prevent mode=frame is not frames present  
  - update formula when change structure without refresh
  - bloch_fig can only display dat info if no simulation available
  - update_bloch calls fig only when called from rotation_mode
  - added `defer` and removed `async` in calling mathjax hoping it fixes init pbs

### Mon 19 Jun 17:04:54 BST 2023
- issue#44 import info
  - allow structure creation without cif
- issue#46 no refresh on structure change
  - refactor `new_structure` and `set_structure` into main controller
  - added open_structure button in import menu
  - implemented searchable structure
  - fetch molecule info(dat,frames,cif)
- created new_form.html
- fixed bug with pedestal (overflow index into colormap)

### Mon 19 Jun 11:14:43 BST 2023
- issue#47 : jump by frames
  -  added pedestal
  - switch keys  s and w for frame navigation
### Mon 19 Jun 10:58:28 BST 2023
- minor css changes
### Mon 19 Jun 10:44:50 BST 2023
- issue#47 : jump by frames
- only allow bloch mode if a cif is provided
- ED==acbd992

### Sat 17 Jun 04:30:12 BST 2023
- issue#44 import info
  - import processed data
  - options to choose from processed data
  - update exp info on refresh
  - import cif file
- refactor :
  - created `upload_cif` into `upload_file` for file submission into tmp/upload
  - created `init_structure` to reload on `import_cif`
  - symlink created to link processed data to software directory (dials/pets/xds)
- bug :
- electron-diffraction  library pets.py has issues retrieving molecule basename

###Fri 16 Jun 10:21:28 BST 2023
- issue#44 import info
  - import frames from local database (creates symlink to exp)
  - download and extract from zenodo to local database
  - browse zenodo database
  - import frames/processed/cif layout
- minor refactor of structure_panel
- minor refactor of frames_viewer

###Tue 13 Jun 12:33:39 BST 2023
- minor changes to tests to get them to work headless for remote website
- uses `rootScope` calls between controllers at init to force sequential execution

###Fri  9 Jun 14:27:01 BST 2023
- bug fixes :
  - fixed CHUNK ERROR by sending only one image at a time
  - fixed padding resolution for more general case
  - fixed rock update on frames mode on refresh
  - fixed calling `update_graph` in `set_rock_graphs` on init
refactor :
  - read image file directly using glob and frame number
  - moved image readers to EDutils
  - moved spacegroup to EDutils
  - calling `init_bloch_panel` from `init` to guarantee order


###Thu  8 Jun 13:20:22 BST 2023
- issue#26 : installation
  - tests can take parameters `sleep` and `headless` and `port`
  - added fixtures

###Thu  8 Jun 11:24:06 BST 2023
- option to run server in debug mode and with another port number
###Wed  7 Jun 17:49:34 BST 2023
- issue#45 :load save rock data
  - save rock
  - load rock
  - refactor loading rock and simulation
  - warning when trying to overwrite save
  - load properly on refresh
- quick layout change
- fix update nbeams
###Tue  6 Jun 16:21:35 BST 2023
- issue#45 :load save rock data
  - frontend load button
- changed layout rocking curve settings and integration
###Mon  5 Jun 19:38:33 BST 2023
- selenium test
###Mon  5 Jun 19:37:07 BST 2023
- issue#43 : Rfactor
  - Show thickness dependent R factor
  - Fo vs Fc at selected thickness

###Thu  1 Jun 17:30:09 BST 2023
- issue#27 : hkl to shelx
  - script
  - download button
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
