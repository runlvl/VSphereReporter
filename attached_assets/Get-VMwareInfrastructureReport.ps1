# VMware Infrastructure Report Script
[CmdletBinding()]
param(
    [switch]$Force,
    [int]$MaxReportAge = 24
)

$ScriptVersion = "1.5"
$ReportLockFile = "VMwareReport.lock"

function Write-Status {
    param([string]$Message, [string]$Color = "Cyan")
    Write-Host $Message -ForegroundColor $Color
}

function Connect-VIEnvironment {
    Write-Status "Checking vCenter connection..."
    
    if ($global:DefaultVIServer) {
        Write-Status "Already connected to $($global:DefaultVIServer.Name)" "Green"
        return $true
    }
    
    $maxAttempts = 3
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        Write-Status "`nConnection attempt $attempt of $maxAttempts" "Cyan"
        try {
            $server = Read-Host "Enter vCenter/ESXi server name/IP (or 'q' to quit)"
            if ($server -eq 'q') { return $false }
            if ([string]::IsNullOrWhiteSpace($server)) {
                throw "Server name/IP cannot be empty"
            }
            
            $cred = Get-Credential -Message "Enter credentials for $server"
            if (-not $cred) { throw "Credentials required" }
            
            Connect-VIServer -Server $server -Credential $cred -ErrorAction Stop
            Write-Status "Successfully connected to $server" "Green"
            return $true
        }
        catch {
            Write-Status "Connection failed: $($_.Exception.Message)" "Red"
            $attempt++
            if ($attempt -le $maxAttempts) {
                Write-Status "Please try again..." "Yellow"
            }
        }
    }
    
    Write-Status "Failed to connect after $maxAttempts attempts" "Red"
    return $false
}

function Test-ReportLock {
    if (Test-Path $ReportLockFile) {
        $lockTime = [DateTime]::ParseExact((Get-Content $ReportLockFile), "yyyyMMdd_HHmm", $null)
        if (((Get-Date) - $lockTime).TotalMinutes -lt 5) {
            return $true
        }
    }
    Set-Content -Path $ReportLockFile -Value (Get-Date -Format "yyyyMMdd_HHmm")
    return $false
}

function Remove-ReportLock {
    if (Test-Path $ReportLockFile) {
        Remove-Item $ReportLockFile -Force
    }
}

try {
    # Check for recent reports unless forced
    if (-not $Force) {
        $recentReport = Get-ChildItem "VMware_Report_v${ScriptVersion}_*.html" | 
            Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-$MaxReportAge) } |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1

        if ($recentReport) {
            Write-Status "Recent report found: $($recentReport.Name)" "Yellow"
            Write-Status "Use -Force to generate a new report" "Yellow"
            Invoke-Item $recentReport.FullName
            exit 0
        }
    }

    # Check for running report generation
    if (Test-ReportLock) {
        Write-Status "Another report generation is in progress. Please wait or use -Force." "Yellow"
        exit 0
    }

    # Verify PowerCLI
    Write-Status "Checking PowerCLI installation..."
    try {
        Import-Module VMware.PowerCLI -ErrorAction Stop
        Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false | Out-Null
    }
    catch {
        Write-Status "PowerCLI not found or failed to load. Please install it first." "Red"
        exit 1
    }

    # Connect to vCenter
    if (-not (Connect-VIEnvironment)) {
        Write-Status "Failed to connect to vCenter. Exiting." "Red"
        exit 1
    }

    # Collect data
    Write-Status "Collecting VM data..."
    $vms = Get-VM | Sort-Object Name
    
    Write-Status "Collecting snapshot data..."
    $snapshots = foreach ($vm in $vms) {
        Get-Snapshot -VM $vm -ErrorAction SilentlyContinue | ForEach-Object {
            $size = [math]::Round(($_ | Get-HardDisk | Measure-Object -Property CapacityGB -Sum).Sum, 2)
            [PSCustomObject]@{
                VM = $vm.Name
                Name = $_.Name
                Created = $_.Created
                Age = [math]::Round(((Get-Date) - $_.Created).TotalDays, 1)
                SizeGB = $size
            }
        }
    }
    
    Write-Status "Collecting VMDK data..."
    $disks = foreach ($vm in $vms) {
        Get-HardDisk -VM $vm | ForEach-Object {
            [PSCustomObject]@{
                VM = $vm.Name
                Path = $_.Filename
                SizeGB = [math]::Round($_.CapacityGB, 2)
                Format = $_.StorageFormat
            }
        }
    }

    # Generate report filename
    $timestamp = Get-Date -Format "yyyyMMdd_HHmm"
    $reportPath = ".\VMware_Report_v${ScriptVersion}_${timestamp}.html"

    # Generate HTML report
    Write-Status "Generating HTML report..."
    # Initialize an empty ArrayList to store HTML fragments
    $htmlParts = [System.Collections.ArrayList]::new()
    
    $report = @"
