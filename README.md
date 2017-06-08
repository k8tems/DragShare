# DragShare

![](https://j.gifs.com/Rgz5XO.gif)

### Tested environment
```
windows 10
python2.7  # can't get compiling to work with py3
```

### Files that need to be in the same folder
`twitter.yml` containing api credentials of dummy twitter account for uploading images  
the twitter account has to be public
```
consumer_key: 'consumer_key'
consumer_secret: 'consumer_secret'
access_token_key: 'access_token_key'
access_token_secret: 'access_token_secret'
```
`log.yml` for configuring logging

### Install required packages
```
pip install -r requirements.txt
```

### Running the app
```
main.py
```

### Building the app
Note: building with --onefile option substantially slows down launch
```
set PYINSTALLER=C:\Python27\Scripts\pyinstaller
set TWITTER_SETTINGS=twitter.yml
set LOGGING_SETTINGS=log.yml
build.bat
```

- [x] Tweet specified image
- [x] Compile as executable
- [x] Share specified area of screen
- [x] Select area of screen
- [x] Visualize area
- [x] Add early check for settings and warn via message box
- [x] Prevent multiple launches
- [x] Change cursor when ready
- [x] Create image confirmation window
- [x] Support multi monitor environment
- [x] Somehow notify the user after the upload has been finished
- [x] Log exceptions
- [x] Save image to disk
- [x] Do I/O asynchronously
- [x] Notify user if anything goes wrong with the upload
- [ ] Support google image search
