$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$qa=Join-Path $root 'pptx/qa/partner_scr_v29'
$src=Join-Path $qa 'final/SA_Market_Story_2026-10-10_v29.pptx'
$pdf=Join-Path $qa 'final/SA_Market_Story_2026-10-10_v29.pdf'
$render=Join-Path $qa 'powerpoint_render'
[void](New-Item -ItemType Directory -Force -Path $render)
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open($src,-1,0,0)
try {
 $deck.SaveAs($pdf,32)
 $deck.Export($render,'PNG',1217,720)
 Write-Output ('Exported PDF and '+$deck.Slides.Count+' previews')
} finally { $deck.Close() }
