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

# On linux and Mac, we are going to use .ogg audio files, so, we want to remove any .mp3 file present.
# NOTE: preserve all .wav files, because they are SFX
rm ./assets/sounds/*.mp3
rm ./assets/sounds/background/*.mp3

# Create a container folder
mkdir TheAlchemist

# Move everything to the container folder
mv * ./TheAlchemist

# Zipping
zip -r TheAlchemist-lin.zip ./TheAlchemist

mkdir -p ../dist

mv TheAlchemist-lin.zip ../dist
