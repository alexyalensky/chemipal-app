# Git Branching Strategy for ChemiPal Project

## Overview

This document defines the **issue-driven branching workflow** for managing the ChemiPal Integration System project.

## Our Workflow

**The Procedure:**
1. Create an Issue on GitHub
2. Create a branch for the issue
3. Develop the required code on this branch
4. Merge to main when finished

**Simple. Clean. Effective.**

---

## Branch Structure

```
main (production-ready code)
│
├── development (main development branch)
│   ├── feature/add-new-customer
│   ├── feature/improve-validation
│   └── feature/add-logging
│
├── hotfix (emergency fixes to main)
│   ├── hotfix/critical-bug-xyz
│   └── hotfix/security-patch
│
└── documentation (documentation updates)
    └── docs/update-instructions
```

---

## Branch Types

### 1. **main**
- **Purpose**: Production-ready code
- **Protection**: Should not be pushed to directly
- **Updates**: Only via merge from development or hotfix branches
- **Deployment**: Use for production deployment

### 2. **development**
- **Purpose**: Main development branch
- **Protection**: Can be worked on by team members
- **Updates**: Regular feature merges
- **Deployment**: Use for staging/testing

### 3. **feature/** (branches)
- **Purpose**: New features, improvements
- **Examples**:
  - `feature/add-namal-process`
  - `feature/improve-error-handling`
  - `feature/add-new-validation`
- **Merge**: Into development, then to main

### 4. **hotfix/** (branches)
- **Purpose**: Critical production fixes
- **Examples**:
  - `hotfix/fix-memory-leak`
  - `hotfix/security-patch`
  - `hotfix/urgent-bug-fix`
- **Merge**: Into main immediately, then back to development

### 5. **docs/** (branches)
- **Purpose**: Documentation updates
- **Examples**:
  - `docs/update-instructions`
  - `docs/add-troubleshooting`
- **Merge**: Into development, then to main

---

## Initial Branch Setup

Here are the commands to set up your branches:

```powershell
# Create development branch from main
git checkout -b development

# Push development branch
git push -u origin development

# Create initial feature branches structure
git checkout -b feature/documentation-updates
git checkout development

git checkout -b docs/maintenance
git checkout development

# Return to main
git checkout main
```

---

## Workflow Examples

### Adding a New Feature

```powershell
# 1. Start from development
git checkout development
git pull origin development

# 2. Create feature branch
git checkout -b feature/add-customer-x

# 3. Make changes
# Edit files...

# 4. Commit changes
git add .
git commit -m "Feature: Add customer X configuration

- Added new HitoAPI instance
- Configured volunteer transfer
- Updated documentation"

# 5. Push feature branch
git push -u origin feature/add-customer-x

# 6. Create Pull Request on GitHub
# (or merge directly)
git checkout development
git merge feature/add-customer-x
git push origin development

# 7. After testing, merge to main
git checkout main
git merge development
git push origin main

# 8. Delete feature branch
git branch -d feature/add-customer-x
git push origin --delete feature/add-customer-x
```

### Hotfix (Emergency Fix)

```powershell
# 1. Start from main
git checkout main
git pull origin main

# 2. Create hotfix branch
git checkout -b hotfix/fix-critical-bug

# 3. Fix the issue
# Edit files...

# 4. Commit and push
git add .
git commit -m "Hotfix: Fix critical bug in validation logic"
git push -u origin hotfix/fix-critical-bug

# 5. Merge to main immediately
git checkout main
git merge hotfix/fix-critical-bug
git push origin main

# 6. Merge back to development
git checkout development
git merge main
git push origin development

# 7. Delete hotfix branch
git branch -d hotfix/fix-critical-bug
git push origin --delete hotfix/fix-critical-bug
```

### Documentation Updates

```powershell
# 1. Create docs branch
git checkout -b docs/update-instructions

# 2. Update documentation
# Edit .md files...

# 3. Commit and push
git add .
git commit -m "Docs: Update installation instructions

- Added troubleshooting section
- Updated configuration examples
- Fixed broken links"

git push -u origin docs/update-instructions

# 4. Merge to development
git checkout development
git merge docs/update-instructions
git push origin development

# 5. Delete docs branch
git branch -d docs/update-instructions
git push origin --delete docs/update-instructions
```

---

## Branch Naming Conventions

### Feature Branches
- `feature/` prefix
- Use kebab-case
- Example: `feature/add-volunteer-validation`

### Bug Fixes
- `bugfix/` prefix
- Example: `bugfix/fix-id-validation`

### Hotfixes
- `hotfix/` prefix
- Example: `hotfix/critical-security-fix`

### Documentation
- `docs/` prefix
- Example: `docs/update-readme`

### Experiments
- `experiment/` prefix
- Example: `experiment/new-validation-approach`

---

## Branch Protection Rules

Recommended rules for GitHub:

1. **main branch**:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   - ✅ Require linear history (no merge commits)
   - ✅ Do not allow force pushes

2. **development branch**:
   - ✅ Allow force pushes (for rebasing)
   - ⚠️ Require status checks

---

## Regular Maintenance Tasks

### Weekly Cleanup

```powershell
# Update all branches
git checkout main
git pull origin main

git checkout development  
git pull origin development

# List all branches
git branch -a

# Delete merged branches
git branch --merged | grep -v "\*\|main\|development" | xargs git branch -d
```

### Before Creating New Branch

```powershell
# Always start with latest code
git checkout main
git pull origin main
git checkout development
git pull origin development
```

---

## AI Assistance Commands

### I Will Help You With:

✅ Creating branches  
✅ Merging branches  
✅ Resolving conflicts  
✅ Pushing to GitHub  
✅ Deleting old branches  
✅ Updating documentation  

### Just Tell Me:

- "Create a feature branch for X"
- "Merge feature X to development"
- "Push changes to GitHub"
- "Delete old feature branches"

---

## Current Branch Status

Your repository currently has:
- ✅ **main** branch (production)
- ⚠️ No **development** branch yet

### Recommended Next Steps:

1. Create development branch
2. Set up initial feature branches
3. Configure branch protection rules on GitHub

---

## Quick Reference

```powershell
# Create new feature branch
git checkout -b feature/name

# Switch branches
git checkout branch-name

# Merge branch
git merge branch-name

# Delete local branch
git branch -d branch-name

# Delete remote branch
git push origin --delete branch-name

# See all branches
git branch -a

# See current branch
git branch --show-current
```

---

**Ready to set up branches?** Tell me which branches you want to create and I'll set them up for you!

