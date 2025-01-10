# dogcat.star

This is a project with playwright altomation to dogcat.star website

## Set up
```
sh scripts/setup.sh
```
Enter poetry
```
poetry shell
```
For more commands for poetry, see https://python-poetry.org/docs/cli/

Test Codegen, If all goes well, that should open two windows.
```
playwright codegen google.com
```
Run Pytest DEBUG mode
```
PWDEBUG=1 pytest -m “app-smoke”
```

### Install and setting XQuartz
1. Install XQuartz in local device 
```
brew install --cask xquartz
```
2. Open XQuartz, go to Preferences -> Security, and check “Allow connections from network clients”
3. Restart your computer (restarting XQuartz might not be enough)
4. Start XQuartz by local Terminal
```
xhost +localhost
```
## Execute
Execute the playwright with pytest print out
```
pytest -s -m “login”
```

## TestRail integration
Update test result to testrail
```
python testrail.py -run_id=<your_test_run_id>
```
