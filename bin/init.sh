# Setup the python development environment
pyenv virtualenv fyyur
pip install -r requirements.txt

# Do the required steps to setup the FYYUR database
createdb fyyur
createuser fyyur
flask db upgrade