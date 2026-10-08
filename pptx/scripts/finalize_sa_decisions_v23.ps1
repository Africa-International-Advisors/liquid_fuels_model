# Pre-delivery wording pass; preserve all layout and analytical values.
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$base=Join-Path $root 'pptx/output/delivered/supporting'
$story=Get-Content (Join-Path $root 'pptx/story/sa_market_story_v23_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $base 'SA_Market_Story_v23.pptx'),0,0,0)
try{
    $deck.Slides.Item(3).Shapes.Item('Table 46').Table.Cell(5,3).Shape.TextFrame.TextRange.Text=$story.slides[1].rows[3][2]
    foreach($page in @(4,5)){
        $s=$deck.Slides.Item($page);$spec=$story.slides[$page-2]
        $s.Shapes.Title.TextFrame.TextRange.Text=$spec.title
        $s.Shapes.Item('Unified source footer').TextFrame.TextRange.Text=$spec.note
        $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$spec.note+"`r"+$spec.analysis_detail
    }
    $deck.Save()
    $deck.SaveAs((Join-Path $base 'SA_Market_Story_v23.pdf'),32)
    $deck.Export((Join-Path $root 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v23'),'PNG',1217,720)
}finally{$deck.Close()}
