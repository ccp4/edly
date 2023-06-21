# TODO

- graph state retrieval
- overlay exp data in both rock and integrated
- output HKL

## changes summary 0.0.6
- import dataset from xds,pets,dials
- automatic exp wavelength retrieval  
- reflections (auto retrieve + live update)
- rock mode : exp rocking curves
- cosmetic :
  - structure info (nb atoms, lat, space group,chemical formula)
  - u_frame,u_sim
  - orientation mode (+tweaking hotkeys,lock)
  - frames very fast and efficient
  - pixels/reversed axis
  - resolution/Nmax
- bug fixing


## main features :
- electron diffraction dynamical Bloch solver explorer
- import processed dataset from xds,pets,dials
- rocking curve simulation of experimental datasets
- experimental frames viewer
- automatic dataset retrieval from zenodo database
- export simulated data to .hkl
- web based application which can work directly with large simulated data on STFC clusters  (avoids downloading large amount of simulated data )

## QA
- get tests for frontend/backend edly with github actions
- put tests for blochwave on same server as edly + github actions
- proper install guide of edly locally
- code coverage link on edly
