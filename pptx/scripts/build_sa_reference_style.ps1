$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$stem='Vopak_SA_Market_Story_2026_10_08_v14'
$out=Join-Path $root 'pptx/output/delivered/supporting'
$target=Join-Path $out "$stem.pptx"
if(Test-Path $target){throw 'Output exists; preserve delivered version.'}
$story=Get-Content (Join-Path $root 'pptx/story/sa_market_story_reference_style_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $out 'archive/story_versions/V13_SA_market_story_Consistent_exhibit_layouts_2026-10-08.pptx'),0,0,0)
try {
    for($i=2;$i -le $deck.Slides.Count;$i++){
        $deck.Slides.Item($i).Shapes.Title.TextFrame.TextRange.Font.Color.ObjectThemeColor=1
    }
    foreach($page in @(6,8,9,10,12,13)){
        $slide=$deck.Slides.Item($page)
        $old=$slide.Shapes.Item('Evidence chart')
        $x=$old.Left;$y=$old.Top;$w=$old.Width;$h=$old.Height
        $old.Delete()
        $new=$slide.Shapes.AddPicture((Join-Path $root $story.slides[$page-2].custom_chart),0,-1,$x,$y,$w,$h)
        $new.Name='Evidence chart'
    }
    $deck.Slides.Item(1).Shapes.Item('TextBox 9').TextFrame.TextRange.Text=$story.cover_status
    $deck.SaveAs($target,24,-1)
    $deck.SaveAs((Join-Path $out "$stem.pdf"),32)
    $qa=Join-Path $root "pptx/qa/$stem"
    New-Item -ItemType Directory -Force $qa | Out-Null
    $deck.Export($qa,'PNG',1217,720)
}finally{$deck.Close()}
Write-Output 'Reference style applied; PPTX, PDF and rendered slides exported.'
