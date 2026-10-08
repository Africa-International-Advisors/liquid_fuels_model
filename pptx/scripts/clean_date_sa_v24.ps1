$ErrorActionPreference='Stop'
$root=(Get-Location).Path
$base=Join-Path $root 'pptx/output/delivered/supporting'
$archive=Join-Path $base 'archive/story_versions'
$records=Join-Path $base 'archive/records'
$actions=@()
foreach($f in Get-ChildItem -LiteralPath $base -File){
 if($f.Name -match '^SA_Market_Story_v(\d+)(?:_nigel)?\.(pptx|pdf)$'){
  $version=[int]$Matches[1]
  if($version -lt 24){$dest=Join-Path $archive $f.Name}
  elseif($version -eq 24){$dest=Join-Path $base ('SA_Market_Story_2026-10-08_v24'+$f.Extension)}
  else{continue}
  $resolved=[IO.Path]::GetFullPath($dest)
  if(-not $resolved.StartsWith($base+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Destination outside delivery folder'}
  if(Test-Path -LiteralPath $resolved){throw "Destination exists: $resolved"}
  $hash=(Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash
  try {Move-Item -LiteralPath $f.FullName -Destination $resolved} catch {Write-Output "Left open/locked file: $($f.Name)"; continue}
  if((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash -ne $hash){throw 'Hash mismatch'}
  $actions+= [pscustomobject]@{source=$f.FullName;destination=$resolved;sha256=$hash;date='2026-10-08'}
 }
}
$actions | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $records 'cleanup_2026-10-08_v24.json') -Encoding UTF8
Write-Output "Archived or dated $($actions.Count) files; all hashes unchanged."
