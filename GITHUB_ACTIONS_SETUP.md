# GitHub Actions Workflow Setup Guide

## 🚀 Quick Setup

Due to GitHub App permission restrictions, the workflow files have been placed in the `github-workflows-backup/` directory. Follow these steps to activate the GitHub Actions workflows:

### Step 1: Activate Workflows

```bash
# Navigate to your repository
cd your-tv-bro-repository

# Create the workflows directory
mkdir -p .github/workflows

# Copy workflow files
cp github-workflows-backup/* .github/workflows/

# Commit the workflows
git add .github/workflows/
git commit -m "feat: Activate GitHub Actions CI/CD workflows"
git push origin master
```

### Step 2: Configure Repository Secrets (Optional - for signed releases)

Go to your repository settings → Secrets and variables → Actions, and add:

```
RELEASE_KEYSTORE_BASE64    # Base64 encoded keystore file
KEYSTORE_PASSWORD          # Your keystore password  
KEY_ALIAS                  # Your key alias
KEY_PASSWORD              # Your key password
```

To create a Base64 encoded keystore:
```bash
base64 -i your-keystore.jks -o keystore.txt
# Copy the contents of keystore.txt to RELEASE_KEYSTORE_BASE64
```

## 📋 Available Workflows

### 1. 🔨 `build-apk.yml` - Main Build Workflow
**Purpose**: Builds APK files for all flavors and variants

**Triggers:**
- Push to master/main/develop/genspark_ai_developer branches
- Pull requests to master/main
- Manual dispatch with custom parameters

**Features:**
- ✅ Matrix builds: 3 flavors × 2 build types = 6 variants
- ✅ Automatic artifact upload (30-90 day retention)
- ✅ Release creation on version tags
- ✅ Security analysis with Qodana
- ✅ Support for manual builds with custom parameters

**Manual Trigger Example:**
```bash
# Using GitHub CLI
gh workflow run build-apk.yml -f build_type=release -f flavor=generic

# Or use the GitHub web interface:
# Go to Actions → Build Android APK → Run workflow
```

### 2. 🔄 `ci.yml` - Continuous Integration
**Purpose**: Comprehensive testing and validation

**Triggers:**
- Push to main branches (ignores markdown files)
- Pull requests
- Daily schedule at 2 AM UTC

**Features:**
- ✅ Multi-API level testing (Android 7.0 to 14)
- ✅ All build flavors validation
- ✅ Unit test execution
- ✅ Lint analysis
- ✅ Security vulnerability scanning
- ✅ Documentation validation
- ✅ APK size monitoring

### 3. 📝 `pr-check.yml` - Pull Request Quality Check
**Purpose**: Fast quality validation for pull requests

**Triggers:**
- Pull request opened/updated/ready for review

**Features:**
- ✅ Quick build verification
- ✅ Unit test execution
- ✅ Code quality analysis
- ✅ APK size comparison with base branch
- ✅ Automated PR status comments
- ✅ Performance impact analysis

### 4. 🚀 `release.yml` - Release Build & Deploy
**Purpose**: Create official releases with signed APKs

**Triggers:**
- Version tags (v*.*.*)
- GitHub release events
- Manual dispatch

**Features:**
- ✅ Signed release APK generation
- ✅ Multi-architecture builds
- ✅ Automatic GitHub release creation
- ✅ Release notes generation
- ✅ Version file updates

**Release Process:**
```bash
# Tag a new version
git tag v2.0.2
git push origin v2.0.2

# Or create via GitHub CLI
gh release create v2.0.2 --generate-notes
```

## 🛠️ Build Variants

### Build Flavors
| Flavor | Target | Package ID | Features |
|--------|--------|------------|----------|
| **generic** | General devices | `com.phlox.tvwebbrowser` | All features, Firebase, Auto-update |
| **google** | Google Play | `com.phlox.tvwebbrowser` | Firebase, No auto-update |
| **foss** | F-Droid/FOSS | `com.phlox.tvwebbrowser.foss` | No proprietary components |

### Build Types
- **debug**: Development builds with debugging enabled
- **release**: Production builds, optimized and minified

## 📊 Workflow Status

Once activated, you can monitor workflow status:

