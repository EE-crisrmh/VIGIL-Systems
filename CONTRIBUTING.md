# contributing to vigil systems

how to get the repo on your computer, work in vs code, and push your code. never share your github login with anyone. everyone uses their own account.

---

## 0. one-time setup

1. install **git**: https://git-scm.com/downloads
2. install **vs code**: https://code.visualstudio.com
3. make sure you have your own github account.
4. **send cris your github username.** he adds you as a collaborator (repo > settings > collaborators > add people). you get an email invite. accept it before step 2 below.
5. tell git who you are (use the same email as your github account):

```bash
git config --global user.name "your name"
git config --global user.email "you@example.com"
```

---

## 1. get the repo into vs code

**option a: from vs code (easiest)**

1. open vs code, press `ctrl+shift+p` (mac: `cmd+shift+p`).
2. type `git: clone` and press enter.
3. choose "clone from github" and sign in to **your own** account when it asks.
4. pick `EE-crisrmh/vigil-systems`, choose a folder, then click "open" when it finishes.

**option b: from a terminal**

```bash
git clone https://github.com/EE-crisrmh/vigil-systems.git
cd vigil-systems
code .
```

if git asks you to sign in, use your own github account. if it asks for a password, github wants a personal access token or the github login popup, not your account password. the vs code clone in option a handles this for you.

**no invite yet or not a collaborator?** fork instead: click "fork" on the repo page, clone your fork, then open pull requests from your fork back to this repo.

---

## 2. every time you work

do not commit straight to `main`. work on a branch and open a pull request.

```bash
git checkout main
git pull                          # get everyone's latest changes first
git checkout -b yourname/short-description   # example: abraham/person-detector
```

in vs code you can do the same with the branch name at the bottom left > "create new branch".

make your changes, then save your work:

```bash
git add .
git commit -m "short message about what changed"
git push -u origin yourname/short-description
```

in vs code: source control tab (left bar) > type a message > commit > "publish branch".

then go to the repo on github, click "compare & pull request", write a sentence on what you did, and ask cris (or another teammate) to review. once it is approved, merge it and delete the branch.

---

## 3. where things go

- `hardware/`: custom flight controller v1.0 (kicad, bom, gerbers, assembly)
- `mechanical/`: cad
- `simulation/`: px4 sitl and ros 2 simulation, test data
- `software/`: companion computer code (ml, detection, patrol logic)
- `docs/`: design documents

put your work in the folder for your area. if you need a new folder, make it lowercase.

---

## 4. ground rules

- **small, frequent commits** with clear messages beat one giant commit.
- **pull before you start** and before you push, so you do not overwrite a teammate.
- **no secrets.** never commit passwords, tokens, api keys or wifi credentials.
- **no huge files.** large datasets, videos and model weights do not belong in git. share them in the discord `#files` channel (or ask the team where they should live) and put a link or a short note in the repo.
- **lowercase** folder names and readme text, to match the rest of the repo.
- **do not force push** (`git push --force`) on shared branches.
- if you break something or get a scary git message, stop and ask in the discord instead of trying random commands.

---

## 5. quick fixes

- **"permission denied" or 403 on push:** you are not a collaborator yet, or you are signed in to the wrong github account. check the invite, then sign out and back in inside vs code (accounts icon, bottom left).
- **merge conflict:** two people changed the same lines. vs code shows both versions. keep the right one, save, then `git add .` and commit. ask for help if unsure.
- **pushed to the wrong branch:** tell cris, do not try to undo it yourself.
- **"not a git repository":** you are in the wrong folder. open the `vigil-systems` folder itself.
