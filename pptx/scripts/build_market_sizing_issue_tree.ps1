param([switch]$IncludeRequests, [ValidateSet('rows','columns','flow')][string]$Layout = 'rows', [datetime]$BuildTime = (Get-Date))
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$referencePath = Join-Path $repoRoot 'pptx/output/delivered/supporting/archive/story_versions/SA_Market_Story_2026-10-08_v25.pptx'
# Naming convention: ddmmyyyy_filename_vHHMM, with the build time rounded to the nearest half hour.
$halfHours = [math]::Round(($BuildTime.Hour * 60 + $BuildTime.Minute) / 30, [MidpointRounding]::AwayFromZero)
$stamp = $BuildTime.Date.AddMinutes(30 * $halfHours)
$outputStem = '{0}_Vopak_Market_Sizing_v{1}' -f $stamp.ToString('ddMMyyyy'), $stamp.ToString('HHmm')
$outputDirectory = Join-Path $repoRoot 'pptx/output/delivered/supporting'
$targetPptx = Join-Path $outputDirectory ($outputStem + '.pptx')
$targetPdf = Join-Path $outputDirectory ($outputStem + '.pdf')
$qaDirectory = Join-Path $repoRoot ('pptx/qa/' + $outputStem)
if ((Test-Path -LiteralPath $targetPptx) -or (Test-Path -LiteralPath $targetPdf)) { throw ('Preserve previous outputs: ' + $outputStem + ' already exists in this half hour; rebuild later or pass -BuildTime.') }
[void](New-Item -ItemType Directory -Force -Path $qaDirectory)
$layoutNote = $(if ($Layout -eq 'rows') {
    'Layout: strict three rows. Row 1 national consumption, gross imports, domestic production and market sizing. Row 2 demand by use, ports, inland (pipeline, road and rail) and the Durban and Lesedi site markets. Row 3 demand parameters, supply and route parameters and market share analysis. The investment test runs along the bottom. Imported product also reaches inland catchments by pipeline.'
} elseif ($Layout -eq 'flow') {
    'Layout: four columns and four rows. Column 2 reads source (imports, production), route (ports, inland delivery), destination (coastal, inland demand) then parameters. Sources and destinations each add to national consumption; routes are throughput and overlap, so they do not add. Volume tags come from pptx/story/issue_tree_volumes_2026_10_08.json, built by pptx/scripts/issue_tree_volumes.py: 2023 department sales (observed), 2023 department trade review (rounded narrative, not customs), production implied as sales less imports plus exports with stock change unknown, and 2022 provincial sales split into coastal (KZN, WC, EC) and inland provinces as a presentation proxy, not a registered assumption. The PS figure of about 20B litres likely reflects 2024; FIASA 2024 (20.8B) remains unverified. All other tags are pending the named data requests.'
} else {
    'Layout: four columns and three rows. Columns are national demand, supply and delivery, Vopak opportunity and investment. Market share analysis feeds the investment column, which reads from achievable capture to existing assets to new investment and returns. Resolution is left to the narrative. Imported product also reaches inland catchments by pipeline.'
})

function Add-Text($slide, $name, $copy, $x, $y, $w, $h, $fontSize = 12, $bold = $false, $theme = 1) {
    $shape = $slide.Shapes.AddTextbox(1,[single]$x,[single]$y,[single]$w,[single]$h)
    $shape.Name = $name
    $shape.TextFrame.MarginLeft = 0; $shape.TextFrame.MarginRight = 0
    $shape.TextFrame.MarginTop = 0; $shape.TextFrame.MarginBottom = 0
    $shape.TextFrame.WordWrap = -1; $shape.TextFrame.AutoSize = 0
    $text = $shape.TextFrame.TextRange
    $text.Text = $copy
    $text.Font.Name = 'Lato'; $text.Font.Size = [single]$fontSize
    $text.Font.Bold = $(if ($bold) { -1 } else { 0 })
    $text.Font.Color.ObjectThemeColor = $theme
    $text.ParagraphFormat.SpaceAfter = 2
    $shape.TextFrame2.AutoSize = 0
    $shape.Left = [single]$x; $shape.Top = [single]$y
    $shape.Width = [single]$w; $shape.Height = [single]$h
    return $shape
}

function Add-Rule($slide, $name, $x1, $y1, $x2, $y2, $arrow = $false, $dashed = $false, $theme = 5) {
    $shape = $slide.Shapes.AddConnector(1,[single]$x1,[single]$y1,[single]$x2,[single]$y2)
    $shape.Name = $name
    $shape.Line.ForeColor.ObjectThemeColor = $theme
    $shape.Line.Weight = $(if ($arrow) { 1.0 } else { 0.65 })
    if ($arrow) { $shape.Line.EndArrowheadStyle = 3 }
    if ($dashed) { $shape.Line.DashStyle = 4 }
    return $shape
}

function Add-Block($slide, $name, $heading, $copy, $x, $y, $w, $h, $fontSize = 12) {
    $shape = Add-Text $slide $name ($heading + "`r" + $copy) $x $y $w $h $fontSize
    $headingRange = $shape.TextFrame.TextRange.Paragraphs(1,1)
    $headingRange.Font.Bold = -1; $headingRange.Font.Color.ObjectThemeColor = 5
    $headingRange.ParagraphFormat.SpaceAfter = 5
    return $shape
}

function Add-Box($slide, $name, $heading, $copy, $x, $y, $w, $h, $fontSize = 11) {
    # Outlined rectangle so connectors can attach to visible edges.
    $shape = $slide.Shapes.AddShape(1,[single]$x,[single]$y,[single]$w,[single]$h)
    $shape.Name = $name
    $shape.Fill.Visible = 0
    $shape.Line.ForeColor.ObjectThemeColor = 5
    $shape.Line.Weight = 0.75
    $shape.Shadow.Visible = 0
    $shape.TextFrame.MarginLeft = 6; $shape.TextFrame.MarginRight = 6
    $shape.TextFrame.MarginTop = 4; $shape.TextFrame.MarginBottom = 3
    $shape.TextFrame.WordWrap = -1; $shape.TextFrame.AutoSize = 0
    $shape.TextFrame.VerticalAnchor = 1
    $text = $shape.TextFrame.TextRange
    $text.Text = $heading + "`r" + $copy
    $text.ParagraphFormat.Alignment = 1
    $text.Font.Name = 'Lato'; $text.Font.Size = [single]$fontSize
    $text.Font.Bold = 0; $text.Font.Color.ObjectThemeColor = 1
    $text.ParagraphFormat.SpaceAfter = 2
    $headingRange = $text.Paragraphs(1,1)
    $headingRange.Font.Bold = -1; $headingRange.Font.Color.ObjectThemeColor = 5
    $headingRange.ParagraphFormat.SpaceAfter = 4
    return $shape
}

function Add-Link($slide, $name, $from, $fromSite, $to, $toSite, $elbow = $false, $dashed = $false, $x1 = 0, $y1 = 0) {
    # Connector glued to shape edges. Rectangle sites: 1 top, 2 left, 3 bottom, 4 right.
    # With $from = $null the start stays at ($x1,$y1) and only the arrowhead is glued.
    $shape = $slide.Shapes.AddConnector($(if ($elbow) { 2 } else { 1 }),[single]$x1,[single]$y1,[single]($x1 + 1),[single]($y1 + 1))
    $shape.Name = $name
    if ($null -ne $from) { $shape.ConnectorFormat.BeginConnect($from,$fromSite) }
    $shape.ConnectorFormat.EndConnect($to,$toSite)
    $shape.Line.ForeColor.ObjectThemeColor = 5
    $shape.Line.Weight = 1.0
    $shape.Line.EndArrowheadStyle = 2
    if ($dashed) { $shape.Line.DashStyle = 4 }
    return $shape
}

function Add-Marker($slide, $box, $copy, $x = 0, $y = 0) {
    # Small navy pill: on a box it sits top-right; with $box = $null it is placed at ($x,$y) for the legend.
    if ($null -ne $box) { $x = $box.Left + $box.Width - 16; $y = $box.Top - 6 }
    $marker = $slide.Shapes.AddShape(5,[single]$x,[single]$y,[single]26,[single]12)
    $marker.Name = $(if ($null -ne $box) { $box.Name + ' deep dive' } else { 'Deep dive legend marker' })
    $marker.Line.Visible = 0
    $marker.Shadow.Visible = 0
    $marker.Fill.ForeColor.ObjectThemeColor = 5
    $marker.TextFrame.MarginLeft = 0; $marker.TextFrame.MarginRight = 0
    $marker.TextFrame.MarginTop = 0; $marker.TextFrame.MarginBottom = 0
    $marker.TextFrame.WordWrap = 0
    $marker.TextFrame.TextRange.Text = $copy
    $marker.TextFrame.TextRange.Font.Name = 'Lato'
    $marker.TextFrame.TextRange.Font.Size = 8
    $marker.TextFrame.TextRange.Font.Bold = -1
    $marker.TextFrame.TextRange.Font.Color.RGB = 16777215
    $marker.TextFrame.TextRange.ParagraphFormat.Alignment = 2
    $marker.TextFrame.VerticalAnchor = 3
    return $marker
}

function Add-Tag($slide, $box, $copy) {
    # Volume/status tag pinned to the bottom of a box. Values in navy; pending items in grey.
    # The box copy must end above the tag line, or the two overprint.
    $copyBottom = $box.Top + $box.TextFrame.MarginTop + $box.TextFrame.TextRange.BoundHeight
    if ($copyBottom -gt ($box.Top + $box.Height - 15)) { throw ("Box copy runs into its tag: '{0}' ({1}): copy ends {2:0.0}, tag starts {3:0.0}" -f $box.Name, $box.TextFrame.TextRange.Paragraphs(1,1).Text.Trim(), $copyBottom, ($box.Top + $box.Height - 15)) }
    $tag = Add-Text $slide ($box.Name + ' tag') $copy ($box.Left + 6) ($box.Top + $box.Height - 15) ($box.Width - 12) 12 9 $true 5
    if ($copy -like 'Pending*') {
        $tag.TextFrame.TextRange.Font.Bold = 0
        $tag.TextFrame.TextRange.Font.Color.RGB = 8421504
    }
    return $tag
}

