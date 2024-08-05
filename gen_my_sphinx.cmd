@echo off

:: sphinx-apidoc: https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html
:: sphinx-build : https://www.sphinx-doc.org/en/master/man/sphinx-build.html

set BARE_OPTIONS=-a --full --force --implicit-namespaces --separate --module-first
set PROJ_NAME=-H dt-console
set AUTHOR=-A JavaWiz1@hotmail.com

poetry run sphinx-apidoc %BARE_OPTIONS% %PROJ_NAME% %AUTHOR% %*

echo.
echo Based on https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
echo.
echo Update conf.py with the following:
echo - extentions - 
echo.    'sphinx.ext.napoleon',
echo.    'sphinx.ext.autosummary',
echo - html_theme = 'sphinx_rtd_theme'