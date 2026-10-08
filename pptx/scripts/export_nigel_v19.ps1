$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$base=Join-Path $root 'pptx/output/delivered/supporting'
$target=Join-Path $base 'SA_Market_Story_v19.pptx'
if(Test-Path -LiteralPath $target){throw 'Preserve existing version.'}
Copy-Item -LiteralPath (Join-Path $base 'SA_Market_Story_v18_nigel.pptx') -Destination $target
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open($target,0,0,0)
try{
    $adjustments=@()
    for($page=2;$page -le $deck.Slides.Count;$page++){
        $s=$deck.Slides.Item($page)
        if($s.Shapes.HasTitle){
            $t=$s.Shapes.Title;$r=$t.TextFrame.TextRange
            $available=$t.Height-$t.TextFrame.MarginTop-$t.TextFrame.MarginBottom
            $original=$r.Font.Size
            while($r.BoundHeight -gt ($available+1) -and $r.Font.Size -gt 18){$r.Font.Size-=.5}
            if($r.Font.Size -ne $original){$adjustments+=@{page=$page;from=$original;to=$r.Font.Size}}
        }
    }
    $deck.Save()
    $deck.SaveAs((Join-Path $base 'SA_Market_Story_v19.pdf'),32)
    $qa=Join-Path $root 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v19'
    New-Item -ItemType Directory -Force $qa | Out-Null
    $deck.Export($qa,'PNG',1217,720)
    ConvertTo-Json -InputObject @($adjustments) | Set-Content (Join-Path $qa 'title_fit.json') -Encoding UTF8
}finally{$deck.Close()}
