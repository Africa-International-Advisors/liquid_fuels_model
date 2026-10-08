$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$base=Join-Path $root 'pptx/output/delivered/supporting'
$target=Join-Path $base 'SA_Market_Story_2026-10-08_v25.pptx'
if((Test-Path -LiteralPath $target) -or (Test-Path -LiteralPath (Join-Path $base 'archive/story_versions/SA_Market_Story_2026-10-08_v25.pptx'))){throw 'Delivered vintage exists; choose a new revision.'}
$story=Get-Content (Join-Path $root 'pptx/story/sa_market_story_v25_2026_10_08.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$code=Get-Content (Join-Path $PSScriptRoot 'build_sa_decisions_v23.ps1') -Raw
$start=$code.IndexOf('function Populate(');$end=$code.IndexOf('$app=New-Object')
. ([scriptblock]::Create($code.Substring($start,$end-$start)))
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $base 'archive/story_versions/SA_Market_Story_2026-10-08_v24.pptx'),0,0,0)
try {
 $copy=$deck.Slides.Item(10).Duplicate();$s=$copy.Item(1);$s.MoveTo($deck.Slides.Count)
 for($n=1;$n -le 4;$n++){
  $sh=$s.Shapes.Item("SCR $n");$sh.Fill.ForeColor.ObjectThemeColor=2;$sh.Fill.ForeColor.TintAndShade=-.08
  $sh.TextFrame.TextRange.Font.Color.ObjectThemeColor=5
  $sh.TextFrame.TextRange.Text=@('Appendix','Supporting evidence','Calibration','Reference detail')[$n-1]
 }
 $copy=$deck.Slides.Item(14).Duplicate();$s=$copy.Item(1);$s.MoveTo(10)
 $deck.Slides.Item(11).Delete()
 Populate $s $story.slides[8]
 for($n=1;$n -le 4;$n++){
  $sh=$s.Shapes.Item("SCR $n");$sh.Fill.ForeColor.ObjectThemeColor=$(if($n -eq 2){5}else{2});$sh.Fill.ForeColor.TintAndShade=[single]$(if($n -eq 2){0.0}else{-.08})
  $sh.TextFrame.TextRange.Font.Color.ObjectThemeColor=$(if($n -eq 2){2}else{5})
 }
 foreach($page in @(10,39)){
  $s=$deck.Slides.Item($page);$spec=$story.slides[$page-2]
  $s.Shapes.Title.TextFrame.TextRange.Text=$spec.title
  $s.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text=[string]$page
  $s.Shapes.Item('Unified source footer').TextFrame.TextRange.Text=$spec.note
  $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$spec.note+"`r"+$spec.analysis_detail
 }
 $deck.SaveAs($target,24,-1);$deck.SaveAs((Join-Path $base 'SA_Market_Story_2026-10-08_v25.pdf'),32)
 $qa=Join-Path $root 'pptx/qa/Vopak_SA_Market_Story_2026_10_08_v25';New-Item -ItemType Directory -Force $qa | Out-Null
 $deck.Export($qa,'PNG',1217,720)
}finally{$deck.Close()}
