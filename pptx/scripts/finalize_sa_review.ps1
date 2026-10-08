$ErrorActionPreference = 'Stop'
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$out = Join-Path $root 'pptx/output/delivered/supporting'
$stem = 'Vopak_SA_Review_Signed_Off_2026_10_07'
$target = Join-Path $out "${stem}_v2.pptx"
if (Test-Path $target) { throw 'Final version already exists.' }
Copy-Item -LiteralPath (Join-Path $out "${stem}_v1.pptx") -Destination $target
$story = Get-Content (Join-Path $root 'pptx/story/sa_review_signed_off_2026_10_07.json') -Raw | ConvertFrom-Json
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [IO.Compression.ZipFile]::Open($target,[IO.Compression.ZipArchiveMode]::Update)
try {
    foreach ($entry in @($zip.Entries | Where-Object {$_.FullName -match '^ppt/slides/slide\d+\.xml$'})) {
        $name = $entry.FullName
        $reader = New-Object IO.StreamReader($entry.Open())
        [xml]$xml = $reader.ReadToEnd()
        $reader.Close()
        $ns = New-Object Xml.XmlNamespaceManager($xml.NameTable)
        $ns.AddNamespace('a','http://schemas.openxmlformats.org/drawingml/2006/main')
        $ns.AddNamespace('p','http://schemas.openxmlformats.org/presentationml/2006/main')
        # Remove inherited deck navigation and empty hyperlink relationship references.
        foreach ($node in @($xml.SelectNodes('//a:hlinkClick | //a:hlinkMouseOver',$ns))) { [void]$node.ParentNode.RemoveChild($node) }
        $slideNo = [int]([regex]::Match($name,'slide(\d+)').Groups[1].Value)
        if ($slideNo -gt 1) {
            $active = $story.slides[$slideNo - 2].section
            for ($n = 1; $n -le 4; $n++) {
                $shape = $xml.SelectSingleNode("//p:sp[p:nvSpPr/p:cNvPr[@name='Section navigation $n']]",$ns)
                foreach ($pr in @($shape.SelectNodes('.//a:rPr | .//a:defRPr',$ns))) {
                    foreach ($old in @($pr.SelectNodes('a:solidFill | a:noFill',$ns))) { [void]$pr.RemoveChild($old) }
                    $fill = $xml.CreateElement('a','solidFill',$ns.LookupNamespace('a'))
                    $clr = $xml.CreateElement('a','schemeClr',$ns.LookupNamespace('a'))
                    $clr.SetAttribute('val',$(if ($n -eq $active) {'lt1'} else {'accent1'}))
                    [void]$fill.AppendChild($clr)
                    [void]$pr.PrependChild($fill)
                }
            }
        }
        $entry.Delete()
        $newEntry = $zip.CreateEntry($name)
        $writer = New-Object IO.StreamWriter($newEntry.Open())
        $writer.Write($xml.OuterXml)
        $writer.Close()
    }
} finally { $zip.Dispose() }
$qa = Join-Path $root 'pptx/qa/sa_review_2026_10_07/v2'
New-Item -ItemType Directory -Force $qa | Out-Null
$app = New-Object -ComObject PowerPoint.Application
$deck = $app.Presentations.Open($target,-1,0,0)
try {
    $deck.SaveAs((Join-Path $out "${stem}_v2.pdf"),32)
    $deck.Export($qa,'PNG',1217,720)
} finally { $deck.Close() }
Write-Output 'Final v2 PPTX and PDF exported; native navigation colours and hyperlinks repaired.'
