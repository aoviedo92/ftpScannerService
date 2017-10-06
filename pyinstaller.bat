@echo off
set name=ftpIndexService
set script=app.py
C:\Python34\Scripts\pyinstaller -n %name% -F -i icon.ico %script%
copy /y "D:\adri\work\PycharmProjects\ftpScannerService\dist\ftpIndexService.exe" "D:\adri\work\node\MyFTPsearch\app\ftpIndexService.exe"
rem start dist
exit