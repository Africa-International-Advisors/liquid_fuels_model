$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$stem='Vopak_SA_Market_Story_2026_10_08_v15'
$out=Join-Path $root 'pptx/output/delivered/supporting'
$target=Join-Path $out "$stem.pptx"
if(Test-Path $target){throw 'Preserve existing output.'}
$story=Get-Content (Join-Path $root 'pptx/story/sa_market_story_row_icons_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$spec=$story.slides[2]
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $out 'archive/story_versions/V14_SA_market_story_Reference_visual_style_2026-10-08.pptx'),0,0,0)
try {
    $slide=$deck.Slides.Item(4)
    $shape=$slide.Shapes.Item('Table 46');$table=$shape.Table
    $top=$shape.Top+$table.Rows.Item(1).Height
    for($i=0;$i -lt 5;$i++){
        $cell=$table.Cell($i+2,1).Shape
        $cell.TextFrame.MarginLeft=35
        $cell.TextFrame.TextRange.Text=$spec.rows[$i][0]
        $path=Join-Path $root ($spec.icon_dir+'/icon_'+$spec.icons[$i]+'.png')
        $pic=$slide.Shapes.AddPicture($path,0,-1,40,($top+9),25,25)
        $pic.Name='Argument icon '+$spec.icons[$i]
        $top+=$table.Rows.Item($i+2).Height
    }
    $deck.SaveAs($target,24,-1)
    $deck.SaveAs((Join-Path $out "$stem.pdf"),32)
    $qa=Join-Path $root "pptx/qa/$stem"
    New-Item -ItemType Directory -Force $qa | Out-Null
    $deck.Export($qa,'PNG',1217,720)
}finally{$deck.Close()}
Write-Output 'Five SCR row icons added; PPTX/PDF exported.'