```bash
# List recent workflow runs
gh run list

# View specific workflow runs
gh run view <run-id> --log

# Download build artifacts
gh run download <run-id>
```

Add these status badges to your README.md:
```markdown
[![Build APK](https://github.com/midozalouk/tv-bro/actions/workflows/build-apk.yml/badge.svg)](https://github.com/midozalouk/tv-bro/actions/workflows/build-apk.yml)
[![CI](https://github.com/midozalouk/tv-bro/actions/workflows/ci.yml/badge.svg)](https://github.com/midozalouk/tv-bro/actions/workflows/ci.yml)
[![PR Check](https://github.com/midozalouk/tv-bro/actions/workflows/pr-check.yml/badge.svg)](https://github.com/midozalouk/tv-bro/actions/workflows/pr-check.yml)
[![Release](https://github.com/midozalouk/tv-bro/actions/workflows/release.yml/badge.svg)](https://github.com/midozalouk/tv-bro/actions/workflows/release.yml)
```

## 🔧 Configuration Options

### Environment Variables
All workflows automatically configure:
- **Java 17** (Temurin distribution)
- **Android SDK** (API 34, Build Tools 34.0.0)
- **Gradle caching** for faster builds
- **Android build cache** for incremental builds

### Customization
You can customize the workflows by editing:
- **API levels**: Modify the matrix in `ci.yml`
- **Build flavors**: Add/remove flavors in build matrices
- **Retention periods**: Adjust artifact retention days
- **Schedule**: Change the cron schedule in `ci.yml`

## 🚨 Troubleshooting

### Common Issues

**1. Workflow doesn't trigger**
- Check if the workflow files are in `.github/workflows/`
- Verify file permissions are correct
- Check branch name matches trigger configuration

**2. Build fails with "SDK not found"**
- Workflows automatically set up Android SDK
- Issue usually resolves automatically

**3. APK signing fails**
- Verify all keystore secrets are configured
- Ensure keystore is Base64 encoded correctly

**4. Permission denied errors**
- Workflow files need to be committed by a user with repository write access
- GitHub Apps require special `workflows` permission

### Debug Commands
```bash
# Check workflow syntax locally
act --list  # If you have 'act' installed

# Validate YAML syntax
yamllint .github/workflows/*.yml

# Check GitHub CLI authentication
gh auth status
```

## 📈 Performance Features

### Build Optimization
- **Gradle build cache**: Speeds up repeated builds
- **Dependency caching**: Reduces download time
- **Matrix parallelization**: Runs multiple builds simultaneously
- **Incremental builds**: Only rebuilds changed components

### Monitoring
- **Build duration tracking**
- **APK size monitoring** with trend analysis
- **Test result reporting**
- **Security vulnerability alerts**

## 🔒 Security Features

### Code Analysis
- **Qodana static analysis** (if token provided)
- **Dependency vulnerability scanning**
- **License compliance checking**
- **Basic secret detection**

### Build Security
- **Keystore management** via GitHub Secrets
- **Dependency verification**
- **Isolated build environments**
- **Artifact integrity verification**

## 📱 Getting Your APKs

### After Workflow Completion

1. **Via GitHub Web Interface:**
   - Go to Actions tab
   - Click on completed workflow run
   - Download artifacts from "Artifacts" section

2. **Via GitHub CLI:**
   ```bash
   gh run download <run-id>
   ```

3. **From Releases (for tagged versions):**
   - Go to Releases tab
   - Download APK files from latest release

### APK Naming Convention
```
tv-bro-{flavor}-{version}-{architecture}.apk

Examples:
- tv-bro-generic-2.0.1-arm64-v8a.apk
- tv-bro-foss-2.0.1-universal.apk
```

## 🎯 Next Steps

1. **Activate the workflows** using the setup commands above
2. **Configure secrets** if you want signed releases
3. **Test the workflows** by creating a pull request
4. **Monitor build status** and adjust as needed
5. **Create your first release** using version tags

## 📞 Support

If you encounter issues:
1. Check the workflow logs in the GitHub Actions tab
2. Review this troubleshooting guide
3. Create an issue with relevant logs attached
4. Tag with `ci/cd` label for CI/CD related issues

---

**Note**: These workflows provide production-ready CI/CD automation for the TV Bro Android browser project. They include comprehensive testing, security scanning, and automated release management.