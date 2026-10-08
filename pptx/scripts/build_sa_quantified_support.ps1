$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$base=Join-Path $root 'pptx/output/delivered/supporting'
$target=Join-Path $base 'SA_Market_Story_v20.pptx'
if(Test-Path $target){throw 'Preserve existing output'}
$spec=(Get-Content (Join-Path $root 'pptx/story/sa_market_story_v20_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json).slides[5]
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $base 'SA_Market_Story_v19.pptx'),0,0,0)
try{
    $slide=$deck.Slides.Item(7);$table=$slide.Shapes.Item('Table 46').Table
    for($c=1;$c -le 3;$c++){
        $table.Columns.Item($c).Width=[single]$spec.column_widths[$c-1]
        $table.Cell(1,$c).Shape.TextFrame.TextRange.Text=$spec.headers[$c-1]
        for($r=2;$r -le 4;$r++){
            $t=$table.Cell($r,$c).Shape.TextFrame.TextRange
            $t.Text=$spec.rows[$r-2][$c-1];$t.Font.Size=12.5
            $t.Font.Bold=$(if($c -eq 1){-1}else{0})
            if($c -eq 2){$t.Paragraphs(1,1).Font.Bold=-1}
        }
    }
    $slide.Shapes.Item('Unified source footer').TextFrame.TextRange.Text=$spec.note
    $slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$spec.note+"`rDerived evidence: "+$spec.evidence_data
    $deck.SaveAs($target,24,-1);$deck.SaveAs((Join-Path $base 'SA_Market_Story_v20.pdf'),32)
    $qa=Join-Path $root 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v20';New-Item -ItemType Directory -Force $qa | Out-Null
    $deck.Export($qa,'PNG',1217,720)
}finally{$deck.Close()}
