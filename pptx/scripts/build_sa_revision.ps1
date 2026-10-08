param([Parameter(Mandatory=$true)][string]$StoryFile,[Parameter(Mandatory=$true)][string]$Stem)
$ErrorActionPreference = 'Stop'
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$story = Get-Content (Join-Path $root $StoryFile) -Raw -Encoding UTF8 | ConvertFrom-Json
$out = Join-Path $root 'pptx/output/delivered/supporting'
$qa = Join-Path $root "pptx/qa/$Stem"
$target = Join-Path $out "$Stem.pptx"
if (Test-Path $target) { throw 'Output exists; choose a new version.' }
New-Item -ItemType Directory -Force $qa | Out-Null
function TextBox($slide, $name, $text, $x, $y, $w, $h, $size) {
    $sh = $slide.Shapes.AddTextbox(1,[single]$x,[single]$y,[single]$w,[single]$h)
    $sh.Name=$name
    $sh.TextFrame.MarginLeft=0; $sh.TextFrame.MarginRight=0
    $sh.TextFrame.MarginTop=0; $sh.TextFrame.MarginBottom=0
    $sh.TextFrame.TextRange.Text=$text
    $sh.TextFrame.TextRange.Font.Name='Lato'
    $sh.TextFrame.TextRange.Font.Size=[single]$size
    $sh.TextFrame.TextRange.Font.Color.ObjectThemeColor=1
    return $sh
}
$app = New-Object -ComObject PowerPoint.Application
$deck = $app.Presentations.Open((Join-Path $root $story.style_reference),0,0,0)
try {
    for ($i=$deck.Slides.Count;$i -ge 2;$i--) { if ($i -ne 26) { $deck.Slides.Item($i).Delete() } }
    for ($i=1;$i -lt $story.slides.Count;$i++) { $copy=$deck.Slides.Item(2).Duplicate(); $copy.Item(1).MoveTo($deck.Slides.Count) }
    $cover=$deck.Slides.Item(1)
    $cover.Shapes.Item('Rectangle 1').Fill.Solid()
    $cover.Shapes.Item('Rectangle 1').Fill.ForeColor.ObjectThemeColor=5
    $cover.Shapes.Item('TextBox 4').TextFrame.TextRange.Text=$story.cover_title
    $cover.Shapes.Item('TextBox 6').TextFrame.TextRange.Text=$story.cover_subtitle
    $cover.Shapes.Item('TextBox 6').TextFrame.TextRange.Font.Size=17
    $cover.Shapes.Item('TextBox 7').TextFrame.TextRange.Text=('Durban'+[char]0x2013+'Lesedi corridor into Gauteng')
    $cover.Shapes.Item('TextBox 8').TextFrame.TextRange.Text=$(if ($story.cover_date) {$story.cover_date} else {'7 October 2026'})
    $cover.Shapes.Item('TextBox 9').TextFrame.TextRange.Text=$story.cover_status
    $cover.Shapes.Item('TextBox 9').TextFrame.TextRange.Font.Size=12
    $master=$deck.Slides.Item(2).Master
    $logo=$master.Shapes.Item('Picture 2')
    $logo.LockAspectRatio=-1; $logo.Width=75; $logo.Left=780; $logo.Top=513
    for ($i=0;$i -lt $story.slides.Count;$i++) {
        $spec=$story.slides[$i]; $s=$deck.Slides.Item($i+2)
        if ($spec.divider) {
            $s.Delete()
            $copy=$deck.Slides.Item(1).Duplicate();$s=$copy.Item(1);$s.MoveTo($i+2)
            $s.Shapes.Item('TextBox 4').TextFrame.TextRange.Text=$spec.title
            $s.Shapes.Item('TextBox 6').TextFrame.TextRange.Text=$spec.subtitle
            $s.Shapes.Item('TextBox 9').TextFrame.TextRange.Text=$spec.note
            [void](TextBox $s 'Appendix page number' ([string]($i+2)) 864 513 28 19 11)
            continue
        }
        $s.Shapes.Title.TextFrame.TextRange.Text=$spec.title
        $s.Shapes.Title.TextFrame.TextRange.Font.Size=$(if($spec.title_font_size){$spec.title_font_size}else{23})
        $s.Shapes.Title.TextFrame.TextRange.Font.Color.ObjectThemeColor=$(if ($story.black_titles) {1} else {5})
        $number=$s.Shapes.Item('Slide Number Placeholder')
        $number.Left=864; $number.Top=513; $number.Width=28; $number.Height=19
        $number.TextFrame.TextRange.Text=[string]($i+2)
        $number.TextFrame.TextRange.Font.Size=11
        for ($n=4;$n -ge 1;$n--) { $s.Shapes.Item("Section navigation $n").Delete() }
        $labels=@('Executive summary','Situation','Complication','Resolution')
        for ($n=0;$n -lt 4;$n++) {
            $sh=$s.Shapes.AddShape(1,[single](36+$n*212),[single]7,[single]202.8,[single]22)
            $sh.Name="SCR $($n+1)"
            $active=($spec.section -eq ($n+1))
            $sh.Line.Visible=0; $sh.Fill.Solid()
            $sh.Fill.ForeColor.ObjectThemeColor=$(if ($active) {5} else {2})
            $sh.Fill.ForeColor.TintAndShade=[single]$(if ($active) {0} else {-0.08})
            $sh.TextFrame.MarginTop=2; $sh.TextFrame.MarginBottom=0
            $sh.TextFrame.TextRange.Text=$(if ($spec.section -eq 0) { @('Appendix','Supporting evidence','Calibration','Reference detail')[$n] } else { $labels[$n] })
            $sh.TextFrame.TextRange.Font.Name='Lato'; $sh.TextFrame.TextRange.Font.Size=11
            $sh.TextFrame.TextRange.Font.Color.ObjectThemeColor=$(if ($active) {2} else {5})
            $sh.TextFrame.TextRange.ParagraphFormat.Alignment=2
        }
        $s.Shapes.Item('TextBox 45').Delete()
        $footer=$s.Shapes.Item('Unified source footer')
        $footer.TextFrame.TextRange.Text=$spec.note
        $footer.TextFrame.TextRange.Font.Size=7.5
        $footer.Top=487; $footer.Height=19; $footer.Width=838.8
        if ($spec.chart -or $spec.custom_chart) {
            $s.Shapes.Item('Table 46').Delete()
            $png=$(if ($spec.custom_chart) {Join-Path $root $spec.custom_chart} else {Join-Path $root ("output/sa_review_2026_10_07/qa_story/" + [IO.Path]::GetFileNameWithoutExtension($spec.chart) + '.png')})
            if ($spec.side_text) {
                $picture=$s.Shapes.AddPicture($png,0,-1,36,165,590,227.95)
                $panelTitle=TextBox $s 'Context heading' $spec.side_title 652 143 219 27 14
                $panelTitle.TextFrame.TextRange.Font.Bold=-1
                $panelTitle.TextFrame.TextRange.Font.Color.ObjectThemeColor=5
                $panel=TextBox $s 'Context evidence' $spec.side_text 652 183 219 233 13
            } else {
                $picture=$s.Shapes.AddPicture($png,0,-1,55,122,800,309.09)
            }
            $picture.Name='Evidence chart'
            foreach($head in $spec.panel_subtitles){
                $subtitle=TextBox $s 'Aligned panel subtitle' $head.text $head.x 128 $head.width 18 12
                $subtitle.TextFrame.TextRange.Font.Bold=-1
                $subtitle.TextFrame.TextRange.ParagraphFormat.Alignment=1
            }
            if ($spec.margin_rules) {
                $ry=122+31*309.09/340
                if ($spec.custom_chart -match 'power_timeseries') {
                    $segments=@(@(36,(55+282*800/880)),@((55+304*800/880),(55+574*800/880)),@((55+596*800/880),874.8))
                } else {
                    $split=if($spec.custom_chart -match 'corridor_map'){560}elseif($spec.custom_chart -match 'turnover'){510}elseif($spec.custom_chart -match 'future_capacity'){325}else{590}
                    $cx=55+$split*800/880;$gap=11*800/880
                    $segments=@(@(36,($cx-$gap)),@(($cx+$gap),874.8))
                }
                foreach($seg in $segments){
                    $rule=$s.Shapes.AddLine([single]$seg[0],[single]$ry,[single]$seg[1],[single]$ry)
                    $rule.Name='Content margin panel rule';$rule.Line.ForeColor.ObjectThemeColor=1;$rule.Line.Transparency=.55;$rule.Line.Weight=.5
                }
            }
            $caption=TextBox $s 'Interpretation' $spec.takeaway 42 442 825 43 12
        } else {
            $shape=$s.Shapes.Item('Table 46'); $t=$shape.Table
            $nr=$spec.rows.Count+1
            $nc=$spec.headers.Count
            while ($t.Columns.Count -lt $nc) { [void]$t.Columns.Add() }
            while ($t.Rows.Count -lt $nr) { [void]$t.Rows.Add() }
            while ($t.Rows.Count -gt $nr) { $t.Rows.Item($t.Rows.Count).Delete() }
            $shape.Top=130
            $widths=$(if ($spec.column_widths) {$spec.column_widths} else {@(165,329,344.8)})
            for ($c=1;$c -le $nc;$c++) { $t.Columns.Item($c).Width=[single]$widths[$c-1] }
            $bodyHeight=$(if ($spec.body_height) {$spec.body_height} else {322})
            $headerHeight=$(if ($spec.header_height) {$spec.header_height} else {28})
            for ($r=1;$r -le $nr;$r++) {
                $t.Rows.Item($r).Height=[single]$(if ($r -eq 1) {$headerHeight} else {$bodyHeight/($nr-1)})
                for ($c=1;$c -le $nc;$c++) {
                    $cell=$t.Cell($r,$c).Shape
                    $cell.TextFrame.TextRange.Text=$(if ($r -eq 1) {$spec.headers[$c-1]} else {$spec.rows[$r-2][$c-1]})
                    $cell.TextFrame.MarginLeft=3; $cell.TextFrame.MarginRight=9
                    if ($spec.icons -and $c -eq 1 -and $r -gt 1) { $cell.TextFrame.MarginLeft=35 }
                    $cell.TextFrame.MarginTop=7; $cell.TextFrame.MarginBottom=4
                    $cell.TextFrame.TextRange.Font.Name='Lato'
                    $cell.TextFrame.TextRange.Font.Size=$(if ($spec.font_size) {$spec.font_size} elseif ($nr -ge 6) {12} else {13})
                    $cell.TextFrame.TextRange.Font.Bold=$(if (($r -eq 1) -or ($c -eq 1)) {-1} else {0})
                    $cell.TextFrame.TextRange.Font.Color.ObjectThemeColor=1
                    $cell.TextFrame.TextRange.Font.Underline=0
                    if ($spec.matrix -and $r -eq $c -and $r -gt 1) {
                        $cell.Fill.Solid()
                        $cell.Fill.ForeColor.ObjectThemeColor=5
                        $cell.Fill.ForeColor.TintAndShade=[single]$(if ($r -eq 3) {0} else {0.85})
                        $cell.TextFrame.TextRange.Font.Color.ObjectThemeColor=$(if ($r -eq 3) {2} else {5})
                        $cell.TextFrame.TextRange.Font.Bold=-1
                    }
                }
            }
            if ($spec.icons) {
                for ($j=0;$j -lt $spec.icons.Count;$j++) {
                    $iconDir=$(if ($spec.icon_dir) {$spec.icon_dir} else {'output/sa_feedback_2026_10_07'})
                    $iconPath=Join-Path $root ($iconDir+"/icon_"+$spec.icons[$j]+'.png')
                    $iconY=130+$headerHeight+$j*$bodyHeight/($nr-1)+9
                    [void]$s.Shapes.AddPicture($iconPath,0,-1,40,[single]$iconY,25,25)
                }
            }
            if ($spec.comparison_bars) {
                for($j=0;$j -lt $spec.comparison_bars.Count;$j++){
                    $top=130+$headerHeight+$j*$bodyHeight/($nr-1)
                    [void](TextBox $s 'Comparison unit' $spec.comparison_bars[$j].unit 204 ($top+6) 355 16 10)
                    $bar=$s.Shapes.AddPicture((Join-Path $root $spec.comparison_bars[$j].path),0,-1,204,($top+12),355,95.85)
                    $bar.Name='Demand comparison '+$spec.comparison_bars[$j].name
                }
                [void]$s.Shapes.AddPicture((Join-Path $root 'output/delivered/demand_support_2026_10_08/bars/legend.png'),0,-1,385,137,110,14.19)
            }
            if ($spec.caption) { $caption=TextBox $s 'Cell outputs' $spec.caption 42 458 825 27 11 }
        }
        $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$spec.note + "`rEvidence: output/delivered/sa_review_2026_10_07_v3/index.html. Comment dispositions: workstreams/WS0_governance/workplan/sa_review_comment_disposition_2026_10_07.csv. Review draft; scenario and commercial calibration pending."
    }
    $deck.SaveAs($target,24,-1)
} finally { try { $deck.Close() } catch { Write-Warning 'PowerPoint presentation was already closed.' } }

