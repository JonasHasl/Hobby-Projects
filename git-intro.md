# Essential Git Commands Cheat Sheet

## 1. Setting Up Your Git Profile (Locally)

Configure your name and email (required for commits):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

User credentials and default branch
```bash
git config --global user.name

git config --global user.email

git config --global init.defaultBranch main


```

Check your configuration:

```bash
git config --list
```

Open folder in vscode:
```
code .

```

U : Untracked, havent moved them to the staging area. No changes made.




## Extra: Git Workflow
<img width="1901" height="991" alt="{745D30F9-1FC7-4300-A0F5-E54297E47FCE}" src="https://github.com/user-attachments/assets/4bf8d905-3dd9-439d-8cea-4dfbdc19a638" />

<img width="546" height="221" alt="image" src="https://github.com/user-attachments/assets/3d2927f8-408f-4dd2-a751-821d5e522deb" />

<img width="553" height="298" alt="image" src="https://github.com/user-attachments/assets/56bcb3e2-9394-49c8-b0f6-83a8142a9ef0" />



<img width="905" height="391" alt="image" src="https://github.com/user-attachments/assets/0f242959-b2e4-458a-b11f-28ad12a901f4" />

Forking: "Clone another repo into your own account as a repo you can work with".

## 2. Cloning a Repository

Clone a remote repository to your local machine:

```bash
git clone https://github.com/username/repository.git
```


## 3. Checking Repository Status

See which files are changed, staged, or untracked:

```bash
git status
```


## 4. Adding and Committing Changes

Stage changes for commit:

```bash
git add filename         # Add a specific file
git add .                # Add all changed files
```

Commit staged changes with a message:

```bash
git commit -m "Describe your changes"
```


## 5. Working with Branches

### Create a New Branch

```bash
git branch new-branch-name
```


### Switch to a Branch

```bash
git checkout branch-name
```

Or, create and switch to a new branch in one command:

```bash
git checkout -b new-branch-name
```
Delete branch

```bash

git branch -d feature/login
```

### List All Branches

```bash
git branch
```


## 6. Merging Branches

Merge another branch into your current branch:

```bash
git merge branch-to-merge
```


## 7. Pulling and Pushing Changes

### Pull Latest Changes from Remote

```bash
git pull
```


### Push Local Commits to Remote

```bash
git push
```

Push a new branch to remote:

```bash
git push -u origin branch-name
```


## 8. Viewing Commit History

```bash
git log
```


## 9. Creating a Pull Request

> **Note:** Pull requests are created via GitHub, GitLab, or similar platforms—not directly in Git.

**Basic steps:**

1. Push your branch to the remote repository.
2. Go to the repository on GitHub/GitLab.
3. Click "New Pull Request" or "Merge Request".
4. Select your branch and the target branch (e.g., `main`).
5. Submit the pull request.

## 10. Helpful Shortcuts

- Discard local changes in a file:

```bash
git checkout -- filename
```

- Remove a file from staging:

```bash
git reset HEAD filename
```


*This cheat sheet covers the most essential commands for daily Git usage, from setup to collaboration.*

