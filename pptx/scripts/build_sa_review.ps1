param([string]$Version = 'v1')
$ErrorActionPreference = 'Stop'
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$story = Get-Content (Join-Path $root 'pptx/story/sa_review_signed_off_2026_10_07.json') -Raw | ConvertFrom-Json
$out = Join-Path $root 'pptx/output/delivered/supporting'
$qa = Join-Path $root "pptx/qa/sa_review_2026_10_07/$Version"
New-Item -ItemType Directory -Force $qa | Out-Null
$stem = "Vopak_SA_Review_Signed_Off_2026_10_07_$Version"
if (Test-Path (Join-Path $out "$stem.pptx")) { throw 'Use a new version; preserve existing outputs.' }
$app = New-Object -ComObject PowerPoint.Application
$deck = $app.Presentations.Open((Join-Path $root $story.style_reference), 0, 0, 0)
try {
    # Reuse the actual convergence cover and Header only layout, including its master.
    for ($i = $deck.Slides.Count; $i -ge 2; $i--) {
        if ($i -ne 26) { $deck.Slides.Item($i).Delete() }
    }
    for ($i = 1; $i -lt $story.slides.Count; $i++) {
        $copy = $deck.Slides.Item(2).Duplicate()
        $copy.Item(1).MoveTo($deck.Slides.Count)
    }
    $cover = $deck.Slides.Item(1)
    $cover.Shapes.Item('TextBox 4').TextFrame.TextRange.Text = "South Africa`rmarket story`rreview"
    $cover.Shapes.Item('TextBox 6').TextFrame.TextRange.Text = 'Agreed scope and work programme'
    $cover.Shapes.Item('TextBox 6').TextFrame.TextRange.Font.Size = 19
    $cover.Shapes.Item('TextBox 7').TextFrame.TextRange.Text = 'Durban and the Lesedi catchment'
    $cover.Shapes.Item('TextBox 8').TextFrame.TextRange.Text = '7 October 2026'
    $cover.Shapes.Item('TextBox 9').TextFrame.TextRange.Text = 'Scope signed off | Analysis pending'
    for ($i = 0; $i -lt $story.slides.Count; $i++) {
        $spec = $story.slides[$i]
        $s = $deck.Slides.Item($i + 2)
        $s.Shapes.Title.TextFrame.TextRange.Text = $spec.title
        $s.Shapes.Title.TextFrame.TextRange.Font.Name = 'Lato'
        $s.Shapes.Title.TextFrame.TextRange.Font.Size = 23
        $s.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text = [string]($i + 2)
        for ($n = 1; $n -le 4; $n++) {
            $nav = $s.Shapes.Item("Section navigation $n")
            $nav.Fill.ForeColor.ObjectThemeColor = $(if ($n -eq $spec.section) {5} else {2})
            $nav.Fill.ForeColor.TintAndShade = [single]$(if ($n -eq $spec.section) {0} else {-0.07})
            $nav.TextFrame.TextRange.Font.Color.ObjectThemeColor = $(if ($n -eq $spec.section) {2} else {5})
        }
        $s.Shapes.Item('TextBox 45').TextFrame.TextRange.Text = $spec.sub
        $s.Shapes.Item('TextBox 45').TextFrame.TextRange.Font.Size = 13
        $s.Shapes.Item('Unified source footer').TextFrame.TextRange.Text = $spec.note
        $s.Shapes.Item('Unified source footer').TextFrame.TextRange.Font.Size = 7.2
        $tableShape = $s.Shapes.Item('Table 46')
        $t = $tableShape.Table
        $nr = $spec.rows.Count + 1
        while ($t.Rows.Count -gt $nr) { $t.Rows.Item($t.Rows.Count).Delete() }
        $t.Columns.Item(1).Width = 165
        $t.Columns.Item(2).Width = 329
        $t.Columns.Item(3).Width = 344.8
        $tableShape.Top = 165.6
        for ($r = 1; $r -le $nr; $r++) {
            $t.Rows.Item($r).Height = [single]$(if ($r -eq 1) {28} else {297.4 / ($nr - 1)})
            for ($c = 1; $c -le 3; $c++) {
                $cell = $t.Cell($r,$c).Shape
                $cell.TextFrame.TextRange.Text = $(if ($r -eq 1) {$spec.headers[$c - 1]} else {$spec.rows[$r - 2][$c - 1]})
                $cell.TextFrame.MarginLeft = 3
                $cell.TextFrame.MarginRight = 9
                $cell.TextFrame.MarginTop = 7
                $cell.TextFrame.MarginBottom = 4
                $cell.TextFrame.TextRange.Font.Name = 'Lato'
                $cell.TextFrame.TextRange.Font.Size = $(if ($nr -ge 6) {12} else {13})
                $cell.TextFrame.TextRange.Font.Bold = $(if (($r -eq 1) -or ($c -eq 1)) {-1} else {0})
                $cell.TextFrame.TextRange.Font.Color.ObjectThemeColor = 1
                $cell.TextFrame.TextRange.Font.Underline = 0
                $cell.TextFrame.TextRange.ActionSettings.Item(1).Hyperlink.Address = ''
                $cell.TextFrame.TextRange.ActionSettings.Item(1).Hyperlink.SubAddress = ''
            }
        }
        $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = "Source: user feedback and explicit scope sign-off in this conversation, 7 October 2026. Style and existing coverage references: Vopak_Convergence_current.pptx, inspected 7 October 2026. Repository boundaries: CLAUDE.md; GATE_CHECKLIST.md; workstreams/README.md. No new market research or quantitative findings are asserted. " + $spec.note
        Write-Output "Prepared slide $($i + 2)"
    }
    $deck.SaveAs((Join-Path $out "$stem.pptx"),24,-1)
    $deck.SaveAs((Join-Path $out "$stem.pdf"),32)
    $deck.Export($qa,'PNG',1217,720)
    Write-Output "Created $stem.pptx and $stem.pdf; slides=$($deck.Slides.Count); renders=$qa"
} finally { $deck.Close() }
