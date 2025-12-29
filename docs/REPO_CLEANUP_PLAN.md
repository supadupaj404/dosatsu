# Dōsatsu Repository Cleanup Plan

## Current Problems

### 1. **Massive Data Files in Git (268+ MB)**
- `billboard_200_all_time.json` - 113 MB ❌
- `billboard_all_time.json` - 61 MB ❌
- `temp_all_charts.json` - 61 MB ❌
- `billboard_67years.json` - 60 MB ❌
- `billboard_25years.json` - 23 MB ❌
- `billboard_recent.json` - 9 MB ❌
- Plus many more cache/data files

**Problem:** GitHub has a 100 MB file limit. Your repo will fail to push and is bloated.

### 2. **Poor Directory Structure**
Everything is in the root directory:
- 86 files in root
- No organization
- Hard to navigate
- Not beginner-friendly

### 3. **Inadequate .gitignore**
Only ignoring:
- `__pycache__/`, `*.pyc`, `.DS_Store`, `.env`

**Missing:**
- All JSON data files
- Log files
- Cache files
- Temp files

### 4. **Deprecated/Unnecessary Files**
- `arxiv_audio_scraper.py` (not related to Billboard)
- `~$SATSU_OVERVIEW.md` (Mac temp file)
- `business_case_summary.md` (internal doc)
- Multiple duplicate scripts

### 5. **Missing Public-Facing Documentation**
- No clear README for new users
- No installation guide
- No contribution guidelines
- No license

---

## Proposed New Structure

```
dosatsu/
├── README.md                    # Public-facing, friendly intro
├── LICENSE                      # Open source license
├── requirements.txt             # Python dependencies
├── .gitignore                   # Comprehensive exclusions
├── setup.py                     # Optional: pip installable
│
├── src/                         # Main source code
│   ├── __init__.py
│   ├── billboard_downloader.py
│   ├── genre_classifier.py
│   ├── spotify_classifier.py
│   ├── musicbrainz_classifier.py
│   ├── hybrid_classifier.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
│
├── analysis/                    # Analysis scripts
│   ├── genre_tracker.py
│   ├── trend_analyzer.py
│   ├── falloff_analysis.py
│   ├── decade_analysis.py
│   └── year_over_year.py
│
├── dashboard/                   # Streamlit app
│   ├── streamlit_app.py
│   └── .streamlit/
│       └── config.toml
│
├── automation/                  # Automation scripts
│   ├── auto_weekly_update.py
│   ├── setup_automation.sh
│   ├── test_automation.sh
│   └── com.dosatsu.weeklyupdate.plist
│
├── scripts/                     # Utility scripts
│   ├── setup.sh                # First-time setup
│   ├── download_data.sh        # Download Billboard data
│   ├── classify_artists.py     # Genre classification
│   └── test_installation.py    # Verify setup
│
├── docs/                        # Documentation
│   ├── QUICKSTART.md
│   ├── AUTOMATION_GUIDE.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── SPOTIFY_INTEGRATION_GUIDE.md
│   ├── API_REFERENCE.md
│   └── ARCHITECTURE.md
│
├── data/                        # Data files (GITIGNORED)
│   ├── .gitkeep
│   ├── billboard/              # Billboard data
│   │   ├── billboard_all_time.json
│   │   ├── billboard_25years.json
│   │   └── ...
│   ├── cache/                  # Cache files
│   │   ├── spotify_genre_cache.json
│   │   ├── musicbrainz_cache.json
│   │   └── ...
│   └── logs/                   # Log files
│       ├── auto_update.log
│       └── ...
│
├── tests/                       # Unit tests
│   ├── __init__.py
│   ├── test_downloader.py
│   ├── test_classifier.py
│   └── test_analyzer.py
│
└── examples/                    # Example usage
    ├── basic_analysis.py
    ├── custom_insights.py
    └── notebook_demo.ipynb
```

---

## New .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Data Files (CRITICAL)
data/
*.json
!requirements.json
*.csv
*.db
*.sqlite

# Logs
logs/
*.log
auto_update.log
auto_update_stdout.log
auto_update_stderr.log

# Cache
.cache/
*.cache
*_cache.json

# Streamlit
.streamlit/secrets.toml

# Environment
.env
.env.local
.env.*.local

# Temporary files
tmp/
temp/
*.tmp
~$*

# macOS Launch Agents (user-specific)
*.plist

# Downloaded data (regenerated on setup)
billboard_*.json
spotify_*.json
musicbrainz_*.json
youtube_*.json
hybrid_*.json
```

---

## Migration Steps

### Phase 1: Backup & Branch
1. Create backup branch: `git checkout -b backup-messy`
2. Push backup: `git push origin backup-messy`
3. Create cleanup branch: `git checkout -b repo-cleanup`

### Phase 2: Directory Structure
1. Create new directory structure
2. Move files to appropriate locations
3. Update import paths in Python files
4. Test that everything still works

### Phase 3: Update .gitignore
1. Create comprehensive .gitignore
2. Remove all data files from git tracking
3. Add .gitkeep files to preserve empty directories

### Phase 4: Documentation
1. Write new public-facing README.md
2. Create QUICKSTART.md for new users
3. Reorganize existing docs into docs/ folder
4. Add LICENSE file (MIT recommended)

### Phase 5: Setup Scripts
1. Create setup.sh for first-time installation
2. Create download_data.sh to fetch Billboard data
3. Update automation scripts for new paths
4. Add test scripts

### Phase 6: Clean Git History
1. Remove large files from git history
2. Force push to clean repo
3. Verify repo size

### Phase 7: Test & Verify
1. Clone repo in fresh directory
2. Run setup.sh
3. Verify all functionality works
4. Test automation
5. Test dashboard

---

## What Users Will Do (After Cleanup)

### Installation:
```bash
git clone https://github.com/supadupaj404/dosatsu.git
cd dosatsu
./scripts/setup.sh
```

This will:
- Install Python dependencies
- Download Billboard data (~5 seconds)
- Set up cache directories
- Verify installation

### Usage:
```bash
# Run dashboard
streamlit run dashboard/streamlit_app.py

# Enable weekly automation
./automation/setup_automation.sh

# Run analysis
python3 analysis/genre_tracker.py
```

---

## Benefits of This Cleanup

### For Users:
✅ **Easy to understand** - Clear directory structure
✅ **Fast clone** - No huge data files
✅ **Quick setup** - One command installation
✅ **Clear documentation** - Know exactly what to do
✅ **Professional** - Looks like a real open-source project

### For You:
✅ **Easy to maintain** - Organized structure
✅ **No git issues** - No large file problems
✅ **Better collaboration** - Others can contribute
✅ **Modular** - Easy to add features
✅ **Testable** - Proper test structure

### For the Project:
✅ **Scalable** - Can grow without chaos
✅ **Discoverable** - Clear what each part does
✅ **Forkable** - Others can easily fork and modify
✅ **Production-ready** - Ready for real users

---

## Estimated Time

- **Phase 1 (Backup):** 5 minutes
- **Phase 2 (Restructure):** 30 minutes
- **Phase 3 (Gitignore):** 10 minutes
- **Phase 4 (Docs):** 45 minutes
- **Phase 5 (Scripts):** 30 minutes
- **Phase 6 (History):** 15 minutes
- **Phase 7 (Test):** 20 minutes

**Total:** ~2.5 hours for a professional, public-ready repository

---

## Next Steps

Would you like me to:
1. **Execute this cleanup automatically** (I'll do all the work)
2. **Do it step-by-step** (so you can review each change)
3. **Modify the plan first** (if you want changes)

Your call!
