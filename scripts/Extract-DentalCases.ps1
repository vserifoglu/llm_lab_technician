<#
.SYNOPSIS
    Safe extraction of dental case files for ML training.
    
.DESCRIPTION
    This script ONLY READS from the source folder - never modifies or deletes.
    It copies specific files (STL, XML) from each case to a destination folder.
    
.NOTES
    - Read-only operation on source
    - Progress tracking with ETA
    - Full error logging
    - Resumable (skips already copied files)
    
.EXAMPLE
    .\Extract-DentalCases.ps1 -Source "D:\ExocadCases" -Destination "E:\DataExport"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Source,
    
    [Parameter(Mandatory=$true)]
    [string]$Destination,
    
    [switch]$Force,  # Overwrite existing files
    [switch]$DryRun  # Preview only, don't copy
)

# ============================================================
# CONFIGURATION
# ============================================================

# File SUFFIXES - will be matched as: {case_name}{suffix}
$FileSuffixes = @(
    "-LowerJaw.stl",
    "-UpperJaw.stl",
    ".constructionInfo",
    ".dentalProject"
)

$LogFile = Join-Path $Destination "extraction_log.txt"
$ErrorLogFile = Join-Path $Destination "extraction_errors.txt"

# ============================================================
# SAFETY CHECKS
# ============================================================

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    if ($Level -eq "ERROR") {
        Write-Host $logEntry -ForegroundColor Red
        Add-Content -Path $ErrorLogFile -Value $logEntry -ErrorAction SilentlyContinue
    } elseif ($Level -eq "SUCCESS") {
        Write-Host $logEntry -ForegroundColor Green
    } elseif ($Level -eq "WARN") {
        Write-Host $logEntry -ForegroundColor Yellow
    } else {
        Write-Host $logEntry
    }
    Add-Content -Path $LogFile -Value $logEntry -ErrorAction SilentlyContinue
}

# Verify source exists and is readable
if (-not (Test-Path $Source)) {
    Write-Host "ERROR: Source folder does not exist: $Source" -ForegroundColor Red
    exit 1
}

# Check source is not the same as destination
$sourcePath = (Resolve-Path $Source).Path.TrimEnd('\')
if ($Destination.TrimEnd('\') -eq $sourcePath) {
    Write-Host "ERROR: Source and destination cannot be the same folder!" -ForegroundColor Red
    exit 1
}

# Create destination if it doesn't exist
if (-not (Test-Path $Destination)) {
    try {
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
        Write-Host "Created destination folder: $Destination" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Cannot create destination folder: $_" -ForegroundColor Red
        exit 1
    }
}

# ============================================================
# MAIN EXTRACTION LOGIC
# ============================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DENTAL CASE FILE EXTRACTOR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Source:      $Source"
Write-Host "Destination: $Destination"
Write-Host "Files:       $($FilesToCopy -join ', ')"
Write-Host "Mode:        $(if ($DryRun) {'DRY RUN (no files will be copied)'} else {'COPY'})"
Write-Host ""

# Get all case folders
$caseFolders = Get-ChildItem -Path $Source -Directory -ErrorAction Stop
$totalCases = $caseFolders.Count

if ($totalCases -eq 0) {
    Write-Host "No case folders found in source directory." -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $totalCases case folders to process." -ForegroundColor Cyan
Write-Host ""

# Initialize counters
$processedCases = 0
$copiedFiles = 0
$skippedFiles = 0
$errorCount = 0
$totalBytes = 0
$startTime = Get-Date

# Process each case
foreach ($caseFolder in $caseFolders) {
    $processedCases++
    $caseName = $caseFolder.Name
    
    # Calculate progress
    $percentComplete = [math]::Round(($processedCases / $totalCases) * 100, 1)
    $elapsed = (Get-Date) - $startTime
    $avgTimePerCase = if ($processedCases -gt 1) { $elapsed.TotalSeconds / ($processedCases - 1) } else { 0 }
    $remainingCases = $totalCases - $processedCases
    $etaSeconds = $avgTimePerCase * $remainingCases
    $eta = [TimeSpan]::FromSeconds($etaSeconds)
    
    # Display progress bar
    $progressParams = @{
        Activity = "Extracting dental cases"
        Status = "Case $processedCases of $totalCases ($percentComplete%) - $caseName"
        PercentComplete = $percentComplete
        CurrentOperation = "ETA: $($eta.ToString('hh\:mm\:ss'))"
    }
    Write-Progress @progressParams
    
    # Create destination case folder
    $destCaseFolder = Join-Path $Destination $caseName
    
    foreach ($suffix in $FileSuffixes) {
        $fileName = "$caseName$suffix"
        $srcFile = Join-Path $caseFolder.FullName $fileName
        $destFile = Join-Path $destCaseFolder $fileName
        
        try {
            # Check if source file exists
            if (-not (Test-Path $srcFile)) {
                continue  # File doesn't exist in this case, skip silently
            }
            
            # Check if already copied (resumable)
            if ((Test-Path $destFile) -and -not $Force) {
                $srcSize = (Get-Item $srcFile).Length
                $destSize = (Get-Item $destFile).Length
                
                if ($srcSize -eq $destSize) {
                    $skippedFiles++
                    continue  # Already copied, skip
                }
            }
            
            if ($DryRun) {
                Write-Log "Would copy: $caseName\$fileName" "INFO"
                $copiedFiles++
            } else {
                # Create destination folder if needed
                if (-not (Test-Path $destCaseFolder)) {
                    New-Item -ItemType Directory -Path $destCaseFolder -Force | Out-Null
                }
                
                # SAFE COPY: Read from source, write to destination
                Copy-Item -Path $srcFile -Destination $destFile -Force -ErrorAction Stop
                
                # Verify copy integrity
                $srcHash = (Get-FileHash -Path $srcFile -Algorithm MD5).Hash
                $destHash = (Get-FileHash -Path $destFile -Algorithm MD5).Hash
                
                if ($srcHash -ne $destHash) {
                    throw "Hash mismatch after copy! File may be corrupted."
                }
                
                $fileSize = (Get-Item $destFile).Length
                $totalBytes += $fileSize
                $copiedFiles++
            }
            
        } catch {
            $errorCount++
            Write-Log "Failed to copy $caseName\$fileName : $_" "ERROR"
        }
    }
}

# Complete progress bar
Write-Progress -Activity "Extracting dental cases" -Completed

# ============================================================
# SUMMARY
# ============================================================

$endTime = Get-Date
$duration = $endTime - $startTime
$totalMB = [math]::Round($totalBytes / 1MB, 2)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   EXTRACTION COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cases processed:  $processedCases"
Write-Host "Files copied:     $copiedFiles"
Write-Host "Files skipped:    $skippedFiles (already existed)"
Write-Host "Errors:           $errorCount"
Write-Host "Total size:       $totalMB MB"
Write-Host "Duration:         $($duration.ToString('hh\:mm\:ss'))"
Write-Host ""

if ($errorCount -gt 0) {
    Write-Host "WARNING: Some files had errors. Check: $ErrorLogFile" -ForegroundColor Yellow
}

Write-Log "Extraction completed. Copied $copiedFiles files, $errorCount errors." "SUCCESS"
