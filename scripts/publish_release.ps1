param(
    [string]$Version,
    [string]$TargetCommitish = "main",
    [string]$PortableAsset,
    [string]$InstallerAsset,
    [string]$ReleaseName,
    [string]$ReleaseBodyFile,
    [string]$GitHubToken = $env:GITHUB_PAT_TOKEN,
    [string]$GiteeToken = $(if ($env:GITEE_RELEASE_TOKEN) { $env:GITEE_RELEASE_TOKEN } else { $env:GITEE_MCP_AUTHORIZATION }),
    [switch]$SkipGitHub,
    [switch]$SkipGitee,
    [switch]$SkipManifestSync,
    [switch]$OverwriteAssets,
    [switch]$Prerelease,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$scriptPath = Join-Path $projectRoot "scripts\publish_release.py"

$arguments = @()
if ($Version) { $arguments += @("--version", $Version) }
if ($TargetCommitish) { $arguments += @("--target-commitish", $TargetCommitish) }
if ($PortableAsset) { $arguments += @("--portable-asset", $PortableAsset) }
if ($InstallerAsset) { $arguments += @("--installer-asset", $InstallerAsset) }
if ($ReleaseName) { $arguments += @("--release-name", $ReleaseName) }
if ($ReleaseBodyFile) { $arguments += @("--release-body-file", $ReleaseBodyFile) }
if ($GitHubToken) { $arguments += @("--github-token", $GitHubToken) }
if ($GiteeToken) { $arguments += @("--gitee-token", $GiteeToken) }
if ($SkipGitHub) { $arguments += "--skip-github" }
if ($SkipGitee) { $arguments += "--skip-gitee" }
if ($SkipManifestSync) { $arguments += "--skip-manifest-sync" }
if ($OverwriteAssets) { $arguments += "--overwrite-assets" }
if ($Prerelease) { $arguments += "--prerelease" }
if ($DryRun) { $arguments += "--dry-run" }

Set-Location $projectRoot
python $scriptPath @arguments

if ($LASTEXITCODE -ne 0) {
    throw "Release publish failed."
}
