# GitHub Setup Commands

## After creating repository on GitHub.com:

Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPO_NAME` with your actual values:

```bash
# Add GitHub as remote origin
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git

# Rename branch to main (GitHub standard)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Example (replace with your actual details):
```bash
git remote add origin https://github.com/sifisos/derivco-stores-infrastructure-admin.git
git branch -M main
git push -u origin main
```

## Verify setup:
```bash
git remote -v
git status
```

## Future commits:
```bash
git add .
git commit -m "Your commit message"
git push
```