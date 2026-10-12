$ErrorActionPreference = 'Stop'
$workspaceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$supportRoot = [IO.Path]::GetFullPath((Join-Path $workspaceRoot 'pptx/output/delivered/supporting'))
$archiveRoot = [IO.Path]::GetFullPath((Join-Path $supportRoot 'archive/2026-10-11_cleanup'))
if (-not $supportRoot.StartsWith($workspaceRoot + [IO.Path]::DirectorySeparatorChar) -or -not $archiveRoot.StartsWith($supportRoot + [IO.Path]::DirectorySeparatorChar)) { throw 'Archive paths leave the intended workspace' }
$keepNames = @('SA_Market_Story_2026-10-11_v37.pptx','SA_Market_Story_2026-10-11_v37.pdf','10102026_Vopak_Market_Sizing_v2000.pptx','10102026_Vopak_Market_Sizing_v2000.pdf','README.md')
foreach ($name in $keepNames) { if (-not (Test-Path -LiteralPath (Join-Path $supportRoot $name))) { throw "Missing current file: $name" } }
$moveFiles = @(Get-ChildItem -LiteralPath $supportRoot -File | Where-Object { $_.Name -notin $keepNames })
foreach ($file in $moveFiles) {
    if ($file.Extension -notin @('.pptx','.pdf')) { throw "Unexpected file needs review: $($file.Name)" }
    if (-not $file.FullName.StartsWith($supportRoot + [IO.Path]::DirectorySeparatorChar)) { throw 'Source outside supporting directory' }
    if (Test-Path -LiteralPath (Join-Path $archiveRoot $file.Name)) { throw "Archive collision: $($file.Name)" }
}
if (Test-Path -LiteralPath $archiveRoot) { throw 'Cleanup destination already exists' }
$manifest = @($moveFiles | ForEach-Object { [pscustomobject]@{File=$_.Name;Bytes=$_.Length;SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash;Original=('supporting/'+$_.Name);Archived=('supporting/archive/2026-10-11_cleanup/'+$_.Name)} })
New-Item -ItemType Directory -Path $archiveRoot | Out-Null
$oldReadme = [IO.File]::ReadAllText((Join-Path $supportRoot 'README.md'))
[IO.File]::WriteAllText((Join-Path $archiveRoot 'README_before_cleanup.original.txt'),$oldReadme)
foreach ($file in $moveFiles) { Move-Item -LiteralPath $file.FullName -Destination (Join-Path $archiveRoot $file.Name) }
foreach ($record in $manifest) {
    if ((Get-FileHash -LiteralPath (Join-Path $archiveRoot $record.File) -Algorithm SHA256).Hash -ne $record.SHA256) { throw "Hash mismatch: $($record.File)" }
}
$manifest | Export-Csv -LiteralPath (Join-Path $archiveRoot 'manifest.csv') -NoTypeInformation -Encoding utf8
# Repair local links in the relocated delivery history; preserve original text separately.
$history = [regex]::Replace($oldReadme,'\]\(([^)]+)\)',{
    param($match)
    $link = $match.Groups[1].Value
    if ($link -match '^(https?://|#|app:)' -or [IO.Path]::IsPathRooted($link)) { return $match.Value }
    $target = [IO.Path]::GetFullPath((Join-Path $supportRoot $link))
    $leaf = [IO.Path]::GetFileName($target)
    if ($leaf -in $manifest.File -and [IO.Path]::GetDirectoryName($target) -eq $supportRoot) { $target=Join-Path $archiveRoot $leaf }
    return '](' + [IO.Path]::GetRelativePath($archiveRoot,$target).Replace('\','/') + ')'
})
[IO.File]::WriteAllText((Join-Path $archiveRoot 'delivery_history.md'),$history)
$archiveIndex = "# Archived deliveries: 11 October 2026`n`nSuperseded story versions v27-v36, sizing versions v1100/v1900, and October 6-7 analyst handbacks. All files retain their original names and content.`n`n- [Delivery history](delivery_history.md)`n- [Move and SHA-256 manifest](manifest.csv)`n- [Current deliverables](../../README.md)`n"
[IO.File]::WriteAllText((Join-Path $archiveRoot 'README.md'),$archiveIndex)
# Preserve source-builder dependencies and references outside the delivery directory.
$referenceFiles = @()
foreach ($folder in @('pptx/scripts','workstreams','docs')) {
    $dir=Join-Path $workspaceRoot $folder
    if (Test-Path -LiteralPath $dir) { $referenceFiles += Get-ChildItem -LiteralPath $dir -File -Recurse | Where-Object { $_.Extension -in @('.md','.py','.mjs','.ps1','.yaml','.yml') -and $_.FullName -ne $PSCommandPath } }
}
foreach ($path in @('README.md','output/delivered/README.md','pptx/output/delivered/README.md')) {
    $full=Join-Path $workspaceRoot $path
    if (Test-Path -LiteralPath $full) { $referenceFiles += Get-Item -LiteralPath $full }
}
$updated = @()
foreach ($file in $referenceFiles) {
    $original=[IO.File]::ReadAllText($file.FullName);$revised=$original
    foreach ($name in $manifest.File) {
        $revised=$revised.Replace('supporting/'+$name,'supporting/archive/2026-10-11_cleanup/'+$name)
        $revised=$revised.Replace('supporting\'+$name,'supporting\archive\2026-10-11_cleanup\'+$name)
    }
    if ($revised -ne $original) { [IO.File]::WriteAllText($file.FullName,$revised);$updated += [IO.Path]::GetRelativePath($workspaceRoot,$file.FullName) }
}
[IO.File]::WriteAllLines((Join-Path $archiveRoot 'updated_references.txt'),$updated)
$currentIndex = @'
# Current supporting deliverables

Updated 11 October 2026. Previous versions are archived; no deliverables were deleted.

| Deliverable | PowerPoint | PDF |
|---|---|---|
| South Africa market story v37 | [Open](SA_Market_Story_2026-10-11_v37.pptx) | [Open](SA_Market_Story_2026-10-11_v37.pdf) |
| Durban and Lesedi market sizing v2000 | [Open](10102026_Vopak_Market_Sizing_v2000.pptx) | [Open](10102026_Vopak_Market_Sizing_v2000.pdf) |

The story has 15 core pages, an appendix divider on page 16 and eight supporting pages. The 5.8bn-litre domestic production assumption remains explicit. Commercial capture and product reconciliation remain subject to review.

## Supporting workbooks

- [South Africa analytical workbook v02](../../../../output/delivered/sa_analytics_2026_10_11_v02/SA_Fuel_Analytics_2025_Baseline_2026-10-11_v02.xlsx)
- [Market-sizing workbook](../../../../output/delivered/Vopak_Market_Sizing_2026-10-10_v01.xlsx)
- [Master-data review and gaps](../../../../output/delivered/Master_data_book_review_2026-10-10_v01.xlsx)

## Reference material

- [Review scope](Review_scope/)
- [Archived revisions and delivery history](archive/2026-10-11_cleanup/README.md)
- [Earlier archive](archive/README.md)

Rebuild the current story with the v37 preparation, builder, trim, style, navigation, chart-workbook, cover-note cleanup and finalizer scripts in `pptx/scripts/`. Archived v30/v31 template references remain available to those builders.
'@
[IO.File]::WriteAllText((Join-Path $supportRoot 'README.md'),$currentIndex)
$archiveReadme=Join-Path $supportRoot 'archive/README.md'
$archiveText=[IO.File]::ReadAllText($archiveReadme)
$archiveText=$archiveText.Replace('Earlier material is retained here only for reference:',"Earlier material is retained here only for reference:`n`n- [11 October cleanup](2026-10-11_cleanup/README.md) — superseded delivered versions and handbacks, with move manifest and delivery history.")
[IO.File]::WriteAllText($archiveReadme,$archiveText)
Write-Output "Archived $($manifest.Count) files; updated $($updated.Count) reference files; SHA-256 hashes match."
Get-ChildItem -LiteralPath $supportRoot | Select-Object Name,PSIsContainer
