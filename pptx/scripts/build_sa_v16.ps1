param([switch]$Preview)
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$stem='Vopak_SA_Market_Story_2026_10_08_v16'
$out=Join-Path $root 'pptx/output/delivered/supporting'
$source=Join-Path $out 'archive/story_versions/V15_SA_market_story_SCR_argument_icons_2026-10-08.pptx'
if($Preview){$out=Join-Path $root 'pptx/output/working';$stem+='_preview';New-Item -ItemType Directory -Force $out | Out-Null}
$target=Join-Path $out "$stem.pptx"
if(Test-Path $target){throw 'Preserve existing delivery.'}
$story=Get-Content (Join-Path $root 'pptx/story/sa_market_story_v16_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json
function Rule($s,$x1,$x2,$y){
    $line=$s.Shapes.AddLine([single]$x1,[single]$y,[single]$x2,[single]$y)
    $line.Name='Content margin panel rule'
    $line.Line.ForeColor.ObjectThemeColor=1;$line.Line.Transparency=.55;$line.Line.Weight=.5
}
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open($source,0,0,0)
try {
    foreach($page in @(7,15)){
        $s=$deck.Slides.Item($page);$spec=$story.slides[$page-2]
        $shape=$s.Shapes.Item('Table 46');$t=$shape.Table;$top=$shape.Top+$t.Rows.Item(1).Height
        for($j=0;$j -lt $spec.icons.Count;$j++){
            $cell=$t.Cell($j+2,1).Shape;$cell.TextFrame.MarginLeft=35
            $cell.TextFrame.TextRange.Text=$spec.rows[$j][0]
            $pic=$s.Shapes.AddPicture((Join-Path $root ($spec.icon_dir+'/icon_'+$spec.icons[$j]+'.png')),0,-1,40,($top+9),25,25)
            $pic.Name='Argument icon '+$spec.icons[$j];$top+=$t.Rows.Item($j+2).Height
        }
    }
    foreach($page in @(6,8,9,10,12,13)){
        $s=$deck.Slides.Item($page);$spec=$story.slides[$page-2]
        $old=$s.Shapes.Item('Evidence chart');$x=$old.Left;$y=$old.Top;$w=$old.Width;$h=$old.Height;$old.Delete()
        $pic=$s.Shapes.AddPicture((Join-Path $root $spec.custom_chart),0,-1,$x,$y,$w,$h);$pic.Name='Evidence chart'
        $ry=$y+31*$h/340
        if($page -eq 12){
            Rule $s 36 ($x+282*$w/880) $ry
            Rule $s ($x+304*$w/880) ($x+574*$w/880) $ry
            Rule $s ($x+596*$w/880) 874.8 $ry
        }else{
            $split=switch($page){6{590}8{590}9{560}10{510}13{325}}
            $cx=$x+$split*$w/880;$gap=11*$w/880
            Rule $s 36 ($cx-$gap) $ry;Rule $s ($cx+$gap) 874.8 $ry
        }
    }
    # Reuse the supplied cover master and native cover shapes for the section page.
    $copy=$deck.Slides.Item(1).Duplicate();$cover=$copy.Item(1);$cover.MoveTo(16)
    $cover.Shapes.Item('TextBox 4').TextFrame.TextRange.Text='Appendix'
    $cover.Shapes.Item('TextBox 6').TextFrame.TextRange.Text='Supporting evidence and calibration'
    $cover.Shapes.Item('TextBox 7').TextFrame.TextRange.Text=('Durban'+[char]0x2013+'Lesedi corridor into Gauteng')
    $cover.Shapes.Item('TextBox 9').TextFrame.TextRange.Text='Detailed evidence, assumptions and remaining calibration requirements'
    $num=$cover.Shapes.AddTextbox(1,864,513,28,19);$num.Name='Appendix page number'
    $num.TextFrame.TextRange.Text='16';$num.TextFrame.TextRange.Font.Name='Lato';$num.TextFrame.TextRange.Font.Size=11
    for($page=2;$page -le $deck.Slides.Count;$page++){
        if($page -eq 16){continue}
        $s=$deck.Slides.Item($page);$spec=$story.slides[$page-2]
        $s.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text=[string]$page
        $s.Shapes.Item('Unified source footer').TextFrame.TextRange.Text=$spec.note
        if($spec.headers){
            $t=$s.Shapes.Item('Table 46').Table
            for($r=0;$r -lt $spec.rows.Count;$r++){for($c=0;$c -lt $spec.headers.Count;$c++){
                $t.Cell($r+2,$c+1).Shape.TextFrame.TextRange.Text=$spec.rows[$r][$c]
            }}
        }
    }
    $deck.Slides.Item(1).Shapes.Item('TextBox 9').TextFrame.TextRange.Text=$story.cover_status
    $deck.SaveAs($target,24,-1);$deck.SaveAs((Join-Path $out "$stem.pdf"),32)
    $qa=Join-Path $root "pptx/qa/$stem";New-Item -ItemType Directory -Force $qa | Out-Null
    $deck.Export($qa,'PNG',1217,720)
}finally{$deck.Close()}
Write-Output 'Updated deck and PDF exported with Appendix cover at page 16.'
