param([Parameter(Mandatory=$true)][string]$SourcePath,[Parameter(Mandatory=$true)][string]$OutputPath)
$ErrorActionPreference='Stop'
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Resolve-Path -LiteralPath $SourcePath).Path,-1,0,0)
try{
    $fits=@()
    for($i=1;$i -le $deck.Slides.Count;$i++){
        $slide=$deck.Slides.Item($i)
        for($j=1;$j -le $slide.Shapes.Count;$j++){
            $shape=$slide.Shapes.Item($j)
            if($shape.HasTable -eq -1){
                for($r=1;$r -le $shape.Table.Rows.Count;$r++){for($c=1;$c -le $shape.Table.Columns.Count;$c++){
                    $cell=$shape.Table.Cell($r,$c).Shape;$tf=$cell.TextFrame
                    $available=$cell.Height-$tf.MarginTop-$tf.MarginBottom
                    if($tf.TextRange.BoundHeight -gt ($available+2)){
                        $fits+=@{page=$i;shape=$shape.Name;row=$r;column=$c;bound=$tf.TextRange.BoundHeight;available=$available;text=$tf.TextRange.Text}
                    }
                }}
            }
        }
        if($i%10 -eq 0){Write-Output "Text fit checked through page $i"}
    }
    ConvertTo-Json -Depth 6 -InputObject @($fits) | Set-Content -Encoding utf8 $OutputPath
    Write-Output "Table text-fit findings: $($fits.Count)"
    if($fits.Count -gt 0){throw 'Review text-fit findings before delivery.'}
}finally{$deck.Close()}
