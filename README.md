# DragShare

### Tested environment
```
windows 10
python2.7  # can't get compiling to work with py3
```

### Required packages
```
twython==3.4.0
pyyaml==3.12
pillow==4.1.1
pyinstaller==3.2.1
quicklock==0.1.7
clipboard==0.0.4
screeninfo==0.3
Desktopmagic==14.3.11
```

### Required files
`twitter.yml` containing api credentials for twitter account
```
consumer_key: 'consumer_key'
consumer_secret: 'consumer_secret'
access_token_key: 'access_token_key'
access_token_secret: 'access_token_secret'
```
`log.conf`
### Running the app
```
main.py
```

### Building the app
Note: building with --onefile option substantially slows down launch
```
C:\Python27\Scripts\pyinstaller main.py
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
- [ ] Somehow notify the user after the upload has been finished
