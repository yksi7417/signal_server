# Autonomous Development Setup Checklist

## ✅ Prerequisites

### 1. Environment
- [ ] Python 3.8.3 installed
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] PyGithub 2.8.1 or higher
- [ ] GitHub CLI (`gh`) installed and authenticated

### 2. GitHub Configuration
- [ ] GITHUB_TOKEN set in `.env` file
- [ ] Token has `repo` scope permissions
- [ ] Repository: `yksi7417/signal_server`
- [ ] Can create issues: `gh issue list --repo yksi7417/signal_server`
- [ ] Can create gists: `gh gist list`

### 3. Git Configuration
- [ ] Git user.name configured
- [ ] Git user.email configured
- [ ] SSH key or HTTPS credentials set up
- [ ] Can push to repository
- [ ] Working on feature branch (not main)

### 4. Testing
- [ ] All current tests pass: `pytest -m "not integration" -v`
- [ ] Test count: ~215 tests (as of 2026-02-07)
- [ ] No syntax errors: `python -m py_compile mahjong_engine/*.py app.py`

## ✅ Documentation Created

- [x] `LEARNINGS.md` - Comprehensive learnings from today's session
- [x] `AUTONOMOUS_DEV_LOOP.md` - Detailed autonomous workflow guide
- [x] `AUTONOMOUS_PROMPT.md` - Ready-to-use prompt templates
- [x] `SETUP_CHECKLIST.md` - This file
- [x] `scripts/autonomous_loop.sh` - Helper script for iterations
- [x] Updated `MEMORY.md` with autonomous instructions

## ✅ Quick Test

Run this to verify everything works:

```bash
# 1. Check GitHub connection
gh auth status

# 2. List open bugs
gh issue list --repo yksi7417/signal_server --label bug --state open

# 3. Run tests
pytest -m "not integration" -v tests/engine/

# 4. Check git status
git status

# 5. Verify Claude Code can access project
# (Claude should be able to read MEMORY.md)
```

## 🚀 Ready to Start!

### Option 1: Manual Single Bug Fix
```
Fix the most recent auto-reported bug. Show me each step and wait for approval.
```

### Option 2: Semi-Autonomous (Recommended First Time)
```
Start autonomous loop. Fix one bug at a time, and ask me after each whether to continue.
```

### Option 3: Full Autonomous
```
Start autonomous bug fix loop. Work through all open bugs. Max 5 iterations. Report when done.
```

## 📊 Monitoring

### During Autonomous Operation

**Terminal 1** (Claude Code):
- Running the autonomous loop

**Terminal 2** (Monitoring):
```bash
# Watch tests
watch -n 5 'pytest -m "not integration" -q 2>&1 | tail -5'

# Watch git
watch -n 5 'git log --oneline -5'

# Watch bugs
watch -n 30 'gh issue list --repo yksi7417/signal_server --label bug --state open'
```

### After Completion

```bash
# Check what was done
git log --oneline --since="1 hour ago"

# See test coverage
pytest --cov=mahjong_engine tests/engine/

# Check remaining bugs
gh issue list --repo yksi7417/signal_server --label bug --state open
```

## 🛑 Emergency Procedures

### If Claude Gets Stuck
```
STOP autonomous loop. Show me:
1. What you were working on
2. Git status
3. Last test output
```

### If Tests Fail
```bash
# Revert last commit
git reset --soft HEAD~1

# Check what changed
git diff

# Run specific test
pytest tests/engine/test_<specific>.py -v
```

### If Git Conflicts
```
STOP. There's a git conflict. Show me git status and the conflicted files.
```

## 📝 Post-Session Checklist

After autonomous operation:

- [ ] Review all commits made
- [ ] Verify all tests still pass
- [ ] Check code quality of fixes
- [ ] Review GitHub issue comments
- [ ] Merge feature branch if ready
- [ ] Update LEARNINGS.md with new discoveries
- [ ] Plan next session

## 💡 Tips for Success

1. **Start Supervised**: Watch the first few iterations
2. **Set Limits**: Use `max_iterations` parameter
3. **Monitor Closely**: Check commits and tests
4. **Trust but Verify**: Review code quality
5. **Learn Patterns**: Update MEMORY.md with discoveries
6. **Iterate**: Gradually increase autonomy

## 📚 Reference Files

- **MEMORY.md** - Claude's persistent memory (auto-loaded)
- **LEARNINGS.md** - Today's detailed learnings
- **AUTONOMOUS_DEV_LOOP.md** - Full workflow documentation
- **AUTONOMOUS_PROMPT.md** - Copy-paste prompts
- **scripts/autonomous_loop.sh** - Automation helper

## 🎯 Success Criteria

Autonomous operation is successful when:
- ✅ All tests pass after each bug fix
- ✅ Commits have clear, descriptive messages
- ✅ GitHub issues are properly updated
- ✅ Code quality is maintained
- ✅ No regressions introduced
- ✅ Each fix has corresponding test

## 🏁 You're Ready!

Everything is set up. Choose your approach:

1. **Cautious** → "Fix one bug, show me each step"
2. **Balanced** → "Fix bugs one at a time, ask after each"
3. **Autonomous** → "Fix all bugs, max 10 iterations, report when done"

Good luck! 🚀