$powerPoint = New-Object -ComObject PowerPoint.Application
# Open as an untitled copy. The reference, master and named layout remain preserved.
$deck = $powerPoint.Presentations.Open($referencePath,0,-1,0)
try {
    for ($slideIndex = $deck.Slides.Count; $slideIndex -ge 1; $slideIndex--) {
        if ($slideIndex -ne 14 -and -not ($Layout -eq 'flow' -and $slideIndex -eq 1)) { $deck.Slides.Item($slideIndex).Delete() }
    }
    $slide = $deck.Slides.Item($deck.Slides.Count)
    $coverOffset = $(if ($Layout -eq 'flow') { 1 } else { 0 })
    if ($slide.CustomLayout.Name -ne 'Header only') { throw 'Expected supplied Header only layout.' }
    $slide.Shapes.Item('Table 46').Delete()
    $slide.Shapes.Title.TextFrame.TextRange.Text = 'Durban and Lesedi market sizing and investment issue tree'
    $slide.Shapes.Title.TextFrame.TextRange.Font.Size = 22
    $slide.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text = '1'
    for ($navIndex = 1; $navIndex -le 4; $navIndex++) {
        $nav = $slide.Shapes.Item("SCR $navIndex")
        $nav.Fill.ForeColor.ObjectThemeColor = $(if ($navIndex -eq 4) { 5 } else { 2 })
        $nav.Fill.ForeColor.TintAndShade = [single]$(if ($navIndex -eq 4) { 0 } else { -0.035 })
        $nav.TextFrame.TextRange.Font.Color.ObjectThemeColor = $(if ($navIndex -eq 4) { 2 } else { 5 })
    }

    if ($Layout -eq 'rows') {
        # Native PowerPoint diagram. All boxes, text and connectors remain editable.
        [void](Add-Text $slide 'Demand heading' '1  NATIONAL DEMAND' 36 129 174 19 12 $true 5)
        [void](Add-Text $slide 'System heading' '2  SUPPLY AND DELIVERY' 245 129 324 19 12 $true 5)
        [void](Add-Text $slide 'Terminal heading' '3  VOPAK OPPORTUNITY' 608 129 267 19 12 $true 5)
        foreach ($span in @(@(36,210),@(245,569),@(608,875))) {
            [void](Add-Rule $slide 'Column heading rule' $span[0] 151 $span[1] 151 $false $false 1)
        }

        # Strict three-row grid. Row 1: totals; row 2: breakdown; row 3: parameters and share analysis.
        $rowTop = @(160,246,332); $rowHeight = 70
        $national = Add-Box $slide 'National market' 'National consumption' "~20B litres/year discussed`rPetrol and diesel by destination`rPS starting point, to reconcile" 36 $rowTop[0] 174 $rowHeight 10.5
        $uses = Add-Box $slide 'Sector demand' 'Demand by use' "Road, mining, industry, agriculture`rPower and other uses" 36 $rowTop[1] 174 $rowHeight 10.5
        $demandParameters = Add-Box $slide 'Demand parameters' 'Demand parameters' "GDP and sector activity`rEVs, fleet turnover, ICE efficiency`rFreight, prices, power dispatch" 36 $rowTop[2] 174 $rowHeight 10.5

        $imports = Add-Box $slide 'Imports' 'Gross imports' "By product and entry point`rExports shown separately" 245 $rowTop[0] 146 $rowHeight 10.5
        $production = Add-Box $slide 'Production' 'Domestic production' "Refinery output and yields`rOwn storage and distribution" 414 $rowTop[0] 155 $rowHeight 10.5
        # Imports arrive through ports; domestic output and onward inland delivery move by pipeline, road and rail.
        $ports = Add-Box $slide 'Ports' 'Ports' "Durban, Richards Bay, other`rReceipt by product" 245 $rowTop[1] 146 $rowHeight 10.5
        $inland = Add-Box $slide 'Inland' 'Inland' "NMPP / TM2 / DJP pipelines`rRoad and rail to catchments" 414 $rowTop[1] 155 $rowHeight 10.5
        $supplyParameters = Add-Box $slide 'Supply and route parameters' 'Supply and route parameters' "Refinery closures / restarts and gas availability`rDelivered cost, competing routes, access and contracts`rPort, pipeline and rail capacity and reliability" 245 $rowTop[2] 324 $rowHeight 10.5

        # Supply and delivery together set the market Vopak can reach, which is then allocated by site.
        $marketSizing = Add-Box $slide 'Market sizing' 'Market sizing' "Feasible volumes Vopak can reach`rDurban and Lesedi, shared flows counted once" 608 $rowTop[0] 267 $rowHeight 10.5
        $durban = Add-Box $slide 'Durban opportunity' 'Durban market' "Via Vopak Durban`rTo reachable customers" 608 $rowTop[1] 128 $rowHeight 10.5
        $lesedi = Add-Box $slide 'Lesedi opportunity' 'Lesedi market' "Inland demand served`rReceipt / dispatch links" 747 $rowTop[1] 128 $rowHeight 10.5
        $share = Add-Box $slide 'Share and headroom' 'Market share analysis' "Client throughput / site market = share`rSite market less current capture = headroom" 608 $rowTop[2] 267 $rowHeight 10.5

        [void](Add-Link $slide 'Uses determine demand' $uses 1 $national 3)
        [void](Add-Link $slide 'Demand parameter effect' $demandParameters 1 $uses 3 $false $true)
        [void](Add-Link $slide 'Demand sets import requirement' $national 4 $imports 2)
        [void](Add-Link $slide 'Import route' $imports 3 $ports 1)
        [void](Add-Link $slide 'Domestic route' $production 3 $inland 1)
        [void](Add-Link $slide 'Ports to inland' $ports 4 $inland 2)
        [void](Add-Link $slide 'Supply parameter effect on ports' $null 0 $ports 3 $false $true 318 $rowTop[2])
        [void](Add-Link $slide 'Supply parameter effect on inland' $null 0 $inland 3 $false $true 491.5 $rowTop[2])
        [void](Add-Link $slide 'Supply into market sizing' $production 4 $marketSizing 2)
        [void](Add-Link $slide 'Delivery into market sizing' $inland 4 $marketSizing 2 $true)
        [void](Add-Link $slide 'Market sizing to Durban' $null 0 $durban 1 $false $false 672 ($rowTop[0] + $rowHeight))
        [void](Add-Link $slide 'Market sizing to Lesedi' $null 0 $lesedi 1 $false $false 811 ($rowTop[0] + $rowHeight))
        (Add-Rule $slide 'Durban into share' 672 ($rowTop[1] + $rowHeight) 672 $rowTop[2] $true).Line.EndArrowheadStyle = 2
        (Add-Rule $slide 'Lesedi into share' 811 ($rowTop[1] + $rowHeight) 811 $rowTop[2] $true).Line.EndArrowheadStyle = 2

        # Investment branch uses the market headroom as its starting point.
        $bottomTop = 424
        $capture = Add-Box $slide 'Additional capture' 'Achievable additional capture' "Customers, contracts, competition`rTest capture within the opportunity" 36 $bottomTop 187 52 10
        $capacity = Add-Box $slide 'Existing capacity' 'Existing assets and improvements' "Working tanks, turns and constraints`rTest receipt, storage and dispatch" 253 $bottomTop 187 52 10
        $economics = Add-Box $slide 'Investment economics' 'New investment and returns' "Incremental volume, cost and capex`rCompare alternatives and downside" 471 $bottomTop 187 52 10
        $resolution = Add-Box $slide 'Resolution' 'Resolution' "Vopak share at each site`rScope for new investment" 688 $bottomTop 187 52 10
        $investmentBus = $rowTop[2] + $rowHeight + 11
        [void](Add-Rule $slide 'Capture into investment 1' 741.5 ($rowTop[2] + $rowHeight) 741.5 $investmentBus)
        [void](Add-Rule $slide 'Capture into investment 2' 741.5 $investmentBus 129.5 $investmentBus)
        [void](Add-Link $slide 'Capture into investment 3' $null 0 $capture 1 $false $false 129.5 $investmentBus)
        [void](Add-Link $slide 'Capture to capacity' $capture 4 $capacity 2)
        [void](Add-Link $slide 'Capacity to returns' $capacity 4 $economics 2)
        [void](Add-Link $slide 'Returns to resolution' $economics 4 $resolution 2)
    } elseif ($Layout -eq 'columns') {
        # Four columns, three rows. Investment testing replaces the bottom chain; Resolution is left to the narrative.
        # Short lines so no box copy wraps at 11pt.
        # Light panel behind each column groups the major blocks; boxes are filled white to sit on it.
        foreach ($panel in @(@('Demand panel',36,150),@('Supply panel',210,252),@('Opportunity panel',486,225),@('Investment panel',735,140))) {
            $panelShape = $slide.Shapes.AddShape(1,[single]($panel[1] - 8),[single]122,[single]($panel[2] + 16),[single]361)
            $panelShape.Name = $panel[0]
            $panelShape.Line.Visible = 0
            $panelShape.Shadow.Visible = 0
            # Soft cool grey (RGB 238, 241, 246) rather than a tint of the navy accent.
            $panelShape.Fill.ForeColor.RGB = 16183790
        }
        [void](Add-Text $slide 'Demand heading' '1  NATIONAL DEMAND' 36 129 150 19 12 $true 5)
        [void](Add-Text $slide 'System heading' '2  SUPPLY AND DELIVERY' 210 129 252 19 12 $true 5)
        [void](Add-Text $slide 'Terminal heading' '3  VOPAK OPPORTUNITY' 486 129 225 19 12 $true 5)
        [void](Add-Text $slide 'Investment heading' '4  INVESTMENT' 735 129 140 19 12 $true 5)
        foreach ($span in @(@(36,186),@(210,462),@(486,711),@(735,875))) {
            [void](Add-Rule $slide 'Column heading rule' $span[0] 151 $span[1] 151 $false $false 1)
        }

        $rowTop = @(160,272,384); $rowHeight = 94; $fontSize = 11
        $national = Add-Box $slide 'National market' 'National consumption' "~20B litres/year (PS)`rPetrol and diesel`rBy destination`rTo reconcile" 36 $rowTop[0] 150 $rowHeight $fontSize
        $uses = Add-Box $slide 'Sector demand' 'Demand by use' "Road and mining`rIndustry and agriculture`rPower and other uses" 36 $rowTop[1] 150 $rowHeight $fontSize
        $demandParameters = Add-Box $slide 'Demand parameters' 'Demand parameters' "GDP and sectors`rEVs, fleet, efficiency`rFreight, prices, power" 36 $rowTop[2] 150 $rowHeight $fontSize

        $imports = Add-Box $slide 'Imports' 'Gross imports' "By product`rBy entry point`rExports separate" 210 $rowTop[0] 120 $rowHeight $fontSize
        $production = Add-Box $slide 'Production' 'Domestic production' "Refinery output`rProduct yields`rOwn distribution" 342 $rowTop[0] 120 $rowHeight $fontSize
        # Imports arrive through ports; domestic output and onward inland delivery move by pipeline, road and rail.
        $ports = Add-Box $slide 'Ports' 'Ports' "Durban`rRichards Bay`rOther gateways" 210 $rowTop[1] 120 $rowHeight $fontSize
        $inland = Add-Box $slide 'Inland' 'Inland' "NMPP / TM2 / DJP`rRoad and rail`rTo catchments" 342 $rowTop[1] 120 $rowHeight $fontSize
        $supplyParameters = Add-Box $slide 'Supply and route parameters' 'Supply and route parameters' "Refinery closures, restarts, gas`rDelivered cost, routes, contracts`rPort, pipeline, rail capacity" 210 $rowTop[2] 252 $rowHeight $fontSize

        $marketSizing = Add-Box $slide 'Market sizing' 'Market sizing' "Feasible volumes Vopak can reach`rDurban and Lesedi combined`rShared flows counted once" 486 $rowTop[0] 225 $rowHeight $fontSize
        $durban = Add-Box $slide 'Durban opportunity' 'Durban market' "Coastal catchment`rShip receipt`rOnward dispatch" 486 $rowTop[1] 108 $rowHeight $fontSize
        $lesedi = Add-Box $slide 'Lesedi opportunity' 'Lesedi market' "Inland catchment`rPipeline receipt`rRoad dispatch" 603 $rowTop[1] 108 $rowHeight $fontSize
        $share = Add-Box $slide 'Share and headroom' 'Market share analysis' "Throughput / site market = share`rSite market less capture = headroom" 486 $rowTop[2] 225 $rowHeight $fontSize

        $capture = Add-Box $slide 'Additional capture' 'Additional capture' "Customers, contracts`rCompetition`rCapture within market" 735 $rowTop[0] 140 $rowHeight $fontSize
        $capacity = Add-Box $slide 'Existing capacity' 'Existing assets' "Tanks and turns`rReceipt and dispatch`rOperating improvements" 735 $rowTop[1] 140 $rowHeight $fontSize
        $economics = Add-Box $slide 'Investment economics' 'New investment' "Incremental volume`rCost and capex`rAlternatives, downside" 735 $rowTop[2] 140 $rowHeight $fontSize

        [void](Add-Link $slide 'Uses determine demand' $uses 1 $national 3)
        [void](Add-Link $slide 'Demand parameter effect' $demandParameters 1 $uses 3 $false $true)
        [void](Add-Link $slide 'Demand sets import requirement' $national 4 $imports 2)
        [void](Add-Link $slide 'Import route' $imports 3 $ports 1)
        [void](Add-Link $slide 'Domestic route' $production 3 $inland 1)
        [void](Add-Link $slide 'Ports to inland' $ports 4 $inland 2)
        [void](Add-Link $slide 'Supply parameter effect on ports' $null 0 $ports 3 $false $true 270 $rowTop[2])
        [void](Add-Link $slide 'Supply parameter effect on inland' $null 0 $inland 3 $false $true 402 $rowTop[2])
        [void](Add-Link $slide 'Supply into market sizing' $production 4 $marketSizing 2)
        [void](Add-Link $slide 'Delivery into market sizing' $inland 4 $marketSizing 2 $true)
        [void](Add-Link $slide 'Market sizing to Durban' $null 0 $durban 1 $false $false 540 ($rowTop[0] + $rowHeight))
        [void](Add-Link $slide 'Market sizing to Lesedi' $null 0 $lesedi 1 $false $false 657 ($rowTop[0] + $rowHeight))
        (Add-Rule $slide 'Durban into share' 540 ($rowTop[1] + $rowHeight) 540 $rowTop[2] $true).Line.EndArrowheadStyle = 2
        (Add-Rule $slide 'Lesedi into share' 657 ($rowTop[1] + $rowHeight) 657 $rowTop[2] $true).Line.EndArrowheadStyle = 2

        foreach ($box in @($national,$uses,$demandParameters,$imports,$production,$ports,$inland,$supplyParameters,$marketSizing,$durban,$lesedi,$share,$capture,$capacity,$economics)) {
            $box.Fill.Visible = -1
            $box.Fill.ForeColor.RGB = 16777215
        }

        # Headroom starts the investment test, which then reads top to bottom.
        [void](Add-Link $slide 'Capture into investment' $share 4 $capture 2 $true)
        [void](Add-Link $slide 'Capture to capacity' $capture 3 $capacity 1)
        [void](Add-Link $slide 'Capacity to returns' $capacity 3 $economics 1)
    } else {
        # Four columns, four rows. Column 2 reads source -> route -> destination; sources and destinations each add to consumption.
        $volumes = Get-Content -Raw -LiteralPath (Join-Path $repoRoot 'pptx/story/issue_tree_volumes_2026_10_08.json') | ConvertFrom-Json
        function Format-Volume($item, $label) { '{0} · {1:0.0}B L · {2}' -f $item.year, $item.billion_litres, $label }
        $rowTop = @(158,242,326,410); $rowHeight = 70; $fontSize = 10.5
        foreach ($panel in @(@('Demand panel',36,150),@('Supply panel',210,252),@('Opportunity panel',486,225),@('Investment panel',735,140))) {
            $panelShape = $slide.Shapes.AddShape(1,[single]($panel[1] - 8),[single]122,[single]($panel[2] + 16),[single]362)
            $panelShape.Name = $panel[0]
            $panelShape.Line.Visible = 0
            $panelShape.Shadow.Visible = 0
            # Soft cool grey (RGB 238, 241, 246) rather than a tint of the navy accent.
            $panelShape.Fill.ForeColor.RGB = 16183790
        }
        [void](Add-Text $slide 'Demand heading' '1  NATIONAL DEMAND' 36 129 150 19 12 $true 5)
        [void](Add-Text $slide 'System heading' '2  SUPPLY AND DELIVERY' 210 129 252 19 12 $true 5)
        [void](Add-Text $slide 'Terminal heading' '3  VOPAK OPPORTUNITY' 486 129 225 19 12 $true 5)
        [void](Add-Text $slide 'Investment heading' '4  INVESTMENT' 735 129 140 19 12 $true 5)
        foreach ($span in @(@(36,186),@(210,462),@(486,711),@(735,875))) {
            [void](Add-Rule $slide 'Column heading rule' $span[0] 151 $span[1] 151 $false $false 1)
        }

        $national = Add-Box $slide 'National market' 'National consumption' "Petrol and diesel sales`rPS discussed ~20B L" 36 $rowTop[0] 150 $rowHeight $fontSize
        $product = Add-Box $slide 'Product demand' 'Demand by product' ("Petrol {0:0.0}B L`rDiesel {1:0.0}B L" -f $volumes.petrol.billion_litres, $volumes.diesel.billion_litres) 36 $rowTop[1] 150 $rowHeight $fontSize
        $uses = Add-Box $slide 'Sector demand' 'Demand by use' ("Road {0:0.0}B, industry {1:0.0}B`rAgri {2:0.0}B, other {3:0.0}B" -f $volumes.demand_by_use.road, $volumes.demand_by_use.industry_incl_mining, $volumes.demand_by_use.agriculture, $volumes.demand_by_use.other) 36 $rowTop[2] 150 $rowHeight $fontSize
        $demandParameters = Add-Box $slide 'Demand parameters' 'Demand parameters' "GDP and sectors`rEVs, fleet, efficiency`rFreight, prices, power" 36 $rowTop[3] 150 $rowHeight $fontSize

        $imports = Add-Box $slide 'Imports' 'Gross imports' ("Petrol {0:0.0}B L`rDiesel {1:0.0}B L" -f $volumes.imports.petrol, $volumes.imports.diesel) 210 $rowTop[0] 120 $rowHeight $fontSize
        $production = Add-Box $slide 'Production' 'Domestic production' "Refinery and synfuels`rNo data after 2021" 342 $rowTop[0] 120 $rowHeight $fontSize
        $ports = Add-Box $slide 'Ports' 'Ports' "Durban, Richards Bay`rOther gateways" 210 $rowTop[1] 120 $rowHeight $fontSize
        $inland = Add-Box $slide 'Inland' 'Inland delivery' "NMPP trunk line`rRoad and rail" 342 $rowTop[1] 120 $rowHeight $fontSize
        $coastal = Add-Box $slide 'Coastal demand' 'Coastal demand' "KZN, WC, EC`rPort-adjacent markets" 210 $rowTop[2] 120 $rowHeight $fontSize
        $inlandDemand = Add-Box $slide 'Inland demand' 'Inland demand' "Gauteng and interior`rSix inland provinces" 342 $rowTop[2] 120 $rowHeight $fontSize
        $supplyParameters = Add-Box $slide 'Supply and route parameters' 'Supply and route parameters' "Refinery closures, restarts, gas`rDelivered cost, routes, contracts`rPort, pipeline, rail capacity" 210 $rowTop[3] 252 $rowHeight $fontSize

        $sites = $volumes.site_markets
        $marketSizing = Add-Box $slide 'Market sizing' 'Market sizing' ("Coastal {0:0.0}B L, inland-bound {1:0.0}B L`rShared flows counted once" -f $sites.durban_coastal, $sites.inland_bound) 486 $rowTop[0] 225 $rowHeight $fontSize
        $durban = Add-Box $slide 'Durban opportunity' 'Durban market' ("Coastal {0:0.0}B L`rAll landed {1:0.0}B L" -f $sites.durban_coastal, $sites.durban_landed) 486 $rowTop[1] 108 $rowHeight $fontSize
        $lesedi = Add-Box $slide 'Lesedi opportunity' 'Lesedi market' ("Gauteng {0:0.0}B L`rVia Durban {1:0.0}B L" -f $sites.lesedi_gauteng, $sites.inland_bound) 603 $rowTop[1] 108 $rowHeight $fontSize
        $share = Add-Box $slide 'Share' 'Market share' ("Tanks allow at 2 turns a month:`rDurban {0:0.0}B L, Lesedi {1:0.0}B L" -f $sites.durban_tanks_allow, $sites.lesedi_tanks_allow) 486 $rowTop[2] 225 $rowHeight $fontSize
        $headroom = Add-Box $slide 'Headroom' 'Headroom' "Site market less current capture`rShared Durban-Lesedi flows once" 486 $rowTop[3] 225 $rowHeight $fontSize

        $capture = Add-Box $slide 'Additional capture' 'Additional capture' "Customers, contracts`rCompetition" 735 $rowTop[0] 140 $rowHeight $fontSize
        $capacity = Add-Box $slide 'Existing capacity' 'Existing assets' "Tanks and turns`rReceipt and dispatch" 735 $rowTop[1] 140 $rowHeight $fontSize
        $economics = Add-Box $slide 'Investment economics' 'New investment' "Volume, capex, returns`rAlternatives, downside" 735 $rowTop[2] 140 $rowHeight $fontSize
        $resolution = Add-Box $slide 'Resolution' 'Resolution' "Vopak share by site`rScope for investment" 735 $rowTop[3] 140 $rowHeight $fontSize

        foreach ($box in @($national,$product,$uses,$demandParameters,$imports,$production,$ports,$inland,$coastal,$inlandDemand,$supplyParameters,$marketSizing,$durban,$lesedi,$share,$headroom,$capture,$capacity,$economics,$resolution)) {
            $box.Fill.Visible = -1
            $box.Fill.ForeColor.RGB = 16777215
        }

        # Volume tags: the ~20B is traced through sources and destinations; everything else names the pending request.
        [void](Add-Tag $slide $national (Format-Volume $volumes.consumption 'observed'))
        [void](Add-Tag $slide $product ($volumes.petrol.year + ' · observed'))
        [void](Add-Tag $slide $uses (Format-Volume $volumes.demand_by_use 'balance'))
        [void](Add-Tag $slide $imports (Format-Volume $volumes.imports 'customs'))
        [void](Add-Tag $slide $production (Format-Volume $volumes.production 'latest'))
        [void](Add-Tag $slide $ports ('{0} · Durban {1:0.0}B L' -f $volumes.entry_points.year, $volumes.entry_points.durban))
        [void](Add-Tag $slide $inland 'Capacity ~7.7B L/yr')
        [void](Add-Tag $slide $coastal (Format-Volume $volumes.coastal_demand 'proxy'))
        [void](Add-Tag $slide $inlandDemand (Format-Volume $volumes.inland_demand 'proxy'))
        [void](Add-Tag $slide $marketSizing ('{0} · {1:0.0}B L · estimate' -f $sites.year, $sites.combined))
        [void](Add-Tag $slide $durban ('{0:0.0} to {1:0.0}B L' -f $sites.durban_coastal, $sites.durban_landed))
        [void](Add-Tag $slide $lesedi ('{0:0.0} to {1:0.0}B L' -f $sites.lesedi_gauteng, $sites.lesedi_inland))
        [void](Add-Tag $slide $share 'Ceiling, not share · DR02/05')
        [void](Add-Tag $slide $headroom 'Pending · DR02/05')
        [void](Add-Tag $slide $capture 'Pending · DR02/05')
        [void](Add-Tag $slide $capacity 'Pending · DR03')
        [void](Add-Tag $slide $economics 'Pending · DR06')

        # Deep-dive markers point to the logistics page; the legend explains them.
        foreach ($balanceBox in @($national,$imports,$production)) { [void](Add-Marker $slide $balanceBox 'p.1') }
        [void](Add-Marker $slide $product 'p.3')
        [void](Add-Marker $slide $uses 'p.4')
        [void](Add-Marker $slide $demandParameters 'p.5')
        foreach ($routeBox in @($ports,$inland)) { [void](Add-Marker $slide $routeBox 'p.6') }
        $slide.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text = '2'
        $legendMarker = Add-Marker $slide $null 'p.#' 747 96
        [void](Add-Text $slide 'Deep dive legend' 'Deep dive on that page' 779 95.5 96 12 9 $false 1)
        [void](Add-Link $slide 'Product sums to consumption' $product 1 $national 3)
        [void](Add-Link $slide 'Uses determine product demand' $uses 1 $product 3)
        [void](Add-Link $slide 'Demand parameter effect' $demandParameters 1 $uses 3 $false $true)
        [void](Add-Link $slide 'Demand sets import requirement' $national 4 $imports 2)
        [void](Add-Link $slide 'Imports land at ports' $imports 3 $ports 1)
        [void](Add-Link $slide 'Domestic output moves inland' $production 3 $inland 1)
        [void](Add-Link $slide 'Ports to inland delivery' $ports 4 $inland 2)
        [void](Add-Link $slide 'Ports serve coastal demand' $ports 3 $coastal 1)
        [void](Add-Link $slide 'Inland delivery serves inland demand' $inland 3 $inlandDemand 1)
        [void](Add-Link $slide 'Supply parameter effect on coastal' $null 0 $coastal 3 $false $true 270 $rowTop[3])
        [void](Add-Link $slide 'Supply parameter effect on inland' $null 0 $inlandDemand 3 $false $true 402 $rowTop[3])
        [void](Add-Link $slide 'Routes into market sizing' $inland 4 $marketSizing 2 $true)
        [void](Add-Link $slide 'Destinations into market sizing' $inlandDemand 4 $marketSizing 2 $true)
        [void](Add-Link $slide 'Market sizing to Durban' $null 0 $durban 1 $false $false 540 ($rowTop[0] + $rowHeight))
        [void](Add-Link $slide 'Market sizing to Lesedi' $null 0 $lesedi 1 $false $false 657 ($rowTop[0] + $rowHeight))
        (Add-Rule $slide 'Durban into share' 540 ($rowTop[1] + $rowHeight) 540 $rowTop[2] $true).Line.EndArrowheadStyle = 2
        (Add-Rule $slide 'Lesedi into share' 657 ($rowTop[1] + $rowHeight) 657 $rowTop[2] $true).Line.EndArrowheadStyle = 2
        [void](Add-Link $slide 'Share to headroom' $share 3 $headroom 1)

        # Headroom starts the investment test, which then reads top to bottom.
        [void](Add-Link $slide 'Headroom into investment' $headroom 4 $capture 2 $true)
        [void](Add-Link $slide 'Capture to capacity' $capture 3 $capacity 1)
        [void](Add-Link $slide 'Capacity to returns' $capacity 3 $economics 1)
        [void](Add-Link $slide 'Returns to resolution' $economics 3 $resolution 1)
    }

    $sourceFooter = $slide.Shapes.Item('Unified source footer')
    $sourceFooter.TextFrame.TextRange.Text = $(if ($Layout -eq 'flow') {
        'Source: 8 Oct PS session; Manish DR01 (sales, SARS customs, energy balance to 2021) and DR04 (entry points); provincial sales 2022. Coastal = KZN, WC, EC. Production is 2021, the last published year. Destinations sum to consumption; routes overlap.'
    } else {
        'Source: 8 October PS session and marked storyboard. ~20B is provisional. Reconcile production + imports - exports - stock build with consumption. Solid: flow; dashed: parameter effect.'
    })
    $sourceFooter.TextFrame.TextRange.Font.Size = 6.7
    $slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = @'
Source: workstreams/WS0_governance/meetings/2026-10-08_ps_session_manish_ramjeawon.docx and Nigel's supplied market sizing.jpg storyboard.
This is the issue-tree framework requested after the PS session. The roughly 20 billion litres is the discussion's provisional annual petrol-plus-diesel consumption total. It is not gross imports, addressable terminal volume or verified throughput. No market shares have been calculated.
Reconcile product/year consumption against actual domestic production, gross imports, exports and stock changes. Keep statistical differences explicit. Capacity is not production.
Estimate the accessible annual market separately for Durban and Lesedi from product compatibility, destination demand, feasible routes, delivered cost and terminal access. Both imported and domestic fuel can influence each site's opportunity. Customer and contractual restrictions narrow achievable capture.
Request site/product throughput, actual working tanks, turns, occupancy, receipt and dispatch limits and customer commitments from the client. Calculate current accessible-market share and national-market share with explicit denominators. Trace common Durban-Lesedi flows so the combined opportunity is deduplicated.
Compare additional achievable capture with existing handling capability, then operational improvements and expansion alternatives. Annual throughput in litres cannot directly determine storage cubic metres. Investment requires incremental cash flows and downside tests across coherent demand and domestic-supply worlds.
Parameters have different effects: road-to-rail changes freight diesel use and delivery choices; EV turnover and ICE efficiency affect road fuel demand; Eskom recovery and IPP delivery affect power diesel demand; refinery output and closures affect the import requirement and origin of flows; infrastructure capacity and access limit routes and terminal capture.
Manish handback: close evidence gaps, consolidate the baseline and build the terminal market-size methodology with source/year/unit, observed or estimated status, owner and unresolved gaps. Nigel coordinates client inputs. Nigel and Henry review scenario and capture assumptions. No commercial commitment or business approval is implied.
LAYOUT_NOTE
Template provenance: copied from the current SA_Market_Story_2026-10-08_v25.pptx, slide 14, with its supplied Vopak master and named Header only layout retained. Original preserved. All diagram content is editable native PowerPoint text and connectors.
'@ -replace 'LAYOUT_NOTE', $layoutNote
    if ($Layout -eq 'flow') {
        # Page 1: national balance, the layer above the issue tree. One row per year; the identity reads left to right.
        $balanceCopy = $slide.Duplicate()
        $balanceSlide = $balanceCopy.Item(1)
        $balanceSlide.MoveTo(1 + $coverOffset)
        $keepNames = @('Title 1','Slide Number Placeholder','Unified source footer','Strictly Confidential footer','SCR 1','SCR 2','SCR 3','SCR 4')
        for ($shapeIndex = $balanceSlide.Shapes.Count; $shapeIndex -ge 1; $shapeIndex--) {
            if ($balanceSlide.Shapes.Item($shapeIndex).Name -notin $keepNames) { $balanceSlide.Shapes.Item($shapeIndex).Delete() }
        }
        $balanceSlide.Shapes.Title.TextFrame.TextRange.Text = 'National petrol and diesel balance: what makes up the ~20B litres'
        $balanceSlide.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text = '1'
        $balanceRows = (Get-Content -Raw -LiteralPath (Join-Path $repoRoot 'pptx/story/issue_tree_volumes_2026_10_08.json') | ConvertFrom-Json).balance

        foreach ($panel in @(@('Balance panel',114,262),@('Findings panel',384,104))) {
            $panelShape = $balanceSlide.Shapes.AddShape(1,[single]28,[single]$panel[1],[single]855,[single]$panel[2])
            $panelShape.Name = $panel[0]
            $panelShape.Line.Visible = 0
            $panelShape.Shadow.Visible = 0
            $panelShape.Fill.ForeColor.RGB = 16183790
        }
        $termLeft = @(121,276,431,586,741); $termWidth = 130
        $terms = @(
            @('production','Domestic production'),
            @('imports','Gross imports'),
            @('exports','Exports'),
            @('sales','Sales'),
            @('supply_less_sales','Supply less sales')
        )
        $operators = @('+','−','−','=')
        [void](Add-Text $balanceSlide 'Year heading' 'Year' 36 129 70 19 12 $true 5)
        for ($term = 0; $term -lt 5; $term++) {
            [void](Add-Text $balanceSlide ('Term heading ' + $terms[$term][0]) $terms[$term][1] $termLeft[$term] 129 $termWidth 19 11 $true 5)
        }
        [void](Add-Rule $balanceSlide 'Equation heading rule' 36 151 871 151 $false $false 1)

        $rowTop = @(160,232,304); $rowHeight = 62
        for ($row = 0; $row -lt 3; $row++) {
            $balanceRow = $balanceRows[$row]
            $yearLabel = Add-Text $balanceSlide ('Year ' + $balanceRow.year) ($balanceRow.year + "`r" + $balanceRow.basis) 36 ($rowTop[$row] + 6) 78 44 14 $true 5
            $yearLabel.TextFrame.TextRange.Paragraphs(2,1).Font.Size = 9
            $yearLabel.TextFrame.TextRange.Paragraphs(2,1).Font.Bold = 0
            $yearLabel.TextFrame.TextRange.Paragraphs(2,1).Font.Color.ObjectThemeColor = 1
            for ($term = 0; $term -lt 5; $term++) {
                $item = $balanceRow.($terms[$term][0])
                $known = $null -ne $item.value
                $signed = $terms[$term][0] -eq 'supply_less_sales'
                $valueText = $(if ($known) { ('{0}{1:0.0}B L' -f $(if ($item.value -lt 0) { '−' } elseif ($signed -and $item.value -gt 0) { '+' } else { '' }), [math]::Abs($item.value)) } elseif ($signed) { 'Cannot close' } else { 'Not published' })
                $detail = $(if ($item.split) { 'Petrol {0:0.0} · diesel {1:0.0}' -f $item.split.petrol, $item.split.diesel } elseif ($signed) { 'Needs production' } else { 'No balance after 2021' })
                $cell = Add-Box $balanceSlide ('Balance ' + $balanceRow.year + ' ' + $terms[$term][0]) $valueText $detail $termLeft[$term] $rowTop[$row] $termWidth $rowHeight 9.5
                $cell.Fill.Visible = -1
                $cell.Fill.ForeColor.RGB = 16777215
                $cell.TextFrame.TextRange.Paragraphs(1,1).Font.Size = 15
                if (-not $known) { $cell.TextFrame.TextRange.Paragraphs(1,1).Font.Color.RGB = 8421504 }
                $tagCopy = $(switch ($item.status) {
                    'not published' { 'Pending · DR08 operators' }
                    'cannot close' { 'Pending · production, stocks' }
                    'calculated' { 'Stocks + stat. difference' }
                    default { $item.status + ' · DR01' }
                })
                [void](Add-Tag $balanceSlide $cell $tagCopy)
                if ($term -lt 4) {
                    $operator = Add-Text $balanceSlide ('Operator ' + $balanceRow.year + ' ' + $term) $operators[$term] ($termLeft[$term] + $termWidth) ($rowTop[$row] + 20) 25 22 16 $true 5
                    $operator.TextFrame.TextRange.ParagraphFormat.Alignment = 2
                }
            }
        }

        # Findings read straight off DR01; nothing is implied after 2021.
        $closure = (Get-Content -Raw -LiteralPath (Join-Path $repoRoot 'pptx/story/issue_tree_volumes_2026_10_08.json') | ConvertFrom-Json).closure
        $findings = @(
            @('Production fell as imports rose', ("Production {0:0.0}B L ({1}) to {2:0.0}B L ({3})`rImports {4:0.0}B L ({1}) to {5:0.0}B L ({6})" -f $balanceRows[0].production.value, $balanceRows[0].year, $balanceRows[1].production.value, $balanceRows[1].year, $balanceRows[0].imports.value, $balanceRows[2].imports.value, $balanceRows[2].year), 'DR01 · energy balance, customs'),
            @('The balance closed to 2021', ("Supply within {0:0.0}B L of sales, {1}-{2}`rException: {3} {4}, +{5:0.0}B L" -f $closure.within, $closure.from, $closure.to, $closure.exception.product, $closure.exception.year, $closure.exception.value), 'DR01 · calculated'),
            @('It cannot close after 2021', "No production published after 2021`rStock change never published", 'Pending · DR08 operators, DR01 stocks')
        )
        for ($finding = 0; $finding -lt 3; $finding++) {
            $findingBox = Add-Box $balanceSlide ('Finding ' + ($finding + 1)) $findings[$finding][0] $findings[$finding][1] (36 + 285 * $finding) 394 269 84 10.5
            $findingBox.Fill.Visible = -1
            $findingBox.Fill.ForeColor.RGB = 16777215
            [void](Add-Tag $balanceSlide $findingBox $findings[$finding][2])
        }
        $balanceFooter = $balanceSlide.Shapes.Item('Unified source footer')
        $balanceFooter.TextFrame.TextRange.Text = 'Source: Manish DR01 (8 Oct): department energy balance (production to 2021), SARS customs (trade), department sales. Supply less sales = stock change + statistical difference, not production. FIASA and JODI not used. Petrol and diesel only.'
        $balanceFooter.TextFrame.TextRange.Font.Size = 6.7
        $balanceSlide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = 'National balance above the issue tree: production + imports - exports - sales = supply less sales, where supply less sales is the stock change and statistical difference together. All figures are Manish''s DR01 balance file (workstreams/WS1_data_validation/fuel_balance_petrol_diesel_2009_2025_2026-10-06.csv): production from the department energy balances (none after 2021), trade from SARS customs, sales from the department. No residual is labelled as production. v9 showed implied production for 2023-24, energy-balance trade for 2021 and FIASA sales for 2024; all three are withdrawn (overlap log, items 1-3). The 2021 energy balance uses higher imports than customs (diesel 11.2 against 9.8B L), unexplained and open with Manish. The PS session figure of about 20B L has no department source after 2023; FIASA and JODI are excluded by instruction.'
    }

    if ($Layout -eq 'flow') {
        # Pages 3-5: demand deep dives, in issue-tree order. Figures come from the volumes file.
        $deep = Get-Content -Raw -LiteralPath (Join-Path $repoRoot 'pptx/story/issue_tree_volumes_2026_10_08.json') | ConvertFrom-Json
        $newPage = {
            param($title, $offset)
            $copy = $slide.Duplicate()
            $page = $copy.Item(1)
            $page.MoveTo($slide.SlideIndex + $offset)
            $keep = @('Title 1','Slide Number Placeholder','Unified source footer','Strictly Confidential footer','SCR 1','SCR 2','SCR 3','SCR 4')
            for ($shapeIndex = $page.Shapes.Count; $shapeIndex -ge 1; $shapeIndex--) {
                if ($page.Shapes.Item($shapeIndex).Name -notin $keep) { $page.Shapes.Item($shapeIndex).Delete() }
            }
            $page.Shapes.Title.TextFrame.TextRange.Text = $title
            $page.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text = [string]$page.SlideIndex
            return $page
        }
        $addPanel = {
            param($page, $name, $x, $w, $heading)
            $panelShape = $page.Shapes.AddShape(1,[single]($x - 8),[single]122,[single]($w + 16),[single]362)
            $panelShape.Name = $name
            $panelShape.Line.Visible = 0
            $panelShape.Shadow.Visible = 0
            $panelShape.Fill.ForeColor.RGB = 16183790
            [void](Add-Text $page ($name + ' heading') $heading $x 129 $w 19 12 $true 5)
            [void](Add-Rule $page 'Column heading rule' $x 151 ($x + $w) 151 $false $false 1)
        }
        $addCard = {
            param($page, $name, $heading, $copy, $x, $y, $w, $h, $tag, $headingSize = 0, $muted = $false)
            $card = Add-Box $page $name $heading $copy $x $y $w $h 10.5
            $card.Fill.Visible = -1
            $card.Fill.ForeColor.RGB = 16777215
            if ($headingSize -gt 0) { $card.TextFrame.TextRange.Paragraphs(1,1).Font.Size = $headingSize }
            if ($muted) { $card.TextFrame.TextRange.Paragraphs(1,1).Font.Color.RGB = 8421504 }
            if ($tag) { [void](Add-Tag $page $card $tag) }
            return $card
        }
        $setFooter = {
            param($page, $text, $notes)
            $footer = $page.Shapes.Item('Unified source footer')
            $footer.TextFrame.TextRange.Text = $text
            $footer.TextFrame.TextRange.Font.Size = 6.7
            $page.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = $notes
        }
        $cardTop = @(160,272,384); $cardHeight = 96

        # Page 3: demand by product and province.
        $provinces = $deep.provinces
        $provincePage = & $newPage 'Demand by product and province: where the litres are sold' 1
        $coastalRows = @($provinces.rows | Where-Object { $_.coastal })
        $inlandRows = @($provinces.rows | Where-Object { -not $_.coastal })
        $coastalTotal = $provinces.coastal_total
        $inlandTotal = $provinces.inland_total
        & $addPanel $provincePage 'Coastal panel' 36 191 ('1  COASTAL · {0:0.0}B L' -f $coastalTotal)
        & $addPanel $provincePage 'Inland panel' 252 407 ('2  INLAND · {0:0.0}B L' -f $inlandTotal)
        & $addPanel $provincePage 'Meaning panel' 684 191 '3  WHAT IT MEANS'
        $provinceCard = {
            param($row, $x, $y, $w)
            $copy = "Petrol {0:0.0} · diesel {1:0.0}B L`rSince {2}: {3}{4}%" -f $row.petrol, $row.diesel, $provinces.first_year, $(if ($row.change_pct -gt 0) { '+' } else { '' }), $row.change_pct
            [void](& $addCard $provincePage ('Province ' + $row.code) ('{0} · {1}%' -f $row.name, $row.share_pct) $copy $x $y $w $cardHeight ('{0} · {1:0.0}B L · {2}' -f $provinces.year, $row.total, $provinces.status))
        }
        for ($i = 0; $i -lt $coastalRows.Count; $i++) { & $provinceCard $coastalRows[$i] 36 $cardTop[$i] 191 }
        for ($i = 0; $i -lt $inlandRows.Count; $i++) { & $provinceCard $inlandRows[$i] (252 + 215.5 * ($i % 2)) $cardTop[[math]::Floor($i / 2)] 191.5 }
        $largest = $provinces.rows | Sort-Object total -Descending | Select-Object -First 1
        $kzn = $provinces.rows | Where-Object { $_.code -eq 'KZN' }
        $wc = $provinces.rows | Where-Object { $_.code -eq 'WC' }
        $petrolFellEverywhere = $provinces.petrol_fell_in -eq $provinces.province_count
        [void](& $addCard $provincePage 'Province finding 1' ('{0} anchors inland' -f $largest.name) ("{0:0.0}B L, {1}% of the national total`rLesedi's catchment" -f $largest.total, $largest.share_pct) 684 $cardTop[0] 191 $cardHeight ($provinces.year + ' · observed · DR01'))
        [void](& $addCard $provincePage 'Province finding 2' 'Diesel grew on the coast' ("KZN {0:0.0} to {1:0.0}, WC {2:0.0} to {3:0.0}B L`r{4}" -f $kzn.diesel_2013, $kzn.diesel, $wc.diesel_2013, $wc.diesel, $(if ($petrolFellEverywhere) { 'Petrol fell in every province' } else { 'Petrol fell in most provinces' })) 684 $cardTop[1] 191 $cardHeight ($provinces.first_year + '-' + $provinces.year + ' · observed'))
        [void](& $addCard $provincePage 'Province finding 3' ('{0} is estimated' -f $provinces.estimate_year) ("First-quarter shares of the total`rError {0} pts petrol, {1} diesel" -f $provinces.estimate_error_points.petrol, $provinces.estimate_error_points.diesel) 684 $cardTop[2] 191 $cardHeight 'Back-test · DR01')
        & $setFooter $provincePage 'Source: Manish DR01 provincial file: department sales by magisterial district summed to province, 2013-2022 observed; 2023 estimated from first-quarter shares. Coastal = KZN, WC, EC (presentation grouping, not registered). Petrol and diesel.' ('Deep dive for Demand by product on the issue tree. Provincial petrol and diesel sales from workstreams/WS1_data_validation/provincial_petrol_diesel_2013_2024_2026-10-06.csv (Manish, DR01). 2022 is the last fully observed year; 2023 splits the national total by first-quarter 2023 shares, back-tested at ' + $provinces.estimate_error_points.petrol + ' share points for petrol and ' + $provinces.estimate_error_points.diesel + ' for diesel. Gauteng maps to Lesedi''s catchment and KZN to Durban''s coastal catchment; the pipeline also carries Durban imports inland, so catchment is not the same as site market. The coastal grouping is a presentation choice and needs a register row before any model use.')

        # Page 4: demand by use, every source side by side for calibration (overlap log item 6).
        $use = $deep.sector_use
        $usePage = & $newPage 'Demand by use: three sources to calibrate' 2
        $sectorLeft = @(121,276,431,586,741); $sectorWidth = 130
        $panelShape = $usePage.Shapes.AddShape(1,[single]28,[single]114,[single]855,[single]262)
        $panelShape.Name = 'Sources panel'; $panelShape.Line.Visible = 0; $panelShape.Shadow.Visible = 0; $panelShape.Fill.ForeColor.RGB = 16183790
        $panelShape = $usePage.Shapes.AddShape(1,[single]28,[single]384,[single]855,[single]104)
        $panelShape.Name = 'Calibration panel'; $panelShape.Line.Visible = 0; $panelShape.Shadow.Visible = 0; $panelShape.Fill.ForeColor.RGB = 16183790
        [void](Add-Text $usePage 'Source heading' 'Source' 36 129 70 19 12 $true 5)
        for ($sector = 0; $sector -lt 5; $sector++) {
            [void](Add-Text $usePage ('Sector heading ' + $sector) $use.sectors[$sector].label $sectorLeft[$sector] 129 $sectorWidth 19 11 $true 5)
        }
        [void](Add-Rule $usePage 'Sector heading rule' 36 151 871 151 $false $false 1)
        $sourceRows = @(
            @('balance', ('Energy balance' + "`r" + $use.balance_year + ', final use'), ($use.balance_year + ' · energy balance')),
            @('model', ('Model baseline' + "`r" + $use.model_year + ', high demand'), ($use.model_year + ' · model, sourced')),
            @('reported', ('Reported' + "`r" + 'separately'), 'DR07 · Eskom + IPP est.')
        )
        $useTop = @(160,232,304)
        for ($row = 0; $row -lt 3; $row++) {
            $label = Add-Text $usePage ('Source ' + $sourceRows[$row][0]) $sourceRows[$row][1] 36 ($useTop[$row] + 6) 78 44 12 $true 5
            $label.TextFrame.TextRange.Paragraphs(2,1).Font.Size = 9
            $label.TextFrame.TextRange.Paragraphs(2,1).Font.Bold = 0
            $label.TextFrame.TextRange.Paragraphs(2,1).Font.Color.ObjectThemeColor = 1
            for ($sector = 0; $sector -lt 5; $sector++) {
                $item = $use.sectors[$sector]
                $value = $item.($sourceRows[$row][0])
                if ($sourceRows[$row][0] -eq 'reported' -and $null -ne $value) {
                    $valueText = '{0:0.0}B L' -f $value.'2024'
                    $detail = 'FY23 {0:0.0} · FY25 {1:0.0}' -f $value.'2023', $value.'2025'
                    $tag = 'FY24 peak · DR07'
                } elseif ($null -ne $value) {
                    $valueText = '{0:0.0}B L' -f $value
                    $detail = $(if ($item.note -and $sourceRows[$row][0] -eq 'balance') { 'Incl. ' + $item.note.Replace(' of balance','') } elseif ($sourceRows[$row][0] -eq 'model' -and $item.key -eq 'other') { 'Marine diesel only' } else { $(if ($sourceRows[$row][0] -eq 'balance') { 'Petrol and diesel' } elseif ($item.key -eq 'road') { 'Petrol and diesel' } else { 'Diesel' }) })
                    $tag = $sourceRows[$row][2]
                } else {
                    $valueText = $(if ($item.key -eq 'power' -and $sourceRows[$row][0] -eq 'balance') { 'Not in final use' } else { 'No separate series' })
                    $detail = $(if ($item.key -eq 'power') { 'Transformation input' } else { 'Inside sales totals' })
                    $tag = 'Pending · none published'
                }
                [void](& $addCard $usePage ('Use ' + $sourceRows[$row][0] + ' ' + $item.key) $valueText $detail $sectorLeft[$sector] $useTop[$row] $sectorWidth 62 $tag $(if ($null -ne $value) { 15 } else { 11 }) ($null -eq $value))
            }
        }
        $power = $use.sectors | Where-Object { $_.key -eq 'power' }
        $other = $use.sectors | Where-Object { $_.key -eq 'other' }
        $useFindings = @(
            @('Totals agree, the mix does not', ("Balance {0:0.0}B L ({1}), model {2:0.0}B L ({3})`rsplit across sectors differently" -f $use.balance_total, $use.balance_year, $use.model_total, $use.model_year), 'To calibrate'),
            @('Power is the largest gap', ("Model {0:0.0}B L against {1:0.0}-{2:0.0}B L reported`rEskom plus independents, FY23-FY25" -f $power.model, $power.reported.'2025', $power.reported.'2024'), 'DR07 · to calibrate'),
            @('"Other" is large in the balance', ("{0:0.0}B L, mostly commercial and public`rThe model has no matching segment" -f $other.balance), 'To calibrate')
        )
        for ($finding = 0; $finding -lt 3; $finding++) {
            [void](& $addCard $usePage ('Use finding ' + ($finding + 1)) $useFindings[$finding][0] $useFindings[$finding][1] (36 + 285 * $finding) 394 269 84 $useFindings[$finding][2])
        }
        & $setFooter $usePage 'Source: department energy balance 2021 (petrol and diesel final consumption); Manish sector baselines (model, high demand, 2024; road petrol and diesel, other sectors diesel); DR07 (Eskom reported litres; independents estimated at 0.31 L/kWh). Not reconciled: overlap log item 6.' 'Deep dive for Demand by use. Three sources are shown side by side for calibration with Manish; none is adopted here. The balance is 2021 final consumption, petrol and diesel; the model baseline is the engine''s 2024 high-demand segments with Manish''s sourced starting values (agriculture 1.06 and industry 1.50 diesel, both provisional); reported power is Eskom''s turbine fuel plus independent plants estimated from generation at 0.31 litres per kWh (DR07). Power diesel is not final consumption in the balance. The model''s generation segment is well above reported burn in every recent year, and the balance''s commercial and public line has no model counterpart. Calibration decision owners: Nigel and Manish.'

        # Page 5: demand parameters, Manish's 2035 cases for the demand levers.
        $levers = $deep.levers
        $leverPage = & $newPage 'Demand parameters: the levers and their 2035 cases' 3
        $unitText = @{ 'percent_per_year' = '% a year'; 'index_2024_100' = ' (2024 = 100)'; 'index_FY2024_100' = ' (FY24 = 100)'; 'percent' = '%'; 'million_per_year' = 'm a year'; 'bn_litres_per_year' = 'B L a year' }
        $leverLeft = @(36,252,468,684)
        for ($group = 0; $group -lt 4; $group++) {
            $leverGroup = $levers.groups[$group]
            & $addPanel $leverPage ('Lever panel ' + $group) $leverLeft[$group] 191 ('{0}  {1}' -f ($group + 1), $leverGroup.group.ToUpper())
            for ($i = 0; $i -lt $leverGroup.levers.Count; $i++) {
                $lever = $leverGroup.levers[$i]
                # Numeric baselines carry their unit; text baselines ('not measured') stand alone.
                $fuelLines = foreach ($fuelLever in $lever.fuels) {
                    $unit = $unitText[$fuelLever.unit]
                    [pscustomobject]@{
                        Fuel = (Get-Culture).TextInfo.ToTitleCase($fuelLever.fuel)
                        Baseline = $(if ($fuelLever.baseline -match '^[\d.]+( to [\d.]+)?$') { $fuelLever.baseline + $unit } else { $fuelLever.baseline })
                        Unit = $unit
                        Cases = $fuelLever.cases_2035 -join ' / '
                        Changed = [int]$fuelLever.changed
                        Added = -not ($fuelLever.proposed_2035 -join '')
                    }
                }
                $fuelLines = @($fuelLines)
                if ($fuelLines.Count -eq 1) {
                    $copy = "Baseline: {0}`r{1}: {2}" -f $fuelLines[0].Baseline, $levers.period, $fuelLines[0].Cases
                } elseif (@($fuelLines.Baseline | Select-Object -Unique).Count -eq 1) {
                    # Same baseline for both fuels: state it once, then each fuel's cases.
                    $copy = (@('Baseline: ' + $fuelLines[0].Baseline) + @($fuelLines | ForEach-Object { '{0} {1}: {2}' -f $_.Fuel, $levers.period, $_.Cases })) -join "`r"
                } else {
                    $copy = (@('{0} cases, {1}:' -f $levers.period, $fuelLines[0].Unit.Trim()) + @($fuelLines | ForEach-Object { '{0} {1}' -f $_.Fuel, $_.Cases })) -join "`r"
                }
                $changedTotal = ($fuelLines | Measure-Object -Property Changed -Sum).Sum
                $origin = $(if (-not ($fuelLines | Where-Object { -not $_.Added })) { 'Added by Manish' } elseif ($changedTotal -gt 0) { 'Manish revised {0} of {1}' -f $changedTotal, (3 * $fuelLines.Count) } else { 'Nigel proposal kept' })
                [void](& $addCard $leverPage ('Lever ' + $group + ' ' + $i) $lever.label $copy $leverLeft[$group] $cardTop[$i] 191 $cardHeight ($origin + ' · not accepted'))
            }
        }
        [void](& $addCard $leverPage 'Lever 3 reported' 'Reported power diesel' ("FY24 {0:0.0}B L, FY25 {1:0.0}B L`rFalling as load-shedding ended" -f $power.reported.'2024', $power.reported.'2025') 684 $cardTop[2] 191 $cardHeight 'Observed and estimated · DR07')
        & $setFooter $leverPage ('Source: Manish lever response (7 Oct): 2035 low / medium / high, an analyst proposal, not accepted; baselines from Stats SA, naamsa, Eskom and SARS. Levers overlap (road activity and rail; EVs and efficiency); the double-count check is open (DR07).') 'Deep dive for Demand parameters. Values are read from workstreams/WS2_model_development/fuel_lever_response_2026-10-07.csv: for each lever the baseline, and 2035 low / medium / high as proposed by Manish, with how many of Nigel''s proposed values he revised. Supply levers (plant utilisation, yields, restart capacity) belong to the supply side and are not shown. Exports to neighbours are terminal throughput, not South African demand. No lever value is an accepted input; Nigel and Henry review scenario settings. The rail and road activity levers overlap, as do EV share and new-cohort efficiency: the DR07 acceptance test (no double count) is still open.'
    }

    if ($Layout -eq 'flow') {
        # Port and logistics deep dive, placed after the issue tree. Same panel grammar; rows compare modes on a common basis.
        $logisticsCopy = $slide.Duplicate()
        $logisticsSlide = $logisticsCopy.Item(1)
        $logisticsSlide.MoveTo($slide.SlideIndex + 4)
        $keepNames = @('Title 1','Slide Number Placeholder','Unified source footer','Strictly Confidential footer','SCR 1','SCR 2','SCR 3','SCR 4')
        for ($shapeIndex = $logisticsSlide.Shapes.Count; $shapeIndex -ge 1; $shapeIndex--) {
            if ($logisticsSlide.Shapes.Item($shapeIndex).Name -notin $keepNames) { $logisticsSlide.Shapes.Item($shapeIndex).Delete() }
        }
        $evidence = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $repoRoot 'pptx/story/logistics_evidence_2026_10_08.json') | ConvertFrom-Json
        $logisticsSlide.Shapes.Title.TextFrame.TextRange.Text = $evidence.title
        $logisticsSlide.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text = [string]$logisticsSlide.SlideIndex
        # Rows compare modes: network, actual throughput, capacity and use, relevance to Durban and Lesedi.
        $modeLeft = @(36,252,468,684); $modeWidth = 191; $rowTop = @(158,242,326,410); $rowHeight = 70; $fontSize = 10.5
        for ($column = 0; $column -lt 4; $column++) {
            $mode = $evidence.modes[$column]
            $panelShape = $logisticsSlide.Shapes.AddShape(1,[single]($modeLeft[$column] - 8),[single]122,[single]($modeWidth + 16),[single]362)
            $panelShape.Name = "Mode panel $($column + 1)"
            $panelShape.Line.Visible = 0
            $panelShape.Shadow.Visible = 0
            $panelShape.Fill.ForeColor.RGB = 16183790
            [void](Add-Text $logisticsSlide "Mode heading $($column + 1)" $mode.heading $modeLeft[$column] 129 $modeWidth 19 12 $true 5)
            [void](Add-Rule $logisticsSlide 'Column heading rule' $modeLeft[$column] 151 ($modeLeft[$column] + $modeWidth) 151 $false $false 1)
            for ($row = 0; $row -lt 4; $row++) {
                $cell = $mode.cells[$row]
                # {name} placeholders take registered port figures from the volumes file.
                $cellCopy = $cell.copy -join "`r"
                foreach ($property in $volumes.port_liquid_bulk.PSObject.Properties) { $cellCopy = $cellCopy.Replace('{' + $property.Name + '}', [string]$property.Value) }
                if ($cellCopy -match '\{\w+\}') { throw ('Unfilled placeholder on logistics page: ' + $cellCopy) }
                $cellBox = Add-Box $logisticsSlide "Mode $($column + 1) row $($row + 1)" $cell.title $cellCopy $modeLeft[$column] $rowTop[$row] $modeWidth $rowHeight $fontSize
                $cellBox.Fill.Visible = -1
                $cellBox.Fill.ForeColor.RGB = 16777215
                [void](Add-Tag $logisticsSlide $cellBox $cell.tag)
            }
        }
        $logisticsFooter = $logisticsSlide.Shapes.Item('Unified source footer')
        $logisticsFooter.TextFrame.TextRange.Text = $evidence.footer
        $logisticsFooter.TextFrame.TextRange.Font.Size = 6.7
        $logisticsSlide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = $evidence.note + ' Not found publicly: per-port liquid bulk after 2021, a petroleum-only port split, Durban berth capacity, Durban-to-Gauteng fuel by rail or road, and an inland supply split by mode in volumes. The 38.9 port figure is printed as million kilometres in the TNPA table; treated as million kilolitres pending confirmation. TPL volumes include crude to Natref and Natref/Secunda product in the inland network, so they are not all Durban imports. The FY26 14.3B L figure is news only and is not shown.'
    }

    if ($IncludeRequests) {
        $requestCopy = $slide.Duplicate()
        $requestSlide = $requestCopy.Item(1)
        $requestSlide.MoveTo($deck.Slides.Count)
        $preserveNames = @('Title 1','Slide Number Placeholder','Unified source footer','Strictly Confidential footer','SCR 1','SCR 2','SCR 3','SCR 4')
        for ($shapeIndex = $requestSlide.Shapes.Count; $shapeIndex -ge 1; $shapeIndex--) {
            if ($requestSlide.Shapes.Item($shapeIndex).Name -notin $preserveNames) { $requestSlide.Shapes.Item($shapeIndex).Delete() }
        }
        $requestSlide.Shapes.Title.TextFrame.TextRange.Text = 'Outstanding data for market share and investment testing'
        $requestSlide.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text = [string]$deck.Slides.Count
        [void](Add-Text $requestSlide 'Request ownership' 'Manish assembles public evidence and estimates. Nigel coordinates client requests. Nigel / Henry review scenario settings.' 36 129 839 17 11)
        $requestRows = @(
            @('DR01  National balance','Petrol/diesel sales, gross imports, exports, production and stocks, with periods and definitions reconciled.',"Manish`rNigel reviews",'Current market size'),
            @('DR04  Routes and access','Port liquid-bulk and pipeline limits, route access and matched delivered costs to the same destinations.',"Manish`rNigel reviews",'Accessible market at each terminal'),
            @('DR07  Demand evidence','Reported Eskom diesel litres; fleet by province/class; efficiency history; IPP commissioning and rail/EV assumptions.',"Manish`rNigel reviews",'Demand baseline and scenario calibration'),
            @('DR08  Refinery supply','All refineries, including PetroSA/Mossgas: output, yields, utilisation, feedstock and closure/restart dates.',"Manish`rNigel reviews",'Domestic output and import requirement'),
            @('DR02/05  Client capture','36 months of site/product receipts and dispatches, linked transfers, customer destinations and contract volumes.',"Nigel`rcoordinates",'Current share and achievable capture'),
            @('DR03  Client operations','Working and committed tanks, turns, occupancy, downtime and receipt/dispatch limits, by site and product.',"Nigel`rcoordinates",'Usable capacity and bottlenecks'),
            @('DR06  Investment inputs','Handling/storage terms, operating costs, project capex, timing, tax, working capital and hurdle rate.',"Nigel`rcoordinates",'Incremental returns and project alternatives')
        )
        if ($Layout -eq 'flow') {
            # Manish returned DR01, DR04, DR07 and DR08 on 8 October (PR #1); state what each still lacks.
            $requestRows[0][1] = 'Received 8 Oct: balance reconciled 2014-2021 (customs, sales, energy balance). Open: stock change, production after 2021, 2024-25 sales.'
            $requestRows[1][1] = 'Received 8 Oct, partial: entry points, pipeline tariff, zone costs, site access. Open: road and rail rates, pipeline volumes by product.'
            $requestRows[2][1] = 'Received 8 Oct: Eskom litres, plant dates, fleet by province, efficiency, rail. Open: double-count check; sector baseline differs (overlap log).'
            $requestRows[3][1] = 'Received 8 Oct, partial: six plants, capacity and status, Natref split. Open: Secunda and Astron output by product; output after 2021.'
        }
        $headers = @('Outstanding request',$(if ($Layout -eq 'flow') { 'Status and what remains open' } else { 'Required data / handback' }),'Coordinator','Decision supported')
        $columnWidths = @(145,402,103,189)
        $requestTableShape = $requestSlide.Shapes.AddTable(8,4,36,154,839,304)
        $requestTableShape.Name = 'Outstanding requests native table'
        $requestTable = $requestTableShape.Table
        # Transparent cells and horizontal rules match the current Vopak evidence tables.
        for ($column = 1; $column -le 4; $column++) { $requestTable.Columns.Item($column).Width = [single]$columnWidths[$column-1] }
        for ($row = 1; $row -le 8; $row++) {
            $requestTable.Rows.Item($row).Height = [single]$(if ($row -eq 1) { 24 } else { 40 })
            for ($column = 1; $column -le 4; $column++) {
                $cell = $requestTable.Cell($row,$column)
                $cellShape = $cell.Shape
                $cellShape.Fill.Visible = 0
                for ($borderIndex = 1; $borderIndex -le 6; $borderIndex++) {
                    $cell.Borders.Item($borderIndex).Visible = 0
                }
                $cell.Borders.Item(3).Visible = -1
                $cell.Borders.Item(3).ForeColor.ObjectThemeColor = 1
                $cell.Borders.Item(3).ForeColor.TintAndShade = [single]$(if ($row -eq 1) { 0.65 } else { 0.9 })
                $cell.Borders.Item(3).Weight = [single]0.4
                $cellShape.TextFrame.MarginLeft = 3; $cellShape.TextFrame.MarginRight = 9
                $cellShape.TextFrame.MarginTop = 4; $cellShape.TextFrame.MarginBottom = 3
                $cellShape.TextFrame.VerticalAnchor = 1
                $cellShape.TextFrame.TextRange.Text = $(if ($row -eq 1) { $headers[$column-1] } else { $requestRows[$row-2][$column-1] })
                $cellShape.TextFrame.TextRange.Font.Name = 'Lato'
                $cellShape.TextFrame.TextRange.Font.Size = [single]$(if ($row -eq 1) { 11.5 } else { 11 })
                $cellShape.TextFrame.TextRange.Font.Bold = $(if ($row -eq 1 -or $column -eq 1) { -1 } else { 0 })
                $cellShape.TextFrame.TextRange.Font.Color.ObjectThemeColor = $(if ($row -gt 1 -and $column -eq 1) { 5 } else { 1 })
                $cellShape.TextFrame.TextRange.ParagraphFormat.SpaceAfter = 0
            }
        }
        [void](Add-Text $requestSlide 'Separate EV request' 'DR09 remains separate: EV adjacency needs customer demand, power access and standalone economics. Nigel coordinates.' 36 467 839 15 9.5)
        $requestFooter = $requestSlide.Shapes.Item('Unified source footer')
        $requestFooter.TextFrame.TextRange.Text = $(if ($Layout -eq 'flow') {
            'Source: DR01-DR09 request register; Manish hand-back of 8 October (DR01, DR04, DR07, DR08; merged as PR #1). Register file not yet updated for receipt. Client requests DR02/05, DR03, DR06: prepared, not sent.'
        } else {
            'Source: DR01-DR09 request register and 8 October PS session. Register status: prepared, not sent; receipt not recorded. Public estimates can proceed while client inputs are pending.'
        })
        $requestFooter.TextFrame.TextRange.Font.Size = 6.7
        $requestRegister = Import-Csv -LiteralPath (Join-Path $repoRoot 'output/delivered/investment_bridge_2026_10_08/data_request.csv')
        $requestSlide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = @'
This page groups the outstanding requests in the existing DR01-DR09 register and adds the explicit evidence gaps raised in the 8 October PS session. It is a request summary, not evidence that requests were sent or data received. No new delivery dates are committed.
Manish: assemble public evidence, retain original source files, consolidate observed versus estimated data, and estimate accessible terminal markets while client inputs are pending. Nigel coordinates commercial requests and reviews the baseline. Henry's review concerns scenario settings and specialist power assumptions.
DR01: compatible product/year definitions, actual output and explicit stock changes/statistical differences. Resolve the 2024 sales source and blank 2025 national sales rather than manufacturing observations.
DR04: public port liquid-bulk capacity and pipeline/road/rail connections; confirm working service capacity, actual access rights and destination-matched route economics with operators. Geographic connectivity alone does not establish customer access.
DR07: reported historical Eskom litres rather than generation-based estimates, vehicle composition by province/class, historical petrol/diesel efficiency, and the source paper behind retirement and road diesel split assumptions. Document renewable and gas commissioning dependencies, coal retirements and rail traction. Nigel/Henry review low/medium/high assumptions; scenarios must avoid double counting. Marine remains an open baseline gap; jet evidence is assembled but a separate model is not agreed in this handback.
DR08: complete refinery/synfuels inventory including PetroSA/Mossgas, Secunda, Natref, SAPREF and other national sites, with actual annual product output, feedstock and restart/closure dependencies. Capacity alone does not establish production.
DR02/05: latest 36 complete months of anonymised product/site movements, destinations, customer commitments, contestable volumes and contracts. Explicitly flag shared Durban-Lesedi flows and final deliveries. Verify market share against an explicit accessible-market denominator.
DR03: product-compatible working and unavailable/committed tankage, stock policy, observed turns, occupancy, downtime and peak receipt/dispatch limits.
DR06: storage and handling revenue terms, incremental operating costs, capex, schedule, ramp-up, tax, working capital, asset life and hurdle rate. Compare existing assets, operating improvements and expansion on incremental cash flows.
DR09 is still outstanding but is a separate EV adjacency case, not a prerequisite to the petrol/diesel terminal market-sizing bridge.
The underlying register and full acceptance tests follow:
'@ + "`r" + ($requestRegister | ConvertTo-Json -Depth 4)
    }
    if ($Layout -eq 'flow') {
        # Cover: the supplied Vopak title slide, with this pack's title, scope and status.
        $cover = $deck.Slides.Item(1)
        if ($cover.CustomLayout.Name -ne '1_Title') { throw 'Expected supplied 1_Title cover layout.' }
        $cover.Shapes.Item('TextBox 4').TextFrame.TextRange.Text = "Durban and Lesedi`rmarket sizing"
        $cover.Shapes.Item('TextBox 6').TextFrame.TextRange.Text = 'National balance, issue tree and deep dives'
        $cover.Shapes.Item('TextBox 7').TextFrame.TextRange.Text = 'South Africa petrol and diesel, Durban-Lesedi corridor'
        $cover.Shapes.Item('TextBox 8').TextFrame.TextRange.Text = '9 October 2026'
        $cover.Shapes.Item('TextBox 9').TextFrame.TextRange.Text = 'Draft for review. Lever cases are proposals, not accepted inputs; open exceptions mean outputs are provisional.'
        $cover.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = 'Cover from the supplied Vopak 1_Title layout (reference: SA_Market_Story_2026-10-08_v25.pptx, slide 1); photo credit retained. Page numbers start after the cover so the p.# deep-dive markers on the issue tree match.'

        # Closing page: decisions and next steps, each with an owner and the page it comes from.
        $closingCopy = $slide.Duplicate()
        $closingSlide = $closingCopy.Item(1)
        $closingSlide.MoveTo($deck.Slides.Count)
        $keep = @('Title 1','Slide Number Placeholder','Unified source footer','Strictly Confidential footer','SCR 1','SCR 2','SCR 3','SCR 4')
        for ($shapeIndex = $closingSlide.Shapes.Count; $shapeIndex -ge 1; $shapeIndex--) {
            if ($closingSlide.Shapes.Item($shapeIndex).Name -notin $keep) { $closingSlide.Shapes.Item($shapeIndex).Delete() }
        }
        $closingSlide.Shapes.Title.TextFrame.TextRange.Text = 'Decisions and next steps'
        $closingColumns = @(
            @('1  DECIDE', @(
                @('Demand by use baseline', "Choose or blend the three sources`rStart with the power gap", 'Nigel, Manish · p.4'),
                @('Demand lever cases', "Accept or revise the 2035 cases`rRun the double-count check", 'Nigel, Henry · p.5'),
                @('Coastal and inland split', "Adopt KZN, WC, EC as coastal`rAdd a register row", 'Nigel · p.3')
            )),
            @('2  REQUEST', @(
                @('Client data', "Send DR02/05, DR03, DR06`rSite throughput, tanks, economics", 'Nigel · p.7'),
                @('Operator data', "Secunda, Astron output by product`rStock change by product", 'Nigel · DR08, DR01'),
                @('Logistics confirmations', "Trunk-line capacity today`rDurban injection into the NMPP", 'Nigel · DR04, p.6')
            )),
            @('3  BUILD NEXT', @(
                @('Market sizing method', "Accessible demand by site`rShared Durban-Lesedi flows once", 'Manish · p.2'),
                @('Figure check', "Extend the pack figure check`rto this pack's volume files", 'Manish · overlap log'),
                @('Request register', "Record DR01, DR04, DR07, DR08`ras received on 8 October", 'Register owner')
            ))
        )
        $closingLeft = @(36,324,612); $closingWidth = 263
        for ($column = 0; $column -lt 3; $column++) {
            $panelShape = $closingSlide.Shapes.AddShape(1,[single]($closingLeft[$column] - 8),[single]122,[single]($closingWidth + 16),[single]362)
            $panelShape.Name = 'Closing panel ' + $column
            $panelShape.Line.Visible = 0
            $panelShape.Shadow.Visible = 0
            $panelShape.Fill.ForeColor.RGB = 16183790
            [void](Add-Text $closingSlide ('Closing heading ' + $column) $closingColumns[$column][0] $closingLeft[$column] 129 $closingWidth 19 12 $true 5)
            [void](Add-Rule $closingSlide 'Column heading rule' $closingLeft[$column] 151 ($closingLeft[$column] + $closingWidth) 151 $false $false 1)
            for ($row = 0; $row -lt 3; $row++) {
                $item = $closingColumns[$column][1][$row]
                $card = Add-Box $closingSlide ('Closing ' + $column + ' ' + $row) $item[0] $item[1] $closingLeft[$column] (160 + 112 * $row) $closingWidth 96 10.5
                $card.Fill.Visible = -1
                $card.Fill.ForeColor.RGB = 16777215
                [void](Add-Tag $closingSlide $card $item[2])
            }
        }
        $closingFooter = $closingSlide.Shapes.Item('Unified source footer')
        $closingFooter.TextFrame.TextRange.Text = 'Owners as proposed in the request register and the 8 October hand-back; no dates are committed. Page references are to this pack; open items are listed in workstreams/WS0_governance/workplan/overlap_log_2026_10_08.md.'
        $closingFooter.TextFrame.TextRange.Font.Size = 6.7
        $closingSlide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = 'Closing page. Decisions: the demand-by-use baseline (overlap log item 6, page 4), the demand lever cases and the open DR07 double-count test (page 5), and whether to register the coastal and inland grouping (page 3). Requests: client data DR02/05, DR03 and DR06 (prepared, not sent); operator output by product and stock change (DR08, DR01 gaps); current trunk-line capacity and whether Vopak Durban can inject into the NMPP (DR04 gaps). Build next: the Durban and Lesedi market sizing method, an independent figure check for this pack, and recording receipt of DR01, DR04, DR07 and DR08 in the register file. No delivery dates are committed.'
    }

    # Number every content page after the cover, so p.# markers match the printed page numbers.
    foreach ($numberedSlide in $deck.Slides) {
        if ($numberedSlide.SlideIndex -le $coverOffset) { continue }
        $numberedSlide.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text = [string]($numberedSlide.SlideIndex - $coverOffset)
    }

    # Validate all slide-owned objects against physical slide bounds and text boxes.
    $qa = @()
    foreach ($slide in $deck.Slides) {
    for ($shapeIndex = 1; $shapeIndex -le $slide.Shapes.Count; $shapeIndex++) {
        $shape = $slide.Shapes.Item($shapeIndex)
        if ($shape.Left -lt -0.5 -or $shape.Top -lt -0.5 -or ($shape.Left + $shape.Width) -gt ($deck.PageSetup.SlideWidth + 0.5) -or ($shape.Top + $shape.Height) -gt ($deck.PageSetup.SlideHeight + 0.5)) { throw ('Shape exceeds slide bounds: ' + $shape.Name) }
        if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
            $bound = $shape.TextFrame.TextRange.BoundHeight
            $qa += [pscustomobject]@{ name=$shape.Name; height=$shape.Height; textHeight=$bound; text=$shape.TextFrame.TextRange.Text }
            $limit = $(if ($shape.Type -eq 1) { $shape.Height - $shape.TextFrame.MarginTop - $shape.TextFrame.MarginBottom + 1 } else { $shape.Height + 2 })
            if ($bound -gt $limit) { throw ('Text exceeds shape height: ' + $shape.Name + ' ' + $bound + ' > ' + $shape.Height) }
        }
        if ($shape.HasTable) {
            for ($row = 1; $row -le $shape.Table.Rows.Count; $row++) {
                for ($column = 1; $column -le $shape.Table.Columns.Count; $column++) {
                    $cellShape = $shape.Table.Cell($row,$column).Shape
                    $cellAvailableHeight = $cellShape.Height - $cellShape.TextFrame.MarginTop - $cellShape.TextFrame.MarginBottom
                    if ($cellShape.TextFrame.TextRange.BoundHeight -gt ($cellAvailableHeight + 1)) { throw ("Request table text overflow: row $row column $column") }
                }
            }
        }
    }
    }
    $qa | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $qaDirectory 'text_fit.json') -Encoding UTF8
    $deck.SaveAs($targetPptx,24,-1)
    $deck.SaveAs($targetPdf,32)
    $deck.Export($qaDirectory,'PNG',1825,1080)
    Write-Output $targetPptx
    Write-Output $targetPdf
} catch { Write-Error ("Build failed at line " + $_.InvocationInfo.ScriptLineNumber + ": " + $_.Exception.Message) } finally { try { $deck.Close() } catch {} }
