# utk-newsvendor-games
Codebase of newsvendor games for research in supply chain planner biases.

### Setup workspace and virtual environment (if not already done):
```bash
git clone https://github.com/miller-moore/utk-newsvendor-games
cd utk-newsvendor-games
python3 -m venv venv
source venv/bin/activate
pip -U install pip wheel setuptools
pip install -r requirements.txt
```

### To run otree devserver (if workspace and virtual environment are setup per above instructions):
```bash
# go to the git repository (i.e., the workspace)
cd utk-newsvendor-games 
# update local 'master' branch with 'origin/master'
git checkout master # just in case - should already be on 'master' branch
git pull # synchronize local branch
# activate the virtual environment 
source venv/bin/activate
# go to the app directory
cd utk-games
# run otree
otree devserver
# then, open http://localhost:8000/ in a web browser
```

### Useful links:
 - [otree source](https://github.com/oTree-org/otree)
 - [otree-core source](https://github.com/oTree-org/otree-core)
 - [z-Tree Home Page (UZH)](https://www.uzh.ch/cmsssl/ztree/en.html)
 - [aqueous-cliffs oTree apps](https://www.otreehub.com/projects/aqueous-cliffs-60932/)
