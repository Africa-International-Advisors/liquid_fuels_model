$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$stem='Vopak_SA_Market_Story_2026_10_08_v17'
$out=Join-Path $root 'pptx/output/delivered/supporting'
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $out "$stem.pptx"),0,0,0)
try{
    foreach($page in @(6,8,9,10,12,13)){
        $s=$deck.Slides.Item($page)
        $rules=@($s.Shapes | Where-Object {$_.Name -eq 'Content margin panel rule'})
        foreach($shape in $rules){$shape.ZOrder(0)}
    }
    $deck.Save()
    $deck.SaveAs((Join-Path $out "$stem.pdf"),32)
    $deck.Export((Join-Path $root "pptx/qa/$stem"),'PNG',1217,720)
}finally{$deck.Close()}
