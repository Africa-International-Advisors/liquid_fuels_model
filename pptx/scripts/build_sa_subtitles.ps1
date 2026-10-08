$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$out=Join-Path $root 'pptx/output/delivered/supporting'
$stem='Vopak_SA_Market_Story_2026_10_08_v17'
$target=Join-Path $out "$stem.pptx"
if(Test-Path $target){throw 'Preserve existing output.'}
$story=Get-Content (Join-Path $root 'pptx/story/sa_market_story_v17_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $out 'archive/story_versions/V16_SA_market_story_Network_map_icons_and_appendix_2026-10-08.pptx'),0,0,0)
try{
    foreach($page in @(6,8,9,10,12,13)){
        $s=$deck.Slides.Item($page);$spec=$story.slides[$page-2]
        $old=$s.Shapes.Item('Evidence chart');$x=$old.Left;$y=$old.Top;$w=$old.Width;$h=$old.Height;$old.Delete()
        $pic=$s.Shapes.AddPicture((Join-Path $root $spec.custom_chart),0,-1,$x,$y,$w,$h);$pic.Name='Evidence chart'
        foreach($head in $spec.panel_subtitles){
            $t=$s.Shapes.AddTextbox(1,[single]$head.x,128,[single]$head.width,18);$t.Name='Aligned panel subtitle'
            $t.TextFrame.MarginLeft=0;$t.TextFrame.MarginRight=0;$t.TextFrame.MarginTop=0;$t.TextFrame.MarginBottom=0
            $t.TextFrame.TextRange.Text=$head.text;$t.TextFrame.TextRange.Font.Name='Lato'
            $t.TextFrame.TextRange.Font.Size=12;$t.TextFrame.TextRange.Font.Bold=-1
            $t.TextFrame.TextRange.Font.Color.ObjectThemeColor=1;$t.TextFrame.TextRange.ParagraphFormat.Alignment=1
        }
        # Bring the existing native rules above the replacement chart picture.
        $rules=@($s.Shapes | Where-Object {$_.Name -eq 'Content margin panel rule'})
        foreach($shape in $rules){$shape.ZOrder(0)}
    }
    $deck.SaveAs($target,24,-1);$deck.SaveAs((Join-Path $out "$stem.pdf"),32)
    $qa=Join-Path $root "pptx/qa/$stem";New-Item -ItemType Directory -Force $qa | Out-Null
    $deck.Export($qa,'PNG',1217,720)
}finally{$deck.Close()}
