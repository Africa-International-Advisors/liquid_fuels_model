param([int]$Version = 1, [switch]$IncludeRequests)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$referencePath = Join-Path $repoRoot 'pptx/output/delivered/supporting/SA_Market_Story_2026-10-08_v25.pptx'
$outputStem = "Vopak_Market_Sizing_Issue_Tree_2026_10_08_v$Version"
$outputDirectory = Join-Path $repoRoot 'pptx/output/delivered/supporting'
$targetPptx = Join-Path $outputDirectory ($outputStem + '.pptx')
$targetPdf = Join-Path $outputDirectory ($outputStem + '.pdf')
$qaDirectory = Join-Path $repoRoot ('pptx/qa/' + $outputStem)
if ((Test-Path -LiteralPath $targetPptx) -or (Test-Path -LiteralPath $targetPdf)) { throw 'Preserve previous outputs: choose a new version.' }
[void](New-Item -ItemType Directory -Force -Path $qaDirectory)

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

$powerPoint = New-Object -ComObject PowerPoint.Application
# Open as an untitled copy. The reference, master and named layout remain preserved.
$deck = $powerPoint.Presentations.Open($referencePath,0,-1,0)
try {
    for ($slideIndex = $deck.Slides.Count; $slideIndex -ge 1; $slideIndex--) {
        if ($slideIndex -ne 14) { $deck.Slides.Item($slideIndex).Delete() }
    }
    $slide = $deck.Slides.Item(1)
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

    # Native PowerPoint diagram. All text and connectors remain editable.
    [void](Add-Text $slide 'Demand heading' '1  NATIONAL DEMAND' 36 129 174 19 12 $true 5)
    [void](Add-Text $slide 'System heading' '2  SUPPLY AND DELIVERY' 245 129 322 19 12 $true 5)
    [void](Add-Text $slide 'Terminal heading' '3  VOPAK OPPORTUNITY' 622 129 253 19 12 $true 5)
    foreach ($span in @(@(36,210),@(245,569),@(622,875))) {
        [void](Add-Rule $slide 'Column heading rule' $span[0] 151 $span[1] 151 $false $false 1)
    }

    [void](Add-Block $slide 'National market' 'National consumption' "~20B litres/year discussed`rPetrol and diesel by destination`rPS starting point, to reconcile" 36 166 174 81 12)
    [void](Add-Block $slide 'Sector demand' 'Demand by use' "Road, mining, industry, agriculture`rPower and other uses" 36 256 174 64 11.5)
    [void](Add-Rule $slide 'Uses determine demand' 120 256 120 249 $true)
    [void](Add-Block $slide 'Demand parameters' 'Demand parameters' "GDP and sector activity`rEVs, fleet turnover, ICE efficiency`rFreight shift, prices, power dispatch" 36 331 174 68 11)
    [void](Add-Rule $slide 'Demand parameter effect' 120 331 120 320 $true $true)

    [void](Add-Block $slide 'Imports' 'Gross imports' "By product and entry point`rExports shown separately" 245 166 146 67 12)
    [void](Add-Block $slide 'Production' 'Domestic production' "Refinery location, output, yields`rOwn storage and distribution" 414 166 155 67 12)
    [void](Add-Block $slide 'Routes' 'Ports and inland delivery network' "Durban, Richards Bay, other gateways`rPipeline, road and rail to customer catchments`rNMPP / TM2 / DJP links to verify" 245 255 324 69 11.5)
    [void](Add-Rule $slide 'Import route' 315 233 315 250 $true)
    [void](Add-Rule $slide 'Domestic route' 489 233 489 250 $true)
    [void](Add-Rule $slide 'Demand determines destinations 1' 210 204 224 204)
    [void](Add-Rule $slide 'Demand determines destinations 2' 224 204 224 280)
    [void](Add-Rule $slide 'Demand determines destinations 3' 224 280 241 280 $true)
    [void](Add-Block $slide 'Supply and route parameters' 'Supply and route parameters' "Refinery closures / restarts and gas availability`rDelivered cost, competing routes, access and contracts`rPort, pipeline and rail capacity and reliability" 245 331 324 68 11)
    [void](Add-Rule $slide 'Supply parameter effect' 489 331 489 323 $true $true)

    [void](Add-Block $slide 'Durban opportunity' 'Durban accessible market' "Feasible annual product volumes through`rVopak Durban to reachable customers" 622 166 253 59 12)
    [void](Add-Block $slide 'Lesedi opportunity' 'Lesedi accessible market' "Inland demand Lesedi can feasibly serve`rCatchment and receipt / dispatch connections" 622 240 253 64 12)
    [void](Add-Rule $slide 'Access screen trunk' 569 280 590 280)
    [void](Add-Rule $slide 'Access screen fork' 590 196 590 280)
    [void](Add-Rule $slide 'Access to Durban' 590 196 616 196 $true)
    [void](Add-Rule $slide 'Access to Lesedi' 590 270 616 270 $true)
    [void](Add-Block $slide 'Share and headroom' 'Capture, market share and headroom' "Client throughput / accessible market = share`rAccessible market less current capture = headroom`rTrack shared Durban-Lesedi flows once" 622 328 253 72 11)
    [void](Add-Rule $slide 'Durban into share 1' 872 225 888 225)
    [void](Add-Rule $slide 'Durban into share 2' 888 225 888 349)
    [void](Add-Rule $slide 'Durban into share 3' 888 349 879 349 $true)
    [void](Add-Rule $slide 'Lesedi into share' 747 304 747 321 $true)

    # Investment branch uses the market headroom as its starting point.
    [void](Add-Rule $slide 'Capture into investment 1' 747 400 747 408)
    [void](Add-Rule $slide 'Capture into investment 2' 747 408 120 408)
    [void](Add-Rule $slide 'Capture into investment 3' 120 408 120 420 $true)
    [void](Add-Block $slide 'Additional capture' 'Achievable additional capture' "Customers, contracts, competition`rTest capture within the opportunity" 36 427 185 45 10.5)
    [void](Add-Block $slide 'Existing capacity' 'Existing assets and improvements' "Working tanks, turns and constraints`rTest receipt, storage and dispatch" 263 427 203 45 10.5)
    [void](Add-Block $slide 'Investment economics' 'New investment and returns' "Incremental volume, cost and capex`rCompare alternatives and downside" 508 427 198 45 10.5)
    [void](Add-Block $slide 'Resolution' 'Resolution' "Vopak share at each site`rScope for new investment" 749 427 126 45 10.5)
    [void](Add-Rule $slide 'Capture to capacity' 224 446 255 446 $true)
    [void](Add-Rule $slide 'Capacity to returns' 469 446 500 446 $true)
    [void](Add-Rule $slide 'Returns to resolution' 708 446 741 446 $true)

    $sourceFooter = $slide.Shapes.Item('Unified source footer')
    $sourceFooter.TextFrame.TextRange.Text = 'Source: 8 October PS session and marked storyboard. ~20B is provisional. Reconcile production + imports - exports - stock build with consumption. Solid: flow; dashed: parameter effect.'
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
Template provenance: copied from the current SA_Market_Story_2026-10-08_v25.pptx, slide 14, with its supplied Vopak master and named Header only layout retained. Original preserved. All diagram content is editable native PowerPoint text and connectors.
'@
    if ($IncludeRequests) {
        $requestCopy = $slide.Duplicate()
        $requestSlide = $requestCopy.Item(1)
        $requestSlide.MoveTo(2)
        $preserveNames = @('Title 1','Slide Number Placeholder','Unified source footer','Strictly Confidential footer','SCR 1','SCR 2','SCR 3','SCR 4')
        for ($shapeIndex = $requestSlide.Shapes.Count; $shapeIndex -ge 1; $shapeIndex--) {
            if ($requestSlide.Shapes.Item($shapeIndex).Name -notin $preserveNames) { $requestSlide.Shapes.Item($shapeIndex).Delete() }
        }
        $requestSlide.Shapes.Title.TextFrame.TextRange.Text = 'Outstanding data for market share and investment testing'
        $requestSlide.Shapes.Item('Slide Number Placeholder').TextFrame.TextRange.Text = '2'
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
        $headers = @('Outstanding request','Required data / handback','Coordinator','Decision supported')
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
        $requestFooter.TextFrame.TextRange.Text = 'Source: DR01-DR09 request register and 8 October PS session. Register status: prepared, not sent; receipt not recorded. Public estimates can proceed while client inputs are pending.'
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
    # Validate all slide-owned objects against physical slide bounds and text boxes.
    $qa = @()
    foreach ($slide in $deck.Slides) {
    for ($shapeIndex = 1; $shapeIndex -le $slide.Shapes.Count; $shapeIndex++) {
        $shape = $slide.Shapes.Item($shapeIndex)
        if ($shape.Left -lt -0.5 -or $shape.Top -lt -0.5 -or ($shape.Left + $shape.Width) -gt ($deck.PageSetup.SlideWidth + 0.5) -or ($shape.Top + $shape.Height) -gt ($deck.PageSetup.SlideHeight + 0.5)) { throw ('Shape exceeds slide bounds: ' + $shape.Name) }
        if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
            $bound = $shape.TextFrame.TextRange.BoundHeight
            $qa += [pscustomobject]@{ name=$shape.Name; height=$shape.Height; textHeight=$bound; text=$shape.TextFrame.TextRange.Text }
            if ($bound -gt ($shape.Height + 2)) { throw ('Text exceeds shape height: ' + $shape.Name + ' ' + $bound + ' > ' + $shape.Height) }
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
} finally { $deck.Close() }
