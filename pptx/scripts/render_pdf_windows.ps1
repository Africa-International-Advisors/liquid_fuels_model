param([Parameter(Mandatory=$true)][string]$SourcePath,[Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference='Stop'
# Run with Windows PowerShell 5.1; Windows' built-in PDF renderer provides independent export QA.
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
[void][Windows.Data.Pdf.PdfDocument,Windows.Data.Pdf,ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.InMemoryRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$operationMethod=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {$_.Name -eq 'AsTask' -and $_.IsGenericMethodDefinition -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'} | Select-Object -First 1
$actionMethod=[System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {$_.Name -eq 'AsTask' -and -not $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction'} | Select-Object -First 1
function Await($operation,$type){$task=$operationMethod.MakeGenericMethod($type).Invoke($null,@($operation));$task.Wait();return $task.Result}
$sourceFile=Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path -LiteralPath $SourcePath).Path)) ([Windows.Storage.StorageFile])
$document=Await ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($sourceFile)) ([Windows.Data.Pdf.PdfDocument])
[void](New-Item -ItemType Directory -Force -Path $OutputDirectory)
for($i=0;$i -lt $document.PageCount;$i++){
    $page=$document.GetPage($i);$memory=New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
    $options=New-Object Windows.Data.Pdf.PdfPageRenderOptions;$options.DestinationWidth=1217;$options.DestinationHeight=720
    $task=$actionMethod.Invoke($null,@($page.RenderToStreamAsync($memory,$options)));$task.Wait();$memory.Seek(0)
    $read=[System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($memory)
    $destination=[System.IO.File]::Create((Join-Path $OutputDirectory ('pdf_page_'+($i+1)+'.png')))
    try{$read.CopyTo($destination)}finally{$destination.Dispose();$read.Dispose();$page.Dispose()}
}
Write-Output "Rendered $($document.PageCount) PDF pages."
