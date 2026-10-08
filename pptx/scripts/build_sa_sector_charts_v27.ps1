$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$story=Get-Content -Raw -Encoding utf8 (Join-Path $root 'pptx/story/sa_market_story_v27_2026_10_08.json') | ConvertFrom-Json
$spec=$story.slides[6]
$qa=Join-Path $root 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v27'
if(Test-Path -LiteralPath $qa){throw 'Preserve prior outputs; choose a new revision.'}
[void](New-Item -ItemType Directory -Path $qa)
function Label($slide,$name,$copy,$x,$y,$w,$h,$size=12,$bold=$false,$theme=1){
    $s=$slide.Shapes.AddTextbox(1,[single]$x,[single]$y,[single]$w,[single]$h);$s.Name=$name
    $s.TextFrame.MarginLeft=0;$s.TextFrame.MarginRight=0;$s.TextFrame.MarginTop=0;$s.TextFrame.MarginBottom=0
    $t=$s.TextFrame.TextRange;$t.Text=$copy;$t.Font.Name='Lato';$t.Font.Size=[single]$size;$t.Font.Bold=$(if($bold){-1}else{0});$t.Font.Color.ObjectThemeColor=$theme
    $s.TextFrame2.AutoSize=0;$s.Left=[single]$x;$s.Top=[single]$y;$s.Width=[single]$w;$s.Height=[single]$h
    return $s
}
function Rule($slide,$name,$x,$y,$x2,$y2){
    $s=$slide.Shapes.AddConnector(1,[single]$x,[single]$y,[single]$x2,[single]$y2);$s.Name=$name
    $s.Line.ForeColor.ObjectThemeColor=1;$s.Line.ForeColor.TintAndShade=0.85;$s.Line.Weight=0.4
}
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $root 'pptx/output/delivered/supporting/SA_Market_Story_2026-10-08_v26.pptx'),0,-1,0)
try{
    $slide=$deck.Slides.Item(8);$slide.Shapes.Item('Native evidence table').Delete();$slide.Shapes.Item('Interpretation').Delete()
    [void](Label $slide 'Sector heading' 'Sector' 36 126 155 18 12 $true)
    [void](Label $slide 'Chart heading' 'Diesel use, billion litres / year' 201 126 349 18 12 $true)
    [void](Label $slide 'Activity heading' 'Activity and interpretation' 589 126 286 18 12 $true)
    Rule $slide 'Sector heading rule' 36 150 874.8 150
    for($i=0;$i -lt 3;$i++){
        $row=$spec.chart_rows[$i];$top=165+$i*99
        [void](Label $slide "Sector label $i" $row[0] 36 ($top+5) 155 56 13 $true 5)
        [void](Label $slide "Sector interpretation $i" $row[4] 589 ($top+6) 286 65 12.5)
        # All rows share a zero-based 0-2bn L scale; each bar remains native/editable.
        Rule $slide "Zero axis $i" 257 ($top+3) 257 ($top+72)
        for($j=0;$j -lt 3;$j++){
            $year=@('2019','2021','2024 est.')[$j];$y=$top+5+$j*24
            [void](Label $slide "Year $i $j" $year 201 ($y-1) 52 15 10)
            $v=[double]::Parse([string]$row[$j+1],[Globalization.CultureInfo]::InvariantCulture)
            $bar=$slide.Shapes.AddShape(1,257,[single]$y,[single]($v/2*274),12);$bar.Name="Sector bar $i $j"
            $bar.Fill.ForeColor.ObjectThemeColor=$(if($j -eq 0){6}else{5});$bar.Line.Visible=0
            if($j -eq 2){$bar.Fill.ForeColor.ObjectThemeColor=2;$bar.Line.Visible=-1;$bar.Line.ForeColor.ObjectThemeColor=5;$bar.Line.Weight=0.9;$bar.Line.DashStyle=4}
            [void](Label $slide "Value $i $j" $row[$j+1] (263+$v/2*274) ($y-1) 43 15 10 $true 5)
        }
        Rule $slide "Sector row rule $i" 36 ($top+85) 874.8 ($top+85)
    }
    [void](Label $slide 'Chart scale note' 'Bars start at zero; all sectors use the same 0-2bn litre scale. Outlined bars are estimates.' 201 452 660 16 9)
    [void](Label $slide 'Interpretation' '2024 estimates apply 2018-2021 average fuel intensity to sector activity; attribution and road-use overlap require review.' 36 470 839 15 9.5)
    $slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$spec.note+"`r`rThree sector rows with comparable, zero-based horizontal bars. 2019/2021 observations; 2024 activity-based estimates. Values unchanged from v26."
    $stem='SA_Market_Story_2026-10-08_v27'
    $deck.SaveAs((Join-Path $qa "$stem.pptx"),24,-1);$deck.SaveAs((Join-Path $qa "$stem.pdf"),32)
    $deck.Export($qa,'PNG',1217,720)
    Write-Output "Built 43-page v27; sector table replaced with three chart rows."
}finally{$deck.Close()}
