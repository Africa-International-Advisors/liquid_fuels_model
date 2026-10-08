$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$base=Join-Path $root 'pptx/output/delivered/supporting'
$target=Join-Path $base 'SA_Market_Story_v23.pptx'
if(Test-Path $target){throw 'Preserve delivered output; choose a new version'}
$story=Get-Content (Join-Path $root 'pptx/story/sa_market_story_v23_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json
function Populate($s,$spec){
    for($j=$s.Shapes.Count;$j -ge 1;$j--){if($s.Shapes.Item($j).Name -like 'Argument icon*'){$s.Shapes.Item($j).Delete()}}
    $shape=$s.Shapes.Item('Table 46');$t=$shape.Table;$nr=$spec.rows.Count+1;$nc=$spec.headers.Count
    while($t.Rows.Count -lt $nr){[void]$t.Rows.Add()}
    while($t.Rows.Count -gt $nr){$t.Rows.Item($t.Rows.Count).Delete()}
    while($t.Columns.Count -lt $nc){[void]$t.Columns.Add()}
    while($t.Columns.Count -gt $nc){$t.Columns.Item($t.Columns.Count).Delete()}
    $widths=$(if($spec.column_widths){$spec.column_widths}else{@(165,329,344.8)})
    for($c=1;$c -le $nc;$c++){$t.Columns.Item($c).Width=[single]$widths[$c-1]}
    $body=$(if($spec.body_height){$spec.body_height}else{322})
    $header=$(if($spec.header_height){$spec.header_height}else{28})
    for($r=1;$r -le $nr;$r++){
        $t.Rows.Item($r).Height=[single]$(if($r -eq 1){$header}else{$body/($nr-1)})
        for($c=1;$c -le $nc;$c++){
            $cell=$t.Cell($r,$c).Shape
            $cell.TextFrame.TextRange.Text=$(if($r -eq 1){$spec.headers[$c-1]}else{$spec.rows[$r-2][$c-1]})
            $cell.TextFrame.MarginLeft=$(if($spec.icons -and $c -eq 1 -and $r -gt 1){35}else{3})
            $cell.TextFrame.MarginRight=9;$cell.TextFrame.MarginTop=7;$cell.TextFrame.MarginBottom=4
            $cell.TextFrame.TextRange.Font.Name='Lato'
            $cell.TextFrame.TextRange.Font.Size=$(if($spec.font_size){$spec.font_size}else{13})
            $cell.TextFrame.TextRange.Font.Bold=$(if($r -eq 1 -or $c -eq 1){-1}else{0})
            $cell.TextFrame.TextRange.Font.Color.ObjectThemeColor=1
            if($spec.matrix -and $r -eq $c -and $r -gt 1){
                $cell.TextFrame.TextRange.Font.Color.ObjectThemeColor=$(if($r -eq 3){2}else{5})
                $cell.TextFrame.TextRange.Font.Bold=-1
            }
        }
    }
    for($j=0;$j -lt $spec.icons.Count;$j++){
        $dir=$(if($spec.icon_dir){$spec.icon_dir}else{'output/sa_feedback_2026_10_07'})
        $pic=$s.Shapes.AddPicture((Join-Path $root ($dir+'/icon_'+$spec.icons[$j]+'.png')),0,-1,40,($shape.Top+$header+$j*$body/($nr-1)+9),25,25)
        $pic.Name='Argument icon '+$spec.icons[$j]
    }
    if($spec.caption){$s.Shapes.Item('Cell outputs').TextFrame.TextRange.Text=$spec.caption}
}
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $base 'SA_Market_Story_v22.pptx'),0,0,0)
try{
    # Retain the original SCR synthesis as an appendix page before editing p4.
    $copy=$deck.Slides.Item(4).Duplicate();$s=$copy.Item(1);$s.MoveTo($deck.Slides.Count)
    for($n=1;$n -le 4;$n++){
        $sh=$s.Shapes.Item("SCR $n");$sh.Fill.ForeColor.ObjectThemeColor=2;$sh.Fill.ForeColor.TintAndShade=-.08
        $sh.TextFrame.TextRange.Font.Color.ObjectThemeColor=5
        $sh.TextFrame.TextRange.Text=@('Appendix','Supporting evidence','Calibration','Reference detail')[$n-1]
    }
    foreach($page in @(3,4,5,14,15,16,18)){Populate $deck.Slides.Item($page) $story.slides[$page-2]}
    # Preserve the p7 paired bars; only edit its implication column.
    for($r=0;$r -lt 3;$r++){$deck.Slides.Item(7).Shapes.Item('Table 46').Table.Cell($r+2,3).Shape.TextFrame.TextRange.Text=$story.slides[5].rows[$r][2]}
    $deck.Slides.Item(9).Shapes.Item('Interpretation').TextFrame.TextRange.Text=$story.slides[7].takeaway
    for($page=2;$page -le $deck.Slides.Count;$page++){
        $s=$deck.Slides.Item($page);$spec=$story.slides[$page-2]
        if($spec.divider){continue}
        $s.Shapes.Title.TextFrame.TextRange.Text=$spec.title
        $s.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text=[string]$page
        $s.Shapes.Item('Unified source footer').TextFrame.TextRange.Text=$spec.note
        $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$spec.note+"`r"+$spec.analysis_detail
    }
    $deck.Slides.Item(1).Shapes.Item('TextBox 9').TextFrame.TextRange.Text=$story.cover_status
    $deck.SaveAs($target,24,-1);$deck.SaveAs((Join-Path $base 'SA_Market_Story_v23.pdf'),32)
    $qa=Join-Path $root 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v23'
    New-Item -ItemType Directory -Force $qa | Out-Null
    $deck.Export($qa,'PNG',1217,720)
}finally{$deck.Close()}
