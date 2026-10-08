$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$base=Join-Path $root 'pptx/output/delivered/supporting'
$target=Join-Path $base 'SA_Market_Story_v22.pptx'
if(Test-Path $target){throw 'Preserve delivered output; choose a new version'}
$story=Get-Content (Join-Path $root 'pptx/story/sa_market_story_v22_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json
function Populate($s,$spec){
    for($j=$s.Shapes.Count;$j -ge 1;$j--){if($s.Shapes.Item($j).Name -like 'Argument icon*'){$s.Shapes.Item($j).Delete()}}
    $s.Shapes.Title.TextFrame.TextRange.Text=$spec.title
    $s.Shapes.Title.TextFrame.TextRange.Font.Size=23
    $t=$s.Shapes.Item('Table 46').Table;$nr=$spec.rows.Count+1
    while($t.Rows.Count -lt $nr){[void]$t.Rows.Add()}
    while($t.Rows.Count -gt $nr){$t.Rows.Item($t.Rows.Count).Delete()}
    for($c=1;$c -le 3;$c++){$t.Columns.Item($c).Width=[single]$spec.column_widths[$c-1]}
    for($r=1;$r -le $nr;$r++){
        $t.Rows.Item($r).Height=[single]$(if($r -eq 1){28}else{322/($nr-1)})
        for($c=1;$c -le 3;$c++){
            $cell=$t.Cell($r,$c).Shape
            $cell.TextFrame.TextRange.Text=$(if($r -eq 1){$spec.headers[$c-1]}else{$spec.rows[$r-2][$c-1]})
            $cell.TextFrame.MarginLeft=3;$cell.TextFrame.MarginRight=9;$cell.TextFrame.MarginTop=7;$cell.TextFrame.MarginBottom=4
            $cell.TextFrame.TextRange.Font.Name='Lato';$cell.TextFrame.TextRange.Font.Size=12
            $cell.TextFrame.TextRange.Font.Bold=$(if($r -eq 1 -or $c -eq 1){-1}else{0})
            $cell.TextFrame.TextRange.Font.Color.ObjectThemeColor=1
        }
    }
    for($n=1;$n -le 4;$n++){
        $sh=$s.Shapes.Item("SCR $n")
        $active=($spec.section -eq $n)
        $sh.Fill.ForeColor.ObjectThemeColor=$(if($active){5}else{2})
        $sh.Fill.ForeColor.TintAndShade=[single]$(if($active){0}else{-.08})
        $sh.TextFrame.TextRange.Font.Color.ObjectThemeColor=$(if($active){2}else{5})
        $sh.TextFrame.TextRange.Text=$(if($spec.section -eq 0){@('Appendix','Supporting evidence','Calibration','Reference detail')[$n-1]}else{@('Executive summary','Situation','Complication','Resolution')[$n-1]})
    }
}
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $base 'SA_Market_Story_v21.pptx'),0,0,0)
try{
    $copy=$deck.Slides.Item(15).Duplicate();$s=$copy.Item(1);$s.MoveTo(16)
    Populate $s $story.slides[14]
    foreach($page in @(32,33)){
        $copy=$deck.Slides.Item(14).Duplicate();$s=$copy.Item(1);$s.MoveTo($deck.Slides.Count)
        Populate $s $story.slides[$page-2]
    }
    for($page=2;$page -le $deck.Slides.Count;$page++){
        $s=$deck.Slides.Item($page);$spec=$story.slides[$page-2]
        if($spec.divider){$s.Shapes.Item('Appendix page number').TextFrame.TextRange.Text=[string]$page;continue}
        $s.Shapes.Title.TextFrame.TextRange.Text=$spec.title
        $s.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text=[string]$page
        $s.Shapes.Item('Unified source footer').TextFrame.TextRange.Text=$spec.note
        $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$spec.note
    }
    $deck.Slides.Item(1).Shapes.Item('TextBox 9').TextFrame.TextRange.Text=$story.cover_status
    $deck.SaveAs($target,24,-1)
    $deck.SaveAs((Join-Path $base 'SA_Market_Story_v22.pdf'),32)
    $qa=Join-Path $root 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v22'
    New-Item -ItemType Directory -Force $qa | Out-Null
    $deck.Export($qa,'PNG',1217,720)
}finally{$deck.Close()}
