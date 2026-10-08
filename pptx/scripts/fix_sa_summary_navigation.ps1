$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$out=Join-Path $root 'pptx/output/delivered/supporting'
$stem='Vopak_SA_Market_Story_2026_10_08_v18'
$target=Join-Path $out "$stem.pptx"
if(Test-Path $target){throw 'Preserve existing delivery.'}
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $out 'archive/story_versions/V17_SA_market_story_Aligned_exhibit_subtitles_2026-10-08.pptx'),0,0,0)
try{
    # Copy the established executive-summary navigation to the remaining summary slides.
    foreach($page in @(4,5)){
        $s=$deck.Slides.Item($page)
        for($n=1;$n -le 4;$n++){
            $s.Shapes.Item("SCR $n").Delete()
            $deck.Slides.Item(2).Shapes.Item("SCR $n").Copy()
            $copy=$s.Shapes.Paste().Item(1);$copy.Name="SCR $n"
        }
    }
    $deck.SaveAs($target,24,-1);$deck.SaveAs((Join-Path $out "$stem.pdf"),32)
    $qa=Join-Path $root "pptx/qa/$stem";New-Item -ItemType Directory -Force $qa | Out-Null
    $deck.Export($qa,'PNG',1217,720)
}finally{$deck.Close()}