<!DOCTYPE html>
<html>
<head>
    <title>VMware Infrastructure Report - Bechtle</title>
    <style>
        :root {
            --bechtle-blue: #004669;
            --secondary-blue: #0073a3;
            --accent-orange: #ff6d00;
            --light-grey: #f5f6f7;
            --border-color: #dee2e6;
            --warning-color: #fff3cd;
            --error-color: #f8d7da;
            --healthy-color: #d4edda;
        }
        
        html {
            scroll-behavior: smooth;
            scroll-padding-top: 60px;
        }
        
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 0; 
            background: var(--light-grey); 
            color: #333;
        }
        
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
        }
        
        .bechtle-header {
            display: flex;
            align-items: center;
            background: white;
            padding: 15px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .bechtle-logo {
            height: 60px;
            margin-right: 20px;
        }
        
        .header-text {
            flex-grow: 1;
            text-align: right;
        }
        
        .header { 
            background: var(--bechtle-blue); 
            color: white; 
            padding: 20px; 
            border-radius: 5px; 
            margin-bottom: 20px; 
        }
        
        .report-nav {
            position: sticky;
            top: 0;
            background: var(--bechtle-blue);
            padding: 0 20px;
            z-index: 1000;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .report-nav ul {
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
        }
        
        .report-nav li {
            padding: 0;
            margin: 0;
        }
        
        .report-nav a {
            display: block;
            color: white;
            text-decoration: none;
            padding: 15px 20px;
            font-weight: 600;
            transition: background-color 0.3s, color 0.3s;
        }
        
        .report-nav a:hover {
            background-color: rgba(255, 255, 255, 0.1);
            color: var(--accent-orange);
        }
        
        .section { 
            background: white; 
            padding: 20px; 
            margin: 20px 0; 
            border-radius: 5px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .summary-card {
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            transition: box-shadow 0.3s ease;
        }
        
        .summary-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 10px 0; 
        }
        
        th, td { 
            padding: 12px; 
            text-align: left; 
            border: 1px solid var(--border-color); 
        }
        
        th { 
            background: var(--bechtle-blue); 
            color: white; 
        }
        
        tr:nth-child(even) { background: var(--light-grey); }
        
        .warning { background: var(--warning-color); }
        .error { background: var(--error-color); }
        .healthy { background: var(--healthy-color); }
        
        @media (max-width: 768px) {
            .report-nav ul {
                flex-direction: column;
            }
            
            .bechtle-header {
                flex-direction: column;
                text-align: center;
            }
            
            .header-text {
                text-align: center;
                margin-top: 10px;
            }
            
            .bechtle-logo {
                margin-right: 0;
            }
        }
    </style>
</head>
<body>
    <div class="bechtle-header">
        <img src="https://www.bechtle.com/at/fcs-utils/getasset/company/standard-logo" alt="Bechtle Logo" class="bechtle-logo">
        <div class="header-text">
            <h2>VMware Infrastructure Report</h2>
        </div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>VMware Infrastructure Report</h1>
            <p>Server: $($global:DefaultVIServer.Name)</p>
            <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')</p>
            <p>Version: $ScriptVersion</p>
        </div>
        
        <nav class="report-nav">
            <ul>
                <li><a href="#summary">Summary Overview</a></li>
                <li><a href="#tools-status">VMware Tools Status</a></li>
                <li><a href="#snapshots">VM Snapshots</a></li>
                <li><a href="#vmdks">Virtual Disks</a></li>
            </ul>
        </nav>

        <div class="section" id="summary">
            <h2>Summary Overview</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Virtual Machines</h3>
                    <p>Total: $($vms.Count)</p>
                    <p>Powered On: $($vms.Where({$_.PowerState -eq 'PoweredOn'}).Count)</p>
                    <p>Powered Off: $($vms.Where({$_.PowerState -eq 'PoweredOff'}).Count)</p>
                </div>
                <div class="summary-card">
                    <h3>Snapshots</h3>
                    <p>Total: $($snapshots.Count)</p>
                    <p>Older than 7 days: $($snapshots.Where({$_.Age -gt 7}).Count)</p>
                    <p>Total Size: $([math]::Round(($snapshots | Measure-Object -Property SizeGB -Sum).Sum, 2)) GB</p>
                </div>
                <div class="summary-card">
                    <h3>Virtual Disks</h3>
                    <p>Total: $($disks.Count)</p>
                    <p>Total Size: $([math]::Round(($disks | Measure-Object -Property SizeGB -Sum).Sum, 2)) GB</p>
                </div>
            </div>
        </div>

        <div class="section" id="tools-status">
            <h2>VMware Tools Status</h2>
            <table>
                <tr>
                    <th>VM Name</th>
                    <th>Power State</th>
                    <th>Tools Status</th>
                    <th>Tools Version</th>
                    <th>CPU</th>
                    <th>Memory (GB)</th>
                </tr>
"@

    # Create an array to hold all HTML fragments
    $htmlParts = [System.Collections.ArrayList]::new()
    $htmlParts.Add($report) | Out-Null
    
    foreach ($vm in $vms) {
        $status = $vm.ExtensionData.Guest.ToolsStatus
        $version = $vm.ExtensionData.Guest.ToolsVersion
        $class = switch ($status) {
            "toolsOld" { "warning" }
            { $_ -in "toolsNotInstalled","toolsNotRunning" } { "error" }
            "toolsOk" { "healthy" }
            default { "" }
        }
        $htmlParts.Add("<tr class='$class'><td>$($vm.Name)</td><td>$($vm.PowerState)</td><td>$status</td><td>$version</td><td>$($vm.NumCpu)</td><td>$($vm.MemoryGB)</td></tr>") | Out-Null
    }
    $htmlParts.Add("</table></div>") | Out-Null
    
    # Reset report variable to be the joined HTML
    $report = $htmlParts -join ""
    $htmlParts.Clear()

    if ($snapshots) {
        $snapshotsHeader = @"
        <div class="section" id="snapshots">
            <h2>VM Snapshots</h2>
            <table>
                <tr>
                    <th>VM</th>
                    <th>Snapshot</th>
                    <th>Created</th>
                    <th>Age (Days)</th>
                    <th>Size (GB)</th>
                </tr>
"@
        # Create an array to hold snapshot HTML fragments
        $htmlParts = [System.Collections.ArrayList]::new()
        $htmlParts.Add($report) | Out-Null
        $htmlParts.Add($snapshotsHeader) | Out-Null
        
        foreach ($snap in $snapshots) {
            $class = if ($snap.Age -gt 7) { "error" } elseif ($snap.Age -gt 3) { "warning" } else { "" }
            $htmlParts.Add("<tr class='$class'><td>$($snap.VM)</td><td>$($snap.Name)</td><td>$($snap.Created)</td><td>$($snap.Age)</td><td>$($snap.SizeGB)</td></tr>") | Out-Null
        }
        $htmlParts.Add("</table></div>") | Out-Null
        
        # Reset report variable to be the joined HTML
        $report = $htmlParts -join ""
        $htmlParts.Clear()
    }

    $vmdkHeader = @"
        <div class="section" id="vmdks">
            <h2>Virtual Disks (VMDKs)</h2>
            <table>
                <tr>
                    <th>VM</th>
                    <th>VMDK Path</th>
                    <th>Size (GB)</th>
                    <th>Format</th>
                </tr>
"@
    # Create an array to hold VMDK HTML fragments
    $htmlParts = [System.Collections.ArrayList]::new()
    $htmlParts.Add($report) | Out-Null
    $htmlParts.Add($vmdkHeader) | Out-Null
    
    foreach ($disk in $disks) {
        $htmlParts.Add("<tr><td>$($disk.VM)</td><td>$($disk.Path)</td><td>$($disk.SizeGB)</td><td>$($disk.Format)</td></tr>") | Out-Null
    }
    $htmlParts.Add("</table></div></div></body></html>") | Out-Null
    
    # Final HTML report
    $report = $htmlParts -join ""

    # Save and open report
    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Status "`nReport generated successfully:" "Green"
    Write-Status "Path: $reportPath" "Green"
    Invoke-Item $reportPath

    # Cleanup old reports
    Get-ChildItem "VMware_Report_*.html" | 
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddHours(-$MaxReportAge) } |
        Remove-Item -Force
}
catch {
    Write-Status "Error generating report: $_" "Red"
}
finally {
    Remove-ReportLock
    if ($global:DefaultVIServer) {
        Write-Status "`nDisconnecting from vCenter..." "Cyan"
        Disconnect-VIServer -Server $global:DefaultVIServer -Confirm:$false
    }
}
