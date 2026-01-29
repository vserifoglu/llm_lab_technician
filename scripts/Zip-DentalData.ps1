<#
.SYNOPSIS
    Analyze extracted dental case files before compression.
    
.DESCRIPTION
    Reports total size, file counts, STL format (ASCII/Binary),
    and runs a sample compression test to estimate final size.
    
.EXAMPLE
    .\Analyze-DentalData.ps1 -Path "E:\DataExport"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Path
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DENTAL DATA ANALYSIS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verify path exists
if (-not (Test-Path $Path)) {
    Write-Host "ERROR: Path does not exist: $Path" -ForegroundColor Red
    exit 1
}

# ============================================================
# FILE INVENTORY
# ============================================================

Write-Host "Scanning files..." -ForegroundColor Yellow
$allFiles = Get-ChildItem -Path $Path -Recurse -File

$stlFiles = $allFiles | Where-Object { $_.Extension -eq ".stl" }
$xmlFiles = $allFiles | Where-Object { $_.Extension -in @(".constructionInfo", ".dentalProject") }
$otherFiles = $allFiles | Where-Object { $_.Extension -notin @(".stl", ".constructionInfo", ".dentalProject") }

# ============================================================
# SIZE CALCULATIONS
# ============================================================

$totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum
$stlSize = ($stlFiles | Measure-Object -Property Length -Sum).Sum
$xmlSize = ($xmlFiles | Measure-Object -Property Length -Sum).Sum

function Format-Size($bytes) {
    if ($bytes -ge 1GB) { return "{0:N2} GB" -f ($bytes / 1GB) }
    if ($bytes -ge 1MB) { return "{0:N2} MB" -f ($bytes / 1MB) }
    if ($bytes -ge 1KB) { return "{0:N2} KB" -f ($bytes / 1KB) }
    return "$bytes bytes"
}

Write-Host ""
Write-Host "FILE INVENTORY" -ForegroundColor Green
Write-Host "-----------------------------------------"
Write-Host "Total files:        $($allFiles.Count)"
Write-Host "  STL files:        $($stlFiles.Count)  ($(Format-Size $stlSize))"
Write-Host "  XML files:        $($xmlFiles.Count)  ($(Format-Size $xmlSize))"
Write-Host "  Other files:      $($otherFiles.Count)"
Write-Host ""
Write-Host "TOTAL SIZE:         $(Format-Size $totalSize)" -ForegroundColor White
Write-Host ""

# ============================================================
# STL FORMAT DETECTION (ASCII vs Binary)
# ============================================================

Write-Host "Detecting STL formats..." -ForegroundColor Yellow

$asciiCount = 0
$binaryCount = 0
$asciiSize = 0
$binarySize = 0

# Sample up to 100 STL files for format detection
$sampleStls = $stlFiles | Select-Object -First 100

foreach ($stl in $sampleStls) {
    try {
        $firstBytes = [System.IO.File]::ReadAllBytes($stl.FullName) | Select-Object -First 80
        $header = [System.Text.Encoding]::ASCII.GetString($firstBytes)
        
        if ($header -match "^solid\s") {
            # Could be ASCII, check if it contains "facet"
            $content = Get-Content $stl.FullName -TotalCount 10 -ErrorAction SilentlyContinue
            if ($content -match "facet") {
                $asciiCount++
                $asciiSize += $stl.Length
            } else {
                $binaryCount++
                $binarySize += $stl.Length
            }
        } else {
            $binaryCount++
            $binarySize += $stl.Length
        }
    } catch {
        $binaryCount++  # Assume binary on error
        $binarySize += $stl.Length
    }
}

$asciiPercent = if ($sampleStls.Count -gt 0) { [math]::Round(($asciiCount / $sampleStls.Count) * 100, 1) } else { 0 }
$binaryPercent = if ($sampleStls.Count -gt 0) { [math]::Round(($binaryCount / $sampleStls.Count) * 100, 1) } else { 0 }

