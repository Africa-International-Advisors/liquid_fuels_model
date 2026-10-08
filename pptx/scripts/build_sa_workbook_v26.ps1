param([string]$Attempt = 'attempt1')
$ErrorActionPreference = 'Stop'
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$story = Get-Content -Raw -Encoding utf8 (Join-Path $root 'pptx/story/sa_market_story_v26_2026_10_08.json') | ConvertFrom-Json
$qa = Join-Path $root "pptx/qa/Vopak_SA_Market_Story_2026_10_08_v26/$Attempt"
if (Test-Path -LiteralPath $qa) { throw 'Use a new attempt name to preserve build outputs.' }
[void](New-Item -ItemType Directory -Path $qa -Force)

function Text($slide,$name,$copy,$x,$y,$w,$h,$size=12,$bold=$false,$theme=1) {
    $s=$slide.Shapes.AddTextbox(1,[single]$x,[single]$y,[single]$w,[single]$h);$s.Name=$name
    $s.TextFrame.MarginLeft=0;$s.TextFrame.MarginRight=0;$s.TextFrame.MarginTop=0;$s.TextFrame.MarginBottom=0
    $t=$s.TextFrame.TextRange;$t.Text=$copy;$t.Font.Name='Lato';$t.Font.Size=[single]$size
    $t.Font.Bold=$(if($bold){-1}else{0});$t.Font.Color.ObjectThemeColor=$theme;$t.ParagraphFormat.SpaceAfter=2
    $s.TextFrame2.AutoSize=0;$s.Left=[single]$x;$s.Top=[single]$y;$s.Width=[single]$w;$s.Height=[single]$h
    return $s
}
function Fill-Table($shape,$spec,$new=$false) {
    $table=$shape.Table;$nr=$spec.rows.Count+1;$nc=$spec.headers.Count
    while($table.Rows.Count -lt $nr){[void]$table.Rows.Add()}
    while($table.Rows.Count -gt $nr){$table.Rows.Item($table.Rows.Count).Delete()}
    if($table.Columns.Count -ne $nc){throw 'Column structure changed unexpectedly.'}
    if($spec.column_widths){for($c=1;$c -le $nc;$c++){$table.Columns.Item($c).Width=[single]$spec.column_widths[$c-1]}}
    $hh=$(if($spec.header_height){$spec.header_height}else{28})
    $bh=$(if($spec.body_height){$spec.body_height}else{$shape.Height-$hh})
    $fs=$(if($spec.font_size){$spec.font_size}else{13})
    for($r=1;$r -le $nr;$r++){
        $table.Rows.Item($r).Height=[single]$(if($r -eq 1){$hh}else{$bh/($nr-1)})
        for($c=1;$c -le $nc;$c++){
            $cell=$table.Cell($r,$c);$s=$cell.Shape
            $s.TextFrame.TextRange.Text=$(if($r -eq 1){$spec.headers[$c-1]}else{$spec.rows[$r-2][$c-1]})
            $s.TextFrame.TextRange.Font.Name='Lato';$s.TextFrame.TextRange.Font.Size=[single]$fs
            $s.TextFrame.TextRange.ParagraphFormat.SpaceAfter=0
            if($new){
                $s.Fill.Visible=0
                for($b=1;$b -le 6;$b++){$cell.Borders.Item($b).Visible=0}
                $cell.Borders.Item(3).Visible=-1;$cell.Borders.Item(3).ForeColor.ObjectThemeColor=1
                $cell.Borders.Item(3).ForeColor.TintAndShade=[single]$(if($r -eq 1){0.65}else{0.9});$cell.Borders.Item(3).Weight=0.4
                $s.TextFrame.MarginLeft=3;$s.TextFrame.MarginRight=9;$s.TextFrame.MarginTop=4;$s.TextFrame.MarginBottom=3
                $s.TextFrame.VerticalAnchor=1;$s.TextFrame.TextRange.Font.Bold=$(if($r -eq 1 -or $c -eq 1){-1}else{0})
                $s.TextFrame.TextRange.Font.Color.ObjectThemeColor=$(if($r -gt 1 -and $c -eq 1){5}else{1})
            }
        }
    }
}
function New-Table($slide,$name,$spec,$x=36,$y=130,$w=838.8) {
    $height=$spec.header_height+$spec.body_height
    $shape=$slide.Shapes.AddTable($spec.rows.Count+1,$spec.headers.Count,[single]$x,[single]$y,[single]$w,[single]$height)
    $shape.Name=$name;Fill-Table $shape $spec $true;return $shape
}
function Blank-Slide($reference) {
    $s=$reference.Duplicate().Item(1)
    $keep=@('Title 1','Slide Number Placeholder','Unified source footer','Strictly Confidential footer','SCR 1','SCR 2','SCR 3','SCR 4')
    for($i=$s.Shapes.Count;$i -ge 1;$i--){if($s.Shapes.Item($i).Name -notin $keep){$s.Shapes.Item($i).Delete()}}
    return $s
}
function Source($slide,$spec) {
    $s=$slide.Shapes.Item('Unified source footer');$s.TextFrame.TextRange.Text=$spec.note
    $s.TextFrame.TextRange.Font.Size=6.5;$s.TextFrame2.AutoSize=0;$s.Top=486;$s.Height=19
    $slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$spec.note+"`r`r"+$spec.analysis_detail
}
function Navigation($slide,$active,$appendix=$false) {
    $labels=@('Appendix','Supporting evidence','Calibration','Reference detail')
    for($i=1;$i -le 4;$i++){
        $s=$slide.Shapes.Item("SCR $i")
        if($appendix){$s.TextFrame.TextRange.Text=$labels[$i-1]}
        $on=(!$appendix -and $i -eq $active)
        $s.Fill.ForeColor.ObjectThemeColor=$(if($on){5}else{2})
        $s.Fill.ForeColor.TintAndShade=[single]$(if($on){0}else{-0.035})
        $s.TextFrame.TextRange.Font.Color.ObjectThemeColor=$(if($on){2}else{5})
    }
}
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $root 'pptx/output/delivered/supporting/SA_Market_Story_2026-10-08_v25.pptx'),0,-1,0)
try {
    $original=@{};for($i=1;$i -le $deck.Slides.Count;$i++){$original[$i]=$deck.Slides.Item($i)}
    $added=@{}
    foreach($spec in $story.slides){
        if($spec.source_page){
            $s=$original[[int]$spec.source_page]
            if($spec.revision_action -eq 'updated'){
                if($spec.rows){Fill-Table $s.Shapes.Item('Table 46') $spec}
                if($spec.takeaway){
                    $caption=$s.Shapes.Item('Interpretation');$caption.TextFrame.TextRange.Text=$spec.takeaway
                    $caption.TextFrame.TextRange.Font.Size=10.5;$caption.TextFrame2.AutoSize=0;$caption.Top=441;$caption.Height=38
                }
                Source $s $spec
            } elseif($spec.revision_action -eq 'references') {
                Source $s $spec
            }
        } elseif($spec.kind -eq 'import') {
            [void]$deck.Slides.InsertFromFile((Join-Path $root 'pptx/output/delivered/supporting/Vopak_Market_Sizing_Issue_Tree_2026_10_08_v2.pptx'),$deck.Slides.Count,1,1)
            $s=$deck.Slides.Item($deck.Slides.Count)
            $b=$s.Shapes.Item('National market');$b.TextFrame.TextRange.Text="National sales baseline`r2023: 21.94bn litres`r2024: 20.76bn, unverified`r2025 sales unavailable"
            $b.TextFrame.TextRange.Font.Size=11.5;$b.TextFrame.TextRange.Paragraphs(1,1).Font.Bold=-1
            Source $s $spec;$added[$spec.new_key]=$s
        } else {
            $s=Blank-Slide $original[14];$s.MoveTo($deck.Slides.Count)
            $s.Shapes.Title.TextFrame.TextRange.Text=$spec.title;$s.Shapes.Title.TextFrame.TextRange.Font.Size=22
            Navigation $s 2 ($spec.new_key -ne 'sectors')
            if($spec.kind -eq 'table'){
                [void](New-Table $s 'Native evidence table' $spec)
                if($spec.takeaway){[void](Text $s 'Interpretation' $spec.takeaway 39 448 832 31 11)}
            } else {
                [void](Text $s 'Fleet heading' 'OPERATING DIESEL FLEET: 3,089 MW' 36 126 434 18 12 $true 5)
                $fleet=@{headers=$spec.fleet_headers;rows=$spec.fleet_rows;column_widths=@(190,95,145);font_size=12;header_height=25;body_height=112}
                [void](New-Table $s 'Operating fleet table' $fleet 36 148 430)
                [void](Text $s 'Timing heading' 'TIMING AND DEPENDENCIES' 497 126 378 18 12 $true 5)
                [void](Text $s 'Timing conditions' $spec.timeline 497 154 378 105 13)
                [void](Text $s 'Scenario heading' 'PROPOSED WORKBOOK CASES — NIGEL / HENRY REVIEW' 36 307 839 18 12 $true 5)
                $cases=@{headers=$spec.case_headers;rows=$spec.case_rows;column_widths=@(155,110,110,463.8);font_size=12;header_height=25;body_height=110}
                [void](New-Table $s 'Proposed cases table' $cases 36 331)
                [void](Text $s 'Case qualification' 'Gas supply, diesel intensity, backup use and coal-site repowering remain assumptions. No engine or approved scenario change is implied.' 39 472 830 12 9)
            }
            Source $s $spec;$added[$spec.new_key]=$s
        }
    }
    $original[1].MoveTo(1)
    for($i=0;$i -lt $story.slides.Count;$i++){
        $spec=$story.slides[$i];$s=$(if($spec.source_page){$original[[int]$spec.source_page]}else{$added[$spec.new_key]})
        $s.MoveTo($i+2)
        if($spec.divider){$s.Shapes.Item('Appendix page number').TextFrame.TextRange.Text=[string]($i+2)}else{$s.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text=[string]($i+2)}
    }
    if($deck.Slides.Count -ne 43){throw 'Expected 43 pages.'}
    $stem='SA_Market_Story_2026-10-08_v26'
    $deck.SaveAs((Join-Path $qa "$stem.pptx"),24,-1)
    $deck.SaveAs((Join-Path $qa "$stem.pdf"),32)
    $deck.Export($qa,'PNG',1217,720)
    $fits=@()
    for($si=1;$si -le $deck.Slides.Count;$si++){
        $s=$deck.Slides.Item($si)
        for($sh=1;$sh -le $s.Shapes.Count;$sh++){
            $shape=$s.Shapes.Item($sh)
            if($shape.HasTable -eq -1){
                for($r=1;$r -le $shape.Table.Rows.Count;$r++){for($c=1;$c -le $shape.Table.Columns.Count;$c++){
                    $cell=$shape.Table.Cell($r,$c).Shape;$tf=$cell.TextFrame
                    if($tf.TextRange.BoundHeight -gt ($cell.Height-$tf.MarginTop-$tf.MarginBottom+2)){
                        $fits+=@{page=$s.SlideIndex;shape=$shape.Name;row=$r;column=$c;bound=$tf.TextRange.BoundHeight;available=$cell.Height-$tf.MarginTop-$tf.MarginBottom;text=$tf.TextRange.Text}
                    }
                }}
            }
        }
    }
    ConvertTo-Json -Depth 6 -InputObject @($fits) | Set-Content -Encoding utf8 (Join-Path $qa 'table_fit.json')
    Write-Output "Built $($deck.Slides.Count) pages in $qa; table fit findings: $($fits.Count)"
} finally {$deck.Close()}
