@echo off

set current_dir=%cd%

rem the path to the python installer executable
set python_installer=%1

rem the path to the git directory for lightcycler
set lightcycler_git_dir=%2

rem the version to install
set lightcycler_version=%3

rem the directory that will contain the python + deps + lightcycler
set target_dir=%4

rem uninstall python
%python_installer% /quiet /uninstall

rem remove(if existing) target directory
rmdir /S /Q %target_dir%

rem create the target directory that will contains the python installation
mkdir %target_dir%

rem install python to the select target directory
%python_installer% /quiet TargetDir=%target_dir%

rem the path to pip executable
set pip_exe=%target_dir%\Scripts\pip.exe

rem install dependencies
%pip_exe% install numpy
%pip_exe% install matplotlib
%pip_exe% install pandas
%pip_exe% install PyQt5
%pip_exe% install openpyxl
%pip_exe% install tabula-py
%pip_exe% install scipy
%pip_exe% install scikit-posthocs
%pip_exe% install xlrd

rem remove unused file for the bundle to reduce its size
rmdir /S /Q %target_dir%\Lib\site-packages\matplotlib\tests
rmdir /S /Q %target_dir%\Lib\site-packages\numpy\tests
rmdir /S /Q %target_dir%\Lib\site-packages\pandas\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\cluster\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\constants\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\fft\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\fftpack\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\integrate\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\interpolate\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\io\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\linalg\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\misc\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\ndimage\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\odr\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\optimize\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\signal\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\sparse\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\spatial\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\special\tests
rmdir /S /Q %target_dir%\Lib\site-packages\scipy\stats\tests

rem the path to python executable
set python_exe=%target_dir%\python.exe

rem cleanup previous installations
cd %target_dir%\Lib\site-packages
for /f %%i in ('dir /a:d /S /B lightcycler*') do rmdir /S /Q %%i
del /Q %target_dir%\Scripts\lightcycler

rem checkout selected version of the lightcycler project
set git_exe="C:\Program Files\Git\bin\git.exe"
cd %lightcycler_git_dir%
%git_exe% fetch --all
%git_exe% checkout %lightcycler_version%

rem build and install lightcycler using the python installed in the target directory
rmdir /S /Q %lightcycler_git_dir%\build
%python_exe% setup.py build install

rem copy the LICENSE and CHANGELOG files
copy %lightcycler_git_dir%\LICENSE %lightcycler_git_dir%\deploy\windows
copy %lightcycler_git_dir%\CHANGELOG.md %lightcycler_git_dir%\deploy\windows\CHANGELOG.txt

rem the path to nsis executable
set makensis="C:\Program Files (x86)\NSIS\Bin\makensis.exe"
set nsis_installer=%lightcycler_git_dir%\deploy\windows\lightcycler_installer.nsi

del /Q %target_dir%\lightcycler-%lightcycler_version%-win-amd64.exe

%makensis% /V4 /Onsis_log.txt /DVERSION=%lightcycler_version% /DARCH=win-amd64 /DTARGET_DIR=%target_dir% %nsis_installer%

cd %current_dir%
