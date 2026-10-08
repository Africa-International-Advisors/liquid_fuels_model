$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$stem='Vopak_SA_Market_Story_2026_10_07_v10'
$target=Join-Path $root "pptx/output/delivered/supporting/$stem.pptx"
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open($target,0,0,0)
try {
    $deck.Slides.Item(1).Shapes.Item('TextBox 7').TextFrame.TextRange.Text=('Durban'+[char]0x2013+'Lesedi corridor into Gauteng')
    $deck.Save()
    $deck.SaveAs((Join-Path $root "pptx/output/delivered/supporting/$stem.pdf"),32)
    $deck.Export((Join-Path $root "pptx/qa/$stem"),'PNG',1217,720)
} finally { $deck.Close() }
