#!/bin/bash

# upgrade npm
npm install npm -g
# upgrade npm packages
npm update -g

# upgrade pip
pip install -U pip setuptools
pip3 install -U pip setuptools wheel
# upgrade pip packages
pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
pip3 freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

# upgrade brew packages (not including brew-cask)
brew update && brew upgrade && brew cleanup && brew doctor

# upgrade Mac App Store apps
mas upgrade

# upgrade gems
gem install rubygems-update
update_rubygems
gem update --system