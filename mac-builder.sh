#!/bin/bash

# Remove old files
rm -rf ./__pycache__

# Generate .pyc files
python -m compileall .

# Move some files that will be needed during the instalation on the target.
cp -r ./assets README.md Makefile Pipfile* ./__pycache__

# Move into the compiled files directory
cd ./__pycache__

# Removing the .cpython-39 substring from compiled files.
for path in $(ls *.cpython-39.pyc)
do
  mv $path $(echo $path | sed 's/.cpython-39//g')
done

# Create a container folder
mkdir TheAlchemist

# Move everything to the container folder
mv * ./TheAlchemist

# Zipping
zip -r TheAlchemist-mac.zip ./TheAlchemist

mkdir -p ../dist

mv TheAlchemist-mac.zip ../dist