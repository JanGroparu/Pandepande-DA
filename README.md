# INSTALLATION
Just download the source code and run the shortcut launcher. Alternatively, if you want a shortcut on the desktop, just right click on the shortcut in the source code and select `send to` -> `Desktop`

# DATA STRUCTURE
When entering a new run into the data set, you must add the new line: `0 100 N/A`

The first value represents the time in seconds since the start of the run. The second value is the last door opened, and the last value is the monster type encountered. Please use this format as any others can break the script.

> *Note: The monster types are case sensitive and are comprised of the following: 
Angler, Blitz, Frogger, Pinkie, Chainsmoker, Pande, Mirage and A60*

A simple example would be an **Angler** spawn at door **93**, **45** seconds in.
In this case, the data entry would look like:
```events.txt
45 93 Angler
```
These entries are separated by new lines created by pressing the **Enter** key.

