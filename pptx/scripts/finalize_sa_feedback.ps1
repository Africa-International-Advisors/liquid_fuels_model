$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$out=Join-Path $root 'pptx/output/delivered/supporting'
$stem='Vopak_SA_Market_Story_2026_10_07_v8'
$target=Join-Path $out "$stem.pptx"
$source=Join-Path $out 'Vopak_SA_Market_Story_2026_10_07_v7.pptx'
if (Test-Path $target) {
    if ((Get-FileHash $target).Hash -ne (Get-FileHash $source).Hash) { throw 'Preserve existing edited version.' }
} else { Copy-Item -LiteralPath $source -Destination $target }
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=[IO.Compression.ZipFile]::Open($target,[IO.Compression.ZipArchiveMode]::Update)
try {
    $reader=New-Object IO.StreamReader($zip.GetEntry('ppt/slides/slide10.xml').Open())
    [xml]$slide=$reader.ReadToEnd();$reader.Close()
    $ns=New-Object Xml.XmlNamespaceManager($slide.NameTable)
    $ns.AddNamespace('p','http://schemas.openxmlformats.org/presentationml/2006/main')
    $ns.AddNamespace('a','http://schemas.openxmlformats.org/drawingml/2006/main')
    $pic=$slide.SelectSingleNode("//p:pic[p:nvPicPr/p:cNvPr[@name='Evidence chart']]",$ns)
    if (!$pic) {throw 'Expected transport chart not found.'}
    $rid=$pic.SelectSingleNode('.//a:blip',$ns).GetAttribute('embed','http://schemas.openxmlformats.org/officeDocument/2006/relationships')
    $reader=New-Object IO.StreamReader($zip.GetEntry('ppt/slides/_rels/slide10.xml.rels').Open())
    [xml]$rels=$reader.ReadToEnd();$reader.Close()
    $rel=$rels.Relationships.Relationship | Where-Object {$_.Id -eq $rid}
    $media='ppt/media/'+[IO.Path]::GetFileName($rel.Target)
    $entry=$zip.GetEntry($media)
    if (!$entry) {throw 'Chart media relationship missing.'}
    $entry.Delete()
    [void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,(Join-Path $root 'output/sa_feedback_2026_10_07/transport_timeseries.png'),$media)
} finally {$zip.Dispose()}
$qa=Join-Path $root "pptx/qa/$stem"
New-Item -ItemType Directory -Force $qa | Out-Null
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open($target,-1,0,0)
try {
    $deck.SaveAs((Join-Path $out "$stem.pdf"),32)
    $deck.Export($qa,'PNG',1217,720)
} finally {try {$deck.Close()} catch {Write-Warning 'Presentation already closed.'}}
Write-Output 'Final feedback PPTX/PDF exported with corrected transport chart spacing.'
