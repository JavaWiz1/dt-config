@echo off

set BARE_OPTIONS=-a --full --force --implicit-namespaces --separate
set PROJ_NAME=-H dt-console
set AUTHOR=-A JavaWiz1@hotmail.com

poetry run sphinx-apidoc %BARE_OPTIONS% %PROJ_NAME% %AUTHOR% %*
