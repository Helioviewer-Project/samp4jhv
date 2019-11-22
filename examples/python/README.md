jhv.vso.load:

> **Arguments**:
> 
> timestamp (string)
> 
> Date of the currently viewed frame coded in the ISO 8601 format  
> (2017-08-28T14:33:28)
> 
> start (string)
> 
> Starting date of the currently viewed sequence coded in the in the ISO
> 8601 format  
> (2017-08-28T14:33:28)
> 
> end (string)
> 
> End date of the currently viewed sequence coded in the ISO 8601
> format  
> (2017-08-28T14:33:28)
> 
> cadence (SAMP long)
> 
> Number of Milliseconds between each frame
> 
> cutout.set (SAMP boolean)
> 
> Wether or not only a part of the sun is visible.  
> 0: The full sun is visible  
> 1: Only a cutout of the sun is visible
> 
> cutout.x0 (SAMP float)
> 
> (OPTIONAL) x-Position of the currently viewed part of the sun in
> arcsec
> 
> cutout.y0 (SAMP float)
> 
> (OPTIONAL) y-Position of the currently viewed part of the sun in
> arcsec
> 
> cutout.w (SAMP float)
> 
> (OPTIONAL) Width of the currently viewed part of the sun in arcsec
> 
> cutout.h (SAMP float)
> 
> (OPTIONAL) Height of the currently viewed part of the sun in arcsec
> 
> layers (list of map)
> 
> The different layers currently displayed. The parameters of each layer
> are stored as a Key-Value Pair with the following Keys:
> 
> observatory (string, required)
> 
> instrument (string, required)
> 
> detector (string, optional)
> 
> measurement (string, optional)
> 
> timestamp (string, required)
> 
> Which Keys are set depends on the selected instrument. The timestamp
> is the date for the specific frame coded in the ISO 8601 format  
> (2017-08-28T14:33:28)
> 
> **Return Values:**
> 
> None
> 
> **Description:**
> 
> Broadcasts information about all the currently visible layers in
> JHelioviewer including the current timestamp of the sun. Other
> application can then use this information to load the raw data from
> VSO for example.

jhv.layers.show:

> **Arguments**:
> 
> date (string)
> 
> Requested date of the new layer  
> (yyyy-MM-dd)
> 
> start (string)
> 
> Start time of the requested layer  
> (HH:mm:ss)
> 
> end (string)
> 
> End time of the requested layer  
> (HH:mm:ss)
> 
> peak (string)
> 
> (OPTIONAL) Time the layer should be displayed at the start  
> (HH:mm:ss)
> 
> cadence (SAMP float)
> 
> (OPTIONAL) the time in seconds between each frame
> 
> xPos (SAMP float)
> 
> (OPTIONAL) x-Position in arcsec that should be displayed
> 
> yPos (SAMP float)
> 
> (OPTIONAL) y-Position in arcsec that should be displayed
> 
> observatory (string)
> 
> (OPTIONAL) TODO
> 
> instrument (string)
> 
> (OPTIONAL) TODO
> 
> detector (string)
> 
> (OPTIONAL) TODO
> 
> measurement (string)
> 
> (OPTIONAL) TODO
> 
> **Return Values:**
> 
> None
> 
> **Description:**
> 
> Tells JHelioviewer to remove all currently visible layers and to
> display a new layer using the given start and end time with frames
> each 12 milliseconds.
> 
> If no information about the instrument and observatory are given, then
> the SDO/AIA 171 instrument will be used. For Dates before 2010-06-02,
> SOHO/EIT 195 will be used instead.
