$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$out=Join-Path $root 'pptx/output/delivered/supporting'
$stem='Vopak_SA_Market_Story_2026_10_07_v9'
$target=Join-Path $out "$stem.pptx"
if (Test-Path $target) {throw 'Use a new version.'}
Copy-Item -LiteralPath (Join-Path $out 'Vopak_SA_Market_Story_2026_10_07_v8.pptx') -Destination $target
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=[IO.Compression.ZipFile]::Open($target,[IO.Compression.ZipArchiveMode]::Update)
try {
    $entry=$zip.GetEntry('ppt/slides/slide26.xml')
    $reader=New-Object IO.StreamReader($entry.Open());[xml]$xml=$reader.ReadToEnd();$reader.Close()
    $ns=New-Object Xml.XmlNamespaceManager($xml.NameTable)
    $ns.AddNamespace('a','http://schemas.openxmlformats.org/drawingml/2006/main')
    $nodes=@($xml.SelectNodes('(//a:tbl/a:tr)[1]/a:tc[1]//a:t',$ns))
    $nodes[0].InnerText='Time series'
    for ($i=1;$i -lt $nodes.Count;$i++) {$nodes[$i].InnerText=''}
    $entry.Delete();$entry=$zip.CreateEntry('ppt/slides/slide26.xml')
    $writer=New-Object IO.StreamWriter($entry.Open());$writer.Write($xml.OuterXml);$writer.Close()
} finally {$zip.Dispose()}
$qa=Join-Path $root "pptx/qa/$stem"
New-Item -ItemType Directory -Force $qa | Out-Null
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open($target,-1,0,0)
try {
    $deck.SaveAs((Join-Path $out "$stem.pdf"),32)
    $deck.Export($qa,'PNG',1217,720)
} finally {try {$deck.Close()} catch {Write-Warning 'Presentation already closed.'}}
Write-Output 'Final v9 exported; power appendix header shortened to preserve the source footer.'
