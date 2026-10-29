@echo off
cd /d "%~dp0"
py -3 tools\weekly_refresh.py --apply-approved
if errorlevel 1 (
  echo Refresh failed. Read the error above; do not upload partial output.
) else (
  echo Open weekly-output\REPORT.txt and weekly-output\weekly-upload.zip
)
pause
