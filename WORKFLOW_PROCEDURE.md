# Our Development Workflow Procedure

## The Process

```
1. Create Issue on GitHub
           ↓
2. Create Branch for Issue
           ↓
3. Develop Code on Branch
           ↓
4. Merge to main
           ↓
5. Close Issue
```

**Simple. Clean. Effective.**

---

## Step-by-Step Procedure

### Step 1: Create an Issue on GitHub

**What**: Define what needs to be done

**Examples**:
- "Add logging to volunteer transfer process"
- "Fix ID validation bug"
- "Document new customer configuration"
- "Update error handling in main_processes"

**How**:
1. Go to https://github.com/alexyalensky/chemipal-app/issues
2. Click "New Issue"
3. Fill in:
   - **Title**: Clear description
   - **Description**: Details of what needs to be done
   - **Labels**: feature, bug, documentation, etc.
4. Click "Submit new issue"
5. **Note the issue number** (e.g., #3)

### Step 2: Create a Branch for the Issue

**Naming Convention**: `issue-[number]-[description]`

**Example**: `issue-3-add-logging-to-volunteer-transfer`

**Commands**:
```powershell
# Make sure you're on main and up to date
git checkout main
git pull origin main

# Create branch
git checkout -b issue-3-add-logging-to-volunteer-transfer

# Push to GitHub
git push -u origin issue-3-add-logging-to-volunteer-transfer
```

### Step 3: Develop the Required Code

**On the branch, make your changes**:

```powershell
# Edit files...

# Stage changes
git add .

# Commit with reference to issue
git commit -m "Add logging to volunteer transfer process

- Added detailed logging for ID validation
- Log successful transfers
- Log validation failures

Fixes #3"

# Push changes
git push
```

**Commit Message Format**:
```powershell
git commit -m "Brief description

- Bullet point of changes
- Another bullet point

Fixes #3"
```

### Step 4: Merge to main

**When you're done developing**:

```powershell
# Switch to main
git checkout main

# Pull latest changes
git pull origin main

# Merge your branch
git merge issue-3-add-logging-to-volunteer-transfer

# Push to main
git push origin main
```

### Step 5: Close the Issue

**On GitHub**:
1. Go to your issue
2. Click "Close with comment"
3. Add: "Merged to main"

**Delete the branch**:
```powershell
# Delete local branch
git branch -d issue-3-add-logging-to-volunteer-transfer

# Delete remote branch
git push origin --delete issue-3-add-logging-to-volunteer-transfer
```

---

## Workflow Examples

### Example 1: Adding a New Feature

**Issue #1**: "Add Namal data transfer documentation"

**Create branch**:
```powershell
git checkout main
git pull origin main
git checkout -b issue-1-add-namal-documentation
git push -u origin issue-1-add-namal-documentation
```

**Develop**:
```powershell
# Create NAMAL_BUSINESS_PROCESS.md
# Edit, write documentation

git add NAMAL_BUSINESS_PROCESS.md
git commit -m "Add Namal data transfer documentation

- Documented Entity 105 → 62 transfer
- Documented Entity 106 → 102 transfer
- Added validation logic
- Added error handling examples

Fixes #1"

git push
```

**Merge**:
```powershell
git checkout main
git pull origin main
git merge issue-1-add-namal-documentation
git push origin main

# Delete branch
git branch -d issue-1-add-namal-documentation
git push origin --delete issue-1-add-namal-documentation
```

### Example 2: Fixing a Bug

**Issue #2**: "Fix ID validation issue in volunteer transfer"

**Create branch**:
```powershell
git checkout main
git checkout -b issue-2-fix-id-validation
git push -u origin issue-2-fix-id-validation
```

**Develop**:
```powershell
# Fix the bug in helpers.py
git add helpers.py
git commit -m "Fix: Update ID validation to handle zero values

- Changed validation to reject zero IDs
- Updated error messages
- Added logging for invalid IDs

Fixes #2"

git push
```

**Merge**:
```powershell
git checkout main
git merge issue-2-fix-id-validation
git push origin main

# Clean up
git branch -d issue-2-fix-id-validation
git push origin --delete issue-2-fix-id-validation
```

---

## Branch Naming Rules

### Format
```
issue-[number]-[short-description]
```

### Examples
- ✅ `issue-5-fix-memory-leak`
- ✅ `issue-10-add-error-handling`
- ✅ `issue-15-update-documentation`
- ❌ `bug-fix` (no issue number)
- ❌ `feature1` (no issue reference)
- ❌ `fixit` (no structure)

### Why This Format?
- Clear reference to GitHub issue
- Easy to track in git log
- Easy to find related code
- Consistent naming

---

## Quick Commands Reference

### Start New Issue
```powershell
git checkout main
git pull origin main
git checkout -b issue-[NUMBER]-[description]
```

### During Development
```powershell
git add .
git commit -m "Description

Details

Fixes #[NUMBER]"

git push
```

### Finish Issue
```powershell
git checkout main
git pull origin main
git merge issue-[NUMBER]-[description]
git push origin main

# Clean up
git branch -d issue-[NUMBER]-[description]
git push origin --delete issue-[NUMBER]-[description]
```

---

## Branch Organization

### Current Branch Structure
```
main (always production-ready)
├── issue-1-add-namal-documentation (in progress)
├── issue-2-fix-id-validation (in progress)
└── issue-3-add-logging (completed, merged)
```

### Working on Multiple Issues
```powershell
# Issue #1
git checkout -b issue-1-feature-a
# ... work on issue 1

# Issue #2  
git checkout main
git checkout -b issue-2-feature-b
# ... work on issue 2

# Switch between them
git checkout issue-1-feature-a
# ... continue issue 1
```

---

## AI Assistant Role

### I Will Handle:
✅ Creating branches from issues  
✅ Committing with proper messages  
✅ Merging to main  
✅ Pushing to GitHub  
✅ Deleting merged branches  
✅ Coordinating with you  

### Just Say:
- "Create issue #5 for adding feature X"
- "Create branch for issue #5"
- "Merge issue #5 to main"
- "List open issues"

---

## Main Branch Protection

**Rule**: main should always be stable and deployable

**Before merging to main**:
1. ✅ Test your changes
2. ✅ Code is working
3. ✅ Documentation updated
4. ✅ No breaking changes

**Merge to main** = "This code is ready for production"

---

## Issue Templates

### Bug Report Template
```
**Description**
What went wrong?

**Steps to Reproduce**
1. 
2. 
3.

**Expected Behavior**
What should happen?

**Actual Behavior**
What actually happened?

**Environment**
- System: 
- Python version:
```

### Feature Request Template
```
**Description**
What feature do you want?

**Why is this needed?**
Business reason

**Proposed Solution**
How should it work?
```

---

## Summary

**Our Simple Workflow**:

1. 📝 **Create Issue** → Describe what needs doing
2. 🌿 **Create Branch** → `issue-[number]-[description]`
3. 💻 **Develop** → Make changes, commit frequently
4. ✅ **Merge to main** → When ready for production
5. 🧹 **Clean up** → Delete branch, close issue

**That's it!** Simple, trackable, professional.

---

**Ready to start?** Create your first issue and I'll help you set up the branch!