Write-Host ""
Write-Host "STL FORMAT ANALYSIS (sampled $($sampleStls.Count) files)" -ForegroundColor Green
Write-Host "-----------------------------------------"
Write-Host "  ASCII STL:   $asciiCount files ($asciiPercent%)"
Write-Host "  Binary STL:  $binaryCount files ($binaryPercent%)"
Write-Host ""

# ============================================================
# COMPRESSION ESTIMATE
# ============================================================

Write-Host "COMPRESSION ESTIMATE" -ForegroundColor Green
Write-Host "-----------------------------------------"

# Estimate based on format ratio
$estimatedAsciiSize = $stlSize * ($asciiPercent / 100)
$estimatedBinarySize = $stlSize * ($binaryPercent / 100)

# ASCII compresses ~80%, Binary ~40%
$compressedAscii = $estimatedAsciiSize * 0.20
$compressedBinary = $estimatedBinarySize * 0.60
$compressedXml = $xmlSize * 0.10  # XML compresses very well

$estimatedCompressed = $compressedAscii + $compressedBinary + $compressedXml
$compressionRatio = [math]::Round((1 - ($estimatedCompressed / $totalSize)) * 100, 1)

Write-Host "  Original size:     $(Format-Size $totalSize)"
Write-Host "  Estimated after:   $(Format-Size $estimatedCompressed)" -ForegroundColor Cyan
Write-Host "  Reduction:         ~$compressionRatio%" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# SAMPLE COMPRESSION TEST
# ============================================================

Write-Host "Running sample compression test..." -ForegroundColor Yellow

# Pick one case folder for real compression test
$sampleFolder = Get-ChildItem -Path $Path -Directory | Select-Object -First 1
$testZip = Join-Path $env:TEMP "dental_test.zip"

if ($sampleFolder) {
    try {
        # Remove old test file
        if (Test-Path $testZip) { Remove-Item $testZip -Force }
        
        # Compress sample folder
        $sampleSize = (Get-ChildItem $sampleFolder.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
        Compress-Archive -Path $sampleFolder.FullName -DestinationPath $testZip -CompressionLevel Optimal -Force
        
        $compressedSize = (Get-Item $testZip).Length
        $actualRatio = [math]::Round((1 - ($compressedSize / $sampleSize)) * 100, 1)
        
        # Extrapolate to full dataset
        $projectedTotal = $totalSize * ($compressedSize / $sampleSize)
        
        Write-Host ""
        Write-Host "SAMPLE COMPRESSION TEST" -ForegroundColor Green
        Write-Host "-----------------------------------------"
        Write-Host "  Sample folder:     $($sampleFolder.Name)"
        Write-Host "  Original:          $(Format-Size $sampleSize)"
        Write-Host "  Compressed:        $(Format-Size $compressedSize)"
        Write-Host "  Ratio:             $actualRatio% reduction"
        Write-Host ""
        Write-Host "  PROJECTED FULL DATASET:" -ForegroundColor Cyan
        Write-Host "  $(Format-Size $totalSize) → $(Format-Size $projectedTotal)" -ForegroundColor Cyan
        Write-Host ""
        
        # Cleanup
        Remove-Item $testZip -Force -ErrorAction SilentlyContinue
        
    } catch {
        Write-Host "  Could not run compression test: $_" -ForegroundColor Yellow
    }
}

# ============================================================
# RECOMMENDATIONS
# ============================================================

Write-Host "RECOMMENDATIONS" -ForegroundColor Green
Write-Host "-----------------------------------------"

if ($estimatedCompressed -lt 50GB) {
    Write-Host "  OK: Size after compression should be manageable for cloud upload" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Large file - consider splitting into multiple archives" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Compression command using 7-Zip:" -ForegroundColor White
$cmd1 = '  7z a -t7z -mx9 "DentalData.7z" "' + $Path + '"'
Write-Host $cmd1 -ForegroundColor Gray
Write-Host ""
Write-Host "  Or PowerShell - slower, less compression:" -ForegroundColor White
$cmd2 = '  Compress-Archive -Path "' + $Path + '" -DestinationPath "DentalData.zip"'
Write-Host $cmd2 -ForegroundColor Gray
Write-Host ""