# Repair inherited hyperlinks and theme overrides in the copied package.
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=[IO.Compression.ZipFile]::Open($target,[IO.Compression.ZipArchiveMode]::Update)
try {
    foreach ($entry in @($zip.Entries | Where-Object {$_.FullName -match '^ppt/(slides/slide\d+|theme/theme\d+)\.xml$'})) {
        $name=$entry.FullName; $reader=New-Object IO.StreamReader($entry.Open()); [xml]$xml=$reader.ReadToEnd(); $reader.Close()
        $ns=New-Object Xml.XmlNamespaceManager($xml.NameTable)
        $ns.AddNamespace('a','http://schemas.openxmlformats.org/drawingml/2006/main')
        $ns.AddNamespace('p','http://schemas.openxmlformats.org/presentationml/2006/main')
        foreach ($node in @($xml.SelectNodes('//a:hlinkClick | //a:hlinkMouseOver',$ns))) { [void]$node.ParentNode.RemoveChild($node) }
        foreach ($node in @($xml.SelectNodes('//a:clrScheme/a:accent1/a:srgbClr',$ns))) { $node.SetAttribute('val','0A2373') }
        if ($name -match '^ppt/slides/slide(\d+)') {
            $sn=[int]$Matches[1]
            if ($sn -gt 1) {
                $active=$story.slides[$sn-2].section
                for ($n=1;$n -le 4;$n++) {
                    $shape=$xml.SelectSingleNode("//p:sp[p:nvSpPr/p:cNvPr[@name='SCR $n']]",$ns)
                    foreach ($pr in @($shape.SelectNodes('.//a:rPr | .//a:defRPr',$ns))) {
                        foreach ($old in @($pr.SelectNodes('a:solidFill | a:noFill',$ns))) { [void]$pr.RemoveChild($old) }
                        $fill=$xml.CreateElement('a','solidFill',$ns.LookupNamespace('a'))
                        $clr=$xml.CreateElement('a','schemeClr',$ns.LookupNamespace('a'))
                        $clr.SetAttribute('val',$(if ($active -eq $n) {'lt1'} else {'accent1'}))
                        [void]$fill.AppendChild($clr); [void]$pr.PrependChild($fill)
                    }
                }
            }
        }
        $entry.Delete(); $replacement=$zip.CreateEntry($name)
        $writer=New-Object IO.StreamWriter($replacement.Open()); $writer.Write($xml.OuterXml); $writer.Close()
    }
} finally { $zip.Dispose() }
$deck=$app.Presentations.Open($target,-1,0,0)
try {
    $deck.SaveAs((Join-Path $out "$Stem.pdf"),32)
    $deck.Export($qa,'PNG',1217,720)
} finally { try { $deck.Close() } catch { Write-Warning 'PowerPoint presentation was already closed.' } }
Write-Output "Created $Stem PPTX, PDF and review images."
