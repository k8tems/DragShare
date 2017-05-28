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
pillow=4.1.1
pyinstaller==3.2.1
quicklock==0.1.7
screeninfo==0.3
```

### Required files
`settings.yml` taking the following format
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
```
C:\Python27\Scripts\pyinstaller main.py --onefile
```

- [x] Tweet specified image
- [x] Compile as executable
- [x] Share specified area of screen
- [x] Select area of screen
- [x] Visualize area
- [x] Add early check for settings and warn via message box
- [x] Prevent multiple launches
- [x] Change cursor when ready
- [ ] Create image confirmation window
- [ ] Persist
