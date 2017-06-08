set PYINSTALLER=C:\Python27\Scripts\pyinstaller
set APP_NAME=dragshare
set DIST_DIR=dist\release
set APP_DIR=%DIST_DIR%\%APP_NAME%
set LOADING_GIF=loading.gif
set TWITTER_SETTINGS=settings\twitter.yml
set LOGGING_SETTINGS=settings\logging\release.yml
%PYINSTALLER% main.py -n %APP_NAME% --specpath build --noconsole --distpath %DIST_DIR%
copy %LOADING_GIF% %APP_DIR%\loading.gif
copy %TWITTER_SETTINGS% %APP_DIR%\twitter.yml
copy %LOGGING_SETTINGS% %APP_DIR%\log.yml
