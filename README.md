# FileMover
A simple python script that sorts files in a folder based on file name.  Intended for use with telegram to auto sort files based on the filename but could be adapted to other purposes.

**This code is a work in progress**

# How it works

This script monitors a specified folder for new files, when a file is detected it waits until the file is moveable then it moves it to a different folder based on the filename.
The program reads the filename and looks for certain keywords:  monthly, kickstarter, trove, and warhammer+.  If it finds a keyword it will split the filename
at '-' or '_' characters to determine the name and date for the file.  The file will then be moved into the sort folder with folder hierarchy based on the keyword (and possibly name).  Anything that cant be sorted is put in a folder called unsorted.

E.G.

`c:\input\monthly-code2-2022.01-building.zip`

will be moved to 

`c:\output\monthly\code2\monthly-code2-2022.01-building.zip`

`c:\input\kickstarter-fantasyfootball.zip`

will be moved to 

`c:\output\kickstarter\kickstarter-fantasyfootball.zip`

`c:\input\trove-cgtrader-darkangelsstuff.zip`

will be moved to 

`c:\output\trove\cgtrader\trove-cgtrader-darkangelsstuff.zip`

`c:\input\icantnamethingscorrectly.png`

will be moved to 

`c:\output\unsorted\icantnamethingscorrectly.png`

# Getting Started
1. [install python 3](https://www.python.org/downloads/)
2. update pip `py -m pip install --upgrade pip`
3. install the watchdog package with pip `py -m pip install watchdog`
4. edit the script mover.py (you can just open with notepad or a code editor like vscode or notepad++)
    - set the watch_path (this should be your telegram download path)
    - set the target_path (this is where you want the mover to put the files, it will create sorted subdirectories)
5. setup telegram to auto download 
    - settings -> advanced -> download path -> custom folder (this will be the same as watch_path above)
    - settings -> advanced -> manage local storage -> increase the total size limit & cache limit to 10GB
    - settings -> advanced -> In Groups -> increase Limit by Size to 2000MB also make sure files and photos are checked
6. run mover.py (either by double clicking or open a cmd window and navigate to the location

# Known issues
* the multithreadding doesnt really work
