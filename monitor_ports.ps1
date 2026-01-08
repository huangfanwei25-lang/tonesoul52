$logFile = "c:\Users\user\Desktop\倉庫\port_monitor.log"
"Starting Monitor..." | Out-File $logFile
while ($true) {
    $proc = Get-Process darlin -ErrorAction SilentlyContinue
    if ($proc) {
        $id = $proc.Id
        $netstat = netstat -ano | Select-String $id
        if ($netstat) {
            $timestamp = Get-Date -Format "HH:mm:ss.fff"
            foreach ($line in $netstat) {
                "$timestamp - $line" | Out-File $logFile -Append
            }
        }
    }
    Start-Sleep -Milliseconds 100
}
