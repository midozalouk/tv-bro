# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the TV Bro Android browser project.

## 🚀 Available Workflows

### 1. `build-apk.yml` - Main Build Workflow
**Triggers:** Push to main branches, Pull Requests, Manual dispatch

**Features:**
- ✅ Builds APKs for all flavors (generic, google, foss)
- ✅ Supports both debug and release builds
- ✅ Matrix strategy for comprehensive testing
- ✅ Artifact upload for easy download
- ✅ Manual workflow dispatch with custom parameters
- ✅ Automatic release creation on tags
- ✅ Security analysis with Qodana

**Build Matrix:**
- **Flavors**: generic, google, foss
- **Build Types**: debug, release
- **Java Version**: 17 (Temurin)
- **Android API**: 34

### 2. `ci.yml` - Continuous Integration
**Triggers:** Push, Pull Requests, Daily schedule (2 AM UTC)

**Features:**
- ✅ Multi-API level testing (24, 28, 33, 34)
- ✅ Code compilation validation
- ✅ Unit test execution
- ✅ Lint analysis
- ✅ Security vulnerability scanning
- ✅ Documentation validation
- ✅ APK size analysis
- ✅ Performance monitoring

### 3. `pr-check.yml` - Pull Request Quality Check
**Triggers:** Pull Request events (opened, synchronized, reopened)

**Features:**
- ✅ Fast build verification
- ✅ Unit test execution
- ✅ Code quality analysis
- ✅ APK size comparison with base branch
- ✅ Automated PR comments with build status
- ✅ Performance impact analysis

### 4. `release.yml` - Release Build & Deploy
**Triggers:** Version tags (`v*.*.*`), Release events, Manual dispatch

**Features:**
- ✅ Signed release APK generation
- ✅ Multi-architecture builds
- ✅ Automatic GitHub release creation
- ✅ Release notes generation
- ✅ Version file updates
- ✅ APK renaming with version and architecture

## 🔧 Configuration

### Required Secrets
For signed releases, add these secrets to your GitHub repository:

```
RELEASE_KEYSTORE_BASE64    # Base64 encoded keystore file
KEYSTORE_PASSWORD          # Keystore password  
KEY_ALIAS                  # Key alias name
KEY_PASSWORD              # Key password
QODANA_TOKEN              # Qodana analysis token (optional)
```

### Environment Setup
The workflows automatically configure:
- **Java 17** (Temurin distribution)
- **Android SDK** (API 34, Build Tools 34.0.0)
- **Gradle caching** for faster builds
- **Android build cache** for incremental builds

## 📱 Build Variants

### Generic Variant
- **Target**: General Android devices
- **Features**: All features enabled, Firebase included
- **Auto-update**: Enabled
- **Package**: `com.phlox.tvwebbrowser`

### Google Variant
- **Target**: Google Play Store
- **Features**: Firebase enabled
- **Auto-update**: Disabled (Play Store policy)
- **Package**: `com.phlox.tvwebbrowser`

### FOSS Variant
- **Target**: F-Droid and FOSS stores
- **Features**: No proprietary components
- **Auto-update**: Disabled
- **Package**: `com.phlox.tvwebbrowser.foss`

## 🚀 Usage Examples

### Manual Build Trigger
```bash
gh workflow run build-apk.yml \
  -f build_type=release \
  -f flavor=generic
```

### Creating a Release
1. **Tag a version:**
   ```bash
   git tag v2.0.2
   git push origin v2.0.2
   ```

2. **Or use GitHub CLI:**
   ```bash
   gh release create v2.0.2 --generate-notes
   ```

### Download Build Artifacts
After workflow completion, artifacts are available:
- **Debug builds**: 30 days retention
- **Release builds**: 90 days retention
- **PR builds**: 14 days retention

## 📊 Workflow Status Badges

Add these badges to your README.md:

```markdown
[![Build APK](https://github.com/midozalouk/tv-bro/actions/workflows/build-apk.yml/badge.svg)](https://github.com/midozalouk/tv-bro/actions/workflows/build-apk.yml)
[![CI](https://github.com/midozalouk/tv-bro/actions/workflows/ci.yml/badge.svg)](https://github.com/midozalouk/tv-bro/actions/workflows/ci.yml)
[![PR Check](https://github.com/midozalouk/tv-bro/actions/workflows/pr-check.yml/badge.svg)](https://github.com/midozalouk/tv-bro/actions/workflows/pr-check.yml)
[![Release](https://github.com/midozalouk/tv-bro/actions/workflows/release.yml/badge.svg)](https://github.com/midozalouk/tv-bro/actions/workflows/release.yml)
```

## 🔍 Troubleshooting

### Common Issues

**1. Build Fails with "SDK not found"**
- The workflow automatically sets up Android SDK
- Check if `ANDROID_HOME` is properly configured

**2. Gradle Build Timeout**
- Workflows have appropriate timeouts configured
- Large builds may need timeout adjustments

**3. APK Signing Fails**
- Verify keystore secrets are properly configured
- Ensure keystore is Base64 encoded correctly

**4. Artifact Upload Fails**
- Check artifact names don't contain invalid characters
- Verify file paths exist after build

### Debug Commands
```bash
# Check workflow status
gh run list --workflow=build-apk.yml

# View workflow logs
gh run view <run-id> --log

# Download artifacts
gh run download <run-id>
```

## 🛡️ Security Considerations

### Code Scanning
- **Qodana analysis** for code quality
- **Dependency vulnerability scanning**
- **License compliance checking**
- **Secret detection** (basic)

### Build Security
- **Keystore handling** via secure secrets
- **Dependency verification** with checksums
- **Isolated build environments**
- **Artifact integrity** verification

## 📈 Performance Monitoring

### Build Metrics
- **Build duration** tracking
- **APK size** monitoring
- **Test coverage** reporting
- **Dependency updates** notifications

### Optimization Features
- **Gradle build cache** for faster builds
- **Dependency caching** across runs
- **Parallel builds** with matrix strategy
- **Incremental builds** support

## 🔄 Maintenance

### Regular Updates
- **Android SDK/tools** updates
- **Java version** upgrades  
- **GitHub Actions** version updates
- **Dependency security** patches

### Monitoring
- **Workflow success rates**
- **Build duration trends**
- **Artifact storage usage**
- **Security scan results**

## 📞 Support

For workflow issues:
1. Check workflow logs in GitHub Actions tab
2. Review common troubleshooting steps above
3. Create an issue with workflow logs attached
4. Tag with `ci/cd` label for faster resolution

---

**Last Updated**: $(date +%Y-%m-%d)
**Maintained by**: TV Bro Development Team