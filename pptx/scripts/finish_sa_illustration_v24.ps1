$ErrorActionPreference='Stop'
$root=(Get-Location).Path
$base=Join-Path $root 'pptx/output/delivered/supporting'
$story=Get-Content (Join-Path $root 'pptx/story/sa_market_story_v24_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $base 'SA_Market_Story_v24.pptx'),0,0,0)
try {
$s=$deck.Slides.Item(35)
$s.Shapes.Item('Unified source footer').TextFrame.TextRange.Text=$story.slides[33].note
$s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$story.slides[33].note
$s=$deck.Slides.Item(38)
$s.Shapes.Item('Evidence chart').Delete()
$pic=$s.Shapes.AddPicture((Join-Path $root 'output/delivered/vopak_illustration_2026_10_08/sensitivity.png'),0,-1,55,122,800,309.09)
$pic.Name='Evidence chart'
$deck.Save()
$deck.SaveAs((Join-Path $base 'SA_Market_Story_v24.pdf'),32)
$deck.Export((Join-Path $root 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v24'),'PNG',1217,720)
} finally {$deck.Close()}
