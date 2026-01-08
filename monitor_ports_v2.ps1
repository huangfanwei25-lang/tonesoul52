$logFile = "c:\Users\user\Desktop\倉庫\port_monitor_v2.log"
"Starting Monitor v2..." | Out-File $logFile
$targetPid = $null

while ($true) {
    if (-not $targetPid) {
        $proc = Get-Process darlin -ErrorAction SilentlyContinue
        if ($proc) { $targetPid = $proc.Id; "Found Darlin PID: $targetPid" | Out-File $logFile -Append }
    }

    if ($targetPid) {
        # Capture all TCP connections for the process
        $conns = Get-NetTCPConnection -OwningProcess $targetPid -ErrorAction SilentlyContinue
        if ($conns) {
            foreach ($c in $conns) {
                # Log everything especially SYN_SENT (Connecting)
                "$($c.State) -> $($c.RemoteAddress):$($c.RemotePort)" | Out-File $logFile -Append
            }
        }
    }
    Start-Sleep -Milliseconds 10
}
