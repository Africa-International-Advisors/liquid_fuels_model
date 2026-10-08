$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$base=Join-Path $root 'pptx/output/delivered/supporting'
function Safe($p){$p=[IO.Path]::GetFullPath($p);if(-not $p.StartsWith($base+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Path outside supporting'};return $p}
$moves=@()
function MoveFile($src,$dst){
    $src=Safe $src;$dst=Safe $dst
    if(Test-Path -LiteralPath $dst){throw "Destination exists: $dst"}
    New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
    $hash=(Get-FileHash -LiteralPath $src).Hash
    Move-Item -LiteralPath $src -Destination $dst
    if((Get-FileHash -LiteralPath $dst).Hash -ne $hash){throw 'Hash mismatch'}
    $script:moves+=@{old=$src;new=$dst;sha256=$hash}
}
foreach($p in @(Get-ChildItem (Join-Path $base '03_Market_story') -File)){
    if($p.Name -like 'V18_*'){$dst=Join-Path $base ('SA_Market_Story_v18'+$p.Extension)}else{$dst=Join-Path $base ('archive/story_versions/'+$p.Name)}
    MoveFile $p.FullName $dst
}
foreach($pair in @(@('01_Background_and_handover','archive/background'),@('02_Review_scope','Review_scope'),@('04_Illustrations','archive/illustrations'))){
    foreach($p in @(Get-ChildItem (Join-Path $base $pair[0]) -File)){MoveFile $p.FullName (Join-Path $base ($pair[1]+'/'+$p.Name))}
}
MoveFile (Join-Path $base 'filename_history.json') (Join-Path $base 'archive/records/filename_history.json')
MoveFile (Join-Path $base 'current_story.json') (Join-Path $base 'archive/records/current_story.json')
MoveFile (Join-Path $base 'archive/2026-10-08_pre_v18/cleanup_manifest.json') (Join-Path $base 'archive/records/cleanup_manifest.json')
foreach($name in @('prior_index.md','README.md')){
    $p=Safe (Join-Path $base ('archive/2026-10-08_pre_v18/'+$name))
    Remove-Item -LiteralPath $p
}
foreach($name in @('01_Background_and_handover','02_Review_scope','03_Market_story','04_Illustrations','archive/2026-10-08_pre_v18')){
    $p=Safe (Join-Path $base $name)
    if(@(Get-ChildItem -LiteralPath $p -Force).Count -ne 0){throw 'Expected empty folder'}
    Remove-Item -LiteralPath $p
}
$moves | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $base 'archive/records/simplification_manifest.json') -Encoding UTF8
Write-Output 'Current pair and review scope retained; older material archived; redundant indexes removed.'
