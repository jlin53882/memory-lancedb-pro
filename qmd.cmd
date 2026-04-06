@echo off
setlocal

REM QMD launcher for Windows (Node)
REM Uses the globally installed npm package: %APPDATA%\npm\node_modules\@tobilu\qmd

set "QMD_JS=%APPDATA%\npm\node_modules\@tobilu\qmd\dist\qmd.js"

if not exist "%QMD_JS%" (
  echo [qmd.cmd] ERROR: Cannot find %QMD_JS%
  echo [qmd.cmd] Try: npm i -g @tobilu/qmd
  exit /b 1
)

node "%QMD_JS%" %*
