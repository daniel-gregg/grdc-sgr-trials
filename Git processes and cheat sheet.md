# Git ‘cheat sheet’ (basic version)

Git is the key mechanism that allows us to undertake distributed coding within a team. There are some critical rules to abide by to ensure that your work can easily be integrated into the core codeset used by your team and that those integrations are low-risk in terms of over-writing important code being developed by others.

Git processes work as shown below.

![GIT Branch and its An Easy Understanding Digital Varys](media/3f47d27bced18e909aa1f0d906b92c4d.png)

This cheat sheet provides the core commands you will use and describes the processes you should follow.

## Daily activities:

1.  Check that you are on the target branch

*If target branch is main this is only for updating and initiating a new feature branch*

1.  Update your local project folder by pulling down from the online repository using ‘git pull’ on the command line
    1.  Branch out to your new feature branch using ‘git checkout -b new-feature’ where ‘new-feature’ is the name of your new feature branch

*If you are already working on a feature:*

1.  Check that you are in the correct branch (this will be indicated at the end of the current directory line in the terminal)

    *If you are working in a team on that feature branch:*

2.  Use ‘git pull’ to pull down any updates your team has developed in that feature branch
3.  Initiate your coding and undertake regular commits to ensure you can trace back changes using:
    1.  ‘git add .’ to add current non-indexed changes to the index (note the ‘.’)
        1.  “git commit -m ‘your commit message’” to commit the changes for pushing to the repository. Enure ‘your commit message’ is meaningful and easily understood by your team and future self
        2.  ‘git push’ to push the committed changes up to the repository

*At the end of each day or on completion of a feature update:*

1.  Add, commit and push changes to the repository
    1.  ‘git add .’ to add current non-indexed changes to the index (note the ‘.’)
        1.  “git commit -m ‘your commit message’” to commit the changes for pushing to the repository. Enure ‘your commit message’ is meaningful and easily understood by your team and future self
        2.  ‘git push’ to push the committed changes up to the repository

## Key operations:

| Command                             | Usage                                                                               | Comments                                                                                                                                                                                                                                                                                                                                                              |
|-------------------------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| git fetch                           | Check if the online repository is ‘ahead’ of your local machine in terms of changes | Provides a check if the online repo has changes that are not included on your local machine. This does not pull the changes down so is ‘safe’ with respect to your local code.  If the online repo *is* ahead of your current branch then continuing to code in that branch without using ‘git pull’ will likely result in conflicts that need to be manually fixed.  |
| git pull                            | Pull down the online repository changes that are not on your local machine          | If there is a conflict you will need to choose whether to overwrite your local code conflicts with the online version or resolve conflicts manually. Try to avoid conflicts by ensuring your branch out and commit regularly.                                                                                                                                         |
| git branch existing-branch          | Move to ‘existing-branch’                                                           | This switches your coding environment to the target branch. This is only possible if the current branch exists. This is typically used when you are moving back to main branch after pushing final changes to a new feature and requested review for that to be pulled to main branch.                                                                                |
| git branch -b new-branch            | Create and move to a ‘new-branch’                                                   | This creates a new branch and moves your coding environment to that. It will copy across all current code from the branch that you are starting on to your new feature branch.                                                                                                                                                                                        |
| git add .                           | Add your current changes to the local index of changes for committing               | Adds tracked changes to the index for commital                                                                                                                                                                                                                                                                                                                        |
| git commit -m ‘informative message’ | Commits indexed changes for pushing up to the online repository.                    | Ensure your message is highly informative about the substance of updates being commited                                                                                                                                                                                                                                                                               |
| git push                            | Push changes up to your online branch                                               | This will update the online repo branch with your committed changes. NOTE: if this is the first commit on a new branch you will receive an error message telling you need to create the origin branch online. Git will provide the exact input you need so just copy that and re-push using that input.                                                               |

:

git fetch
