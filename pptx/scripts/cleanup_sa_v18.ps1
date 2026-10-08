$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
function Within($path){
    $full=[IO.Path]::GetFullPath($path)
    if(-not $full.StartsWith($root+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw "Outside workspace: $full"}
    return $full
}
$support=Within (Join-Path $root 'pptx/output/delivered/supporting')
if(Test-Path (Join-Path $support 'filename_history.json')){throw 'Supporting has been resequenced; this historical cleanup must not be rerun.'}
$archive=Within (Join-Path $support 'archive/2026-10-08_pre_v18')
New-Item -ItemType Directory -Force $archive | Out-Null
$records=@()
$manifest=Join-Path $archive 'cleanup_manifest.json'
if(Test-Path -LiteralPath $manifest){
    $prior=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
    foreach($item in $prior){$records+=$item}
}
$old=@(Get-ChildItem -LiteralPath $support -File | Where-Object {$_.Name -match '^Vopak_SA_Market_Story_.*_v(\d+)\.(pptx|pdf)$' -and [int]$Matches[1] -lt 18})
foreach($file in $old){
    $source=Within $file.FullName;$dest=Within (Join-Path $archive $file.Name)
    if(Test-Path -LiteralPath $dest){throw "Archive already exists: $dest"}
    $hash=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    Move-Item -LiteralPath $source -Destination $dest
    if((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash -ne $hash){throw 'Archive hash mismatch'}
    $records+=@{name=$file.Name;bytes=$file.Length;sha256=$hash;action='archived';source=$source;destination=$dest}
}
$qaRoot=Within (Join-Path $root 'pptx/qa')
$qaArchive=Within (Join-Path $qaRoot 'archive/2026-10-08_pre_v18')
New-Item -ItemType Directory -Force $qaArchive | Out-Null
foreach($folder in @(Get-ChildItem -LiteralPath $qaRoot -Directory | Where-Object {$_.Name -like 'Vopak_SA_Market_Story_*' -and $_.Name -ne 'Vopak_SA_Market_Story_2026_10_08_v18'})){
    $source=Within $folder.FullName;$dest=Within (Join-Path $qaArchive $folder.Name)
    if(Test-Path -LiteralPath $dest){throw 'QA archive exists'}
    Move-Item -LiteralPath $source -Destination $dest
    $records+=@{name=$folder.Name;action='QA directory archived';source=$source;destination=$dest}
}
$working=Within (Join-Path $root 'pptx/output/working')
$previewArchive=Within (Join-Path $working 'archive/2026-10-08_pre_v18')
New-Item -ItemType Directory -Force $previewArchive | Out-Null
foreach($file in @(Get-ChildItem -LiteralPath $working -File | Where-Object {$_.Name -like 'Vopak_SA_Market_Story_*_preview.*'})){
    $source=Within $file.FullName;$dest=Within (Join-Path $previewArchive $file.Name)
    Move-Item -LiteralPath $source -Destination $dest
    $records+=@{name=$file.Name;action='preview archived';source=$source;destination=$dest}
}
# Download fragments are redundant only after the original complete PBF is verified.
$raw=Within (Join-Path $root 'external/sources/geospatial/2026_10_08/osm')
foreach($meta in @(Get-ChildItem -LiteralPath $raw -Filter '*.json' -File | Where-Object {$_.Name -ne 'manifest.json'})){
    $entry=Get-Content -LiteralPath $meta.FullName -Raw | ConvertFrom-Json
    $complete=Within (Join-Path $root $entry.path)
    if((Get-FileHash -LiteralPath $complete -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256){throw 'Complete PBF hash mismatch; retain download fragments'}
    foreach($name in @(($entry.country+'_chunks'),($entry.country+'.osm.part'))){
        $fragment=Within (Join-Path $raw $name)
        if(Test-Path -LiteralPath $fragment){
            $bytes=(Get-ChildItem -LiteralPath $fragment -File -Recurse | Measure-Object Length -Sum).Sum
            if(Test-Path -LiteralPath $fragment -PathType Leaf){$bytes=(Get-Item -LiteralPath $fragment).Length}
            Remove-Item -LiteralPath $fragment -Recurse -Force
            $records+=@{name=$name;action='redundant download fragment removed';bytes=$bytes;retained_complete_source=$complete;source_sha256=$entry.sha256}
        }
    }
}
$records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $archive 'cleanup_manifest.json') -Encoding UTF8
Write-Output ("Archived {0} delivered files; cleanup manifest written." -f $old.Count)
