$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$spec=Get-Content -Raw -Encoding utf8 (Join-Path $root 'pptx/story/sa_market_review_v28_2026_10_10.json') | ConvertFrom-Json
$app=New-Object -ComObject PowerPoint.Application
foreach($key in @('story','sizing')){
    $d=$spec.decks.$key
    $qa=Join-Path $root ('pptx/qa/market_review_2026_10_10/'+$key)
    $pptx=Join-Path $qa ('final_2/'+$d.output+'.pptx')
    $pdf=Join-Path $qa ('final_2/'+$d.output+'.pdf')
    $render=Join-Path $qa 'powerpoint_render'
    [void](New-Item -ItemType Directory -Force -Path $render)
    $deck=$app.Presentations.Open($pptx,-1,0,0)
    try{
        $deck.SaveAs($pdf,32)
        $deck.Export($render,'PNG',1217,720)
        Write-Output ($key+': exported PDF and '+$deck.Slides.Count+' slide previews')
    }finally{$deck.Close()}
}
