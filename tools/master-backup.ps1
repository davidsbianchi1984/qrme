<#
  master-backup.ps1 - one complete copy of QRME, JIM-mini and PDI.

      .\master-backup.ps1 -Dest D:\apps
      .\master-backup.ps1 -Dest D:\apps -Pack

  Makes one folder per app holding the whole repository (every branch,
  every tag, all history) and every file attached to every release.

      315 GiB, 5,938 files, across 804 releases. Give it hours.

  Safe to stop and rerun: a file already on disk at the right size is
  skipped, so a rerun resumes rather than starting over. Nothing is
  ever deleted.

  Needs nothing installed. curl.exe and tar.exe ship with Windows.
  git is optional - without it the release files still come down, and
  the script says which part it skipped.

  $env:GITHUB_TOKEN is optional for these public repositories, but
  without one GitHub allows only 60 API calls an hour and this uses
  about 30.
#>
param(
    [Parameter(Mandatory = $true)][string]$Dest,
    [switch]$Pack
)

$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'   # or every file crawls
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Owner = 'davidsbianchi1984'
$Repos = @('qrme', 'jim-mini', 'pdi')
$Curl  = "$env:SystemRoot\System32\curl.exe"

if (-not (Test-Path $Curl)) { throw "curl.exe not found at $Curl" }
$HasGit = [bool](Get-Command git -ErrorAction SilentlyContinue)

function Api($Path) {
    $h = @{ Accept = 'application/vnd.github+json' }
    if ($env:GITHUB_TOKEN) { $h['Authorization'] = "Bearer $env:GITHUB_TOKEN" }
    Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Path" `
                      -Headers $h -UseBasicParsing
}

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$full = (Resolve-Path $Dest).Path
$drive = Get-PSDrive -Name $full.Substring(0, 1) -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Destination: $full"
if ($drive) {
    $freeGB = [math]::Round($drive.Free / 1GB, 1)
    Write-Host "Free space:  $freeGB GB   (this needs about 320 GB, or 640 GB with -Pack)"
    if ($drive.Free -lt 330GB) {
        Write-Host "That looks too small. Ctrl-C now if this is the wrong disk." `
                   -ForegroundColor Yellow
    }
}
if (-not $HasGit) {
    Write-Host "git not found - release files will download, repository mirrors will be skipped." `
               -ForegroundColor Yellow
}
Write-Host ""
Start-Sleep -Seconds 5

$failed = New-Object System.Collections.Generic.List[string]

foreach ($repo in $Repos) {
    $root = Join-Path $full $repo
    New-Item -ItemType Directory -Force -Path (Join-Path $root 'releases') | Out-Null
    Write-Host "=== $repo ===" -ForegroundColor Cyan

    # --- the repository itself: every branch, every tag, all history ------
    if ($HasGit) {
        $mirror = Join-Path $root "$repo.git"
        if (Test-Path $mirror) {
            Write-Host "  repository: updating"
            git -C $mirror remote update --prune 2>&1 | Out-Null
        } else {
            Write-Host "  repository: cloning"
            git clone --mirror "https://github.com/$Owner/$repo.git" $mirror 2>&1 | Out-Null
        }
        $work = Join-Path $root 'source'
        if (-not (Test-Path $work)) { git clone $mirror $work 2>&1 | Out-Null }
    }

    # --- list every file attached to every release -----------------------
    $assets = New-Object System.Collections.Generic.List[object]
    $page = 1
    while ($true) {
        $rels = Api "$repo/releases?per_page=100&page=$page"
        if (-not $rels -or $rels.Count -eq 0) { break }
        foreach ($r in $rels) {
            foreach ($a in $r.assets) {
                $assets.Add([pscustomobject]@{
                    Tag = $r.tag_name; Name = $a.name
                    Size = [int64]$a.size; Url = $a.browser_download_url })
            }
        }
        if ($rels.Count -lt 100) { break }
        $page++
    }

    $total = $assets.Count
    $bytes = ($assets | Measure-Object -Property Size -Sum).Sum
    Write-Host ("  releases: {0} files listed, {1} GB" -f $total, [math]::Round($bytes / 1GB, 1))

    $i = 0; $got = 0; $had = 0; $bad = 0
    foreach ($a in $assets) {
        $i++
        $dir = Join-Path (Join-Path $root 'releases') $a.Tag
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        $out = Join-Path $dir $a.Name

        if ((Test-Path $out) -and ((Get-Item $out).Length -eq $a.Size)) {
            $had++; continue
        }
        Write-Host ("`r  [{0}/{1}] {2}/{3}" -f $i, $total, $a.Tag, $a.Name).PadRight(78) `
                   -NoNewline
        & $Curl -fsSL --retry 5 --retry-delay 3 -o "$out.part" $a.Url
        if ($LASTEXITCODE -eq 0 -and (Test-Path "$out.part")) {
            Move-Item -Force "$out.part" $out; $got++
        } else {
            Remove-Item -Force -ErrorAction SilentlyContinue "$out.part"
            $bad++; $failed.Add("$repo`t$($a.Tag)`t$($a.Name)")
        }
    }
    Write-Host ("`r  releases: {0} downloaded, {1} already here, {2} failed" -f `
                $got, $had, $bad).PadRight(78)

    # --- a checksum for every file, so a bad card is visible -------------
    Write-Host "  checksums: writing"
    $relDir = Join-Path $root 'releases'
    Get-ChildItem -Path $relDir -Recurse -File |
        ForEach-Object {
            "{0}  {1}" -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash,
                          $_.FullName.Substring($root.Length + 1)
        } | Set-Content -Path (Join-Path $root 'CHECKSUMS.txt') -Encoding ASCII

    $size = (Get-ChildItem $root -Recurse -File | Measure-Object -Property Length -Sum).Sum
    Write-Host ("  {0}: {1} GB" -f $repo, [math]::Round($size / 1GB, 1))
    Write-Host ""
}

if ($Pack) {
    Write-Host "Packing three archives (needs room for a second copy)"
    foreach ($repo in $Repos) {
        Write-Host "  $repo.tar ... " -NoNewline
        Push-Location $full
        & "$env:SystemRoot\System32\tar.exe" -cf "$repo.tar" $repo
        Pop-Location
        $t = Join-Path $full "$repo.tar"
        if (Test-Path $t) {
            Write-Host ("{0} GB" -f [math]::Round((Get-Item $t).Length / 1GB, 1))
        } else { Write-Host "FAILED" -ForegroundColor Red }
    }
}

Write-Host ""
if ($failed.Count -gt 0) {
    $log = Join-Path $full 'FAILED.txt'
    $failed | Set-Content -Path $log -Encoding ASCII
    Write-Host ("{0} file(s) failed - listed in {1}. Rerun to pick them up." -f `
                $failed.Count, $log) -ForegroundColor Yellow
} else {
    Write-Host "Done. Nothing failed." -ForegroundColor Green
}
