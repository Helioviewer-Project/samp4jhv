# samp4jhv
SAMP library to interact with JHV

## examples
scripts showing examples of how to interact with JHV

### python

#### 2021-05 Extract images from IRIS SJI cubes.ipynb
Example script to load IRIS images from TAP source and extract them into single images, with slight modifications for optimal display in JHV.

#### 2021-10-04-Send-RHESSI_to_JHV_via_SAMP.ipynb
Example script to download RHESSI image cubes from TAP source, extract images and send them to JHV:
1. retrieve data from TAP service using `pyvo`
1. select interesting RHESSI observations
1. usage of `sunkit_instruments.rhessi.imagecube2map` to extract images (into `sunpy.map.Map` objects) from image cube
1. (optional) convert datatype to bypass JHV gamma correction and re-scaling data into respective value range
1. usage of `SAMP4JHVClient` to send maps directly to JHV via SAMP. Alternatively one could save the maps to disk and drag-and-drop them into JHV.
1. usage of `Samp4JHVClient` object to clean up temporary data

#### 2022-05-create_space_time_plot.ipynb
Example script to create space-time plot along IRIS slit - this was used to visually verify whether observations contain downflows with the help of JHV

#### SAMP_example.ipynb
older example (from CCN2) to read SAMP message from JHV and manually download defined data from VSO.

#### SAMP_example_Fido.ipynb
older example (from CCN2) to read SAMP message from JHV and download defined data using Fido search

#### SAMP_example_new.ipynb
same as `SAMP_example.ipynb` but with progress bars

#### SAMP_example_sunpy3.0.ipynb
updated version of `SAMP_example_new.ipynb` to work with sunpy 3.0

### IDL
examples to setup JSAMP in IDL to read SAMP messages from JHV and load corresponding data from VSO. See separate README.

### web
examples on how to use varioud files and formats that can send data to JHV from a webpage

## ext
### rhessi
Contains convenience functions to read raw rhessi flare lists and extracting images from rhessi image cube. These functionalities have been replaced:
- reading flare lists can now by done using `pyvo` by accessing the tap service at https://tap.cs.technik.fhnw.ch/tap
- functionality to extract images has been added to [sunkit-instruments](https://docs.sunpy.org/projects/sunkit-instruments/en/stable/index.html)

### example_send_rhessi_flare_to_jhv.ipynb
Example notebook to use functionalities from `rhessi` subfolder. See `examples/python/2021-10-04-Send-RHESSI_to_JHV_via_SAMP.ipynb` for the updated version of this file.
