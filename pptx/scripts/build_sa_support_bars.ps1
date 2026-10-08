$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$base=Join-Path $root 'pptx/output/delivered/supporting'
$target=Join-Path $base 'SA_Market_Story_v21.pptx'
if(Test-Path $target){throw 'Preserve delivered output'}
$spec=(Get-Content (Join-Path $root 'pptx/story/sa_market_story_v21_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json).slides[5]
function Text($s,$name,$value,$x,$y,$w,$size){
    $t=$s.Shapes.AddTextbox(1,[single]$x,[single]$y,[single]$w,16);$t.Name=$name
    $t.TextFrame.MarginLeft=0;$t.TextFrame.MarginRight=0;$t.TextFrame.MarginTop=0;$t.TextFrame.MarginBottom=0
    $t.TextFrame.TextRange.Text=$value;$t.TextFrame.TextRange.Font.Name='Lato';$t.TextFrame.TextRange.Font.Size=[single]$size
    $t.TextFrame.TextRange.Font.Color.ObjectThemeColor=1
}
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $base 'SA_Market_Story_v20.pptx'),0,0,0)
try{
    $s=$deck.Slides.Item(7);$sh=$s.Shapes.Item('Table 46');$t=$sh.Table
    for($c=1;$c -le 3;$c++){$t.Cell(1,$c).Shape.TextFrame.TextRange.Text=$spec.headers[$c-1]}
    $top=$sh.Top+$t.Rows.Item(1).Height
    for($r=0;$r -lt 3;$r++){
        $t.Cell($r+2,2).Shape.TextFrame.TextRange.Text=''
        $t.Cell($r+2,3).Shape.TextFrame.TextRange.Text=$spec.rows[$r][2]
        Text $s 'Comparison unit' $spec.comparison_bars[$r].unit 204 ($top+6) 355 10
        $pic=$s.Shapes.AddPicture((Join-Path $root $spec.comparison_bars[$r].path),0,-1,204,($top+12),355,95.85)
        $pic.Name='Demand comparison '+$spec.comparison_bars[$r].name
        $top+=$t.Rows.Item($r+2).Height
    }
    # Compact year key beside the column heading.
    [void]$s.Shapes.AddPicture((Join-Path $root 'output/delivered/demand_support_2026_10_08/bars/legend.png'),0,-1,385,137,110,14.19)
    $s.Shapes.Item('Unified source footer').TextFrame.TextRange.Text=$spec.note
    $deck.SaveAs($target,24,-1);$deck.SaveAs((Join-Path $base 'SA_Market_Story_v21.pdf'),32)
    $qa=Join-Path $root 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v21';New-Item -ItemType Directory -Force $qa | Out-Null
    $deck.Export($qa,'PNG',1217,720)
}finally{$deck.Close()}
