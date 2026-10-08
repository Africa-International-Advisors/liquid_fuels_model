$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$base=Join-Path $root 'pptx/output/delivered/supporting'
$target=Join-Path $base 'SA_Market_Story_v24.pptx'
if(Test-Path $target){throw 'Preserve existing delivery'}
$story=Get-Content (Join-Path $root 'pptx/story/sa_market_story_v24_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json
# Reuse the established native-table updater without invoking its build entry point.
$prior=Get-Content (Join-Path $PSScriptRoot 'build_sa_decisions_v23.ps1') -Raw
$start=$prior.IndexOf('function Populate(');$end=$prior.IndexOf('$app=New-Object')
. ([scriptblock]::Create($prior.Substring($start,$end-$start)))
function AppendixNav($s){
    for($n=1;$n -le 4;$n++){
        $sh=$s.Shapes.Item("SCR $n");$sh.Fill.ForeColor.ObjectThemeColor=2;$sh.Fill.ForeColor.TintAndShade=-.08
        $sh.TextFrame.TextRange.Font.Color.ObjectThemeColor=5
        $sh.TextFrame.TextRange.Text=@('Appendix','Supporting evidence','Calibration','Reference detail')[$n-1]
    }
}
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $base 'SA_Market_Story_v23.pptx'),0,0,0)
try{
    foreach($page in @(3,4,5,16)){Populate $deck.Slides.Item($page) $story.slides[$page-2]}
    foreach($page in @(35,36,37)){
        $copy=$deck.Slides.Item(14).Duplicate();$s=$copy.Item(1);$s.MoveTo($deck.Slides.Count)
        Populate $s $story.slides[$page-2];AppendixNav $s
    }
    $copy=$deck.Slides.Item(6).Duplicate();$s=$copy.Item(1);$s.MoveTo($deck.Slides.Count);AppendixNav $s
    for($j=$s.Shapes.Count;$j -ge 1;$j--){
        if($s.Shapes.Item($j).Name -in @('Evidence chart','Aligned panel subtitle','Content margin panel rule')){$s.Shapes.Item($j).Delete()}
    }
    $spec=$story.slides[36]
    $pic=$s.Shapes.AddPicture((Join-Path $root $spec.custom_chart),0,-1,55,122,800,309.09);$pic.Name='Evidence chart'
    $s.Shapes.Item('Interpretation').TextFrame.TextRange.Text=$spec.takeaway
    for($page=2;$page -le $deck.Slides.Count;$page++){
        $s=$deck.Slides.Item($page);$spec=$story.slides[$page-2]
        if($spec.divider){continue}
        $s.Shapes.Title.TextFrame.TextRange.Text=$spec.title
        $s.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text=[string]$page
        $s.Shapes.Item('Unified source footer').TextFrame.TextRange.Text=$spec.note
        $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$spec.note+"`r"+$spec.analysis_detail
    }
    $deck.Slides.Item(1).Shapes.Item('TextBox 9').TextFrame.TextRange.Text=$story.cover_status
    $deck.SaveAs($target,24,-1);$deck.SaveAs((Join-Path $base 'SA_Market_Story_v24.pdf'),32)
    $qa=Join-Path $root 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v24';New-Item -ItemType Directory -Force $qa | Out-Null
    $deck.Export($qa,'PNG',1217,720)
}finally{$deck.Close()}
