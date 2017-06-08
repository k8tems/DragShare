set PYINSTALLER=C:\Python27\Scripts\pyinstaller
set APP_NAME=dragshare
set RELEASE_DIR=dist\release
set DEST_DIR=%RELEASE_DIR%\%APP_NAME%
set LOADING_GIF=loading.gif
set TWITTER_SETTINGS=settings\twitter.yml
set LOGGING_SETTINGS=settings\logging\release.yml
%PYINSTALLER% main.py -n %APP_NAME% --specpath build --noconsole --distpath %RELEASE_DIR%
copy %LOADING_GIF% %DEST_DIR%\loading.gif
copy %TWITTER_SETTINGS% %DEST_DIR%\twitter.yml
copy %LOGGING_SETTINGS% %DEST_DIR%\log.yml
