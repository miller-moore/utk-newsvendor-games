# utk-newsvendor-games
Codebase of "gamified survey web applications" facilitating various objectives of academic research in supply chain management at the University of Tennessee, Knoxville.

### Setup workspace and virtual environment (if not already done):
```bash
git clone https://github.com/miller-moore/utk-newsvendor-games
cd utk-newsvendor-games
bash scripts/setup
```

### To run otree (if steps above have been completed):
```bash
# go to the git repository (i.e., the workspace)
cd utk-newsvendor-games
# update local 'master' branch with 'origin/master'
git checkout master # just in case - should already be on 'master' branch
git pull # synchronize local branch
# ensure latest setup
bash scripts/setup
# activate the virtual environment
source venv/bin/activate
# go to the games directory
cd games/
# run otree ...
# if running otree devserver, should be able to open http://localhost:8000/ in a web browser but only if you're running `otree devserver` on your local machine. This is not likely to work on remote machines unless a port is forwarded from your local machine to the remote machine through ssh, which is a topic beyond the scope of this project.
```

### Useful links:
 - [otree source](https://github.com/oTree-org/otree)
 - [otree-core source](https://github.com/oTree-org/otree-core)
 - [z-Tree Home Page (UZH)](https://www.uzh.ch/cmsssl/ztree/en.html)
 - [aqueous-cliffs oTree apps](https://www.otreehub.com/projects/aqueous-cliffs-60932/)
