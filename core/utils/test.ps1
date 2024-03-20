function Test-InternetConnection {
    try {
        $response = Test-Connection -ComputerName "www.google.com" -Count 1 -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Set-IP {
    param (
        [string]$interfaceName,
        [string]$ipAddress,
        [string]$subnetMask,
        [string]$defaultGateway,
        [string[]]$dnsServers
    )

    Get-NetIPAddress -InterfaceAlias $interfaceName | Remove-NetIPAddress -Confirm:$false
    Get-NetRoute -InterfaceAlias $interfaceName | Remove-NetRoute -Confirm:$false
    New-NetIPAddress -InterfaceAlias $interfaceName -IPAddress $ipAddress -PrefixLength 20 -DefaultGateway $defaultGateway
    Set-DnsClientServerAddress -InterfaceAlias $interfaceName -ServerAddresses $dnsServers
}

function Increment-IPAddress {
    param (
        [string]$IPAddress
    )

    $ipParts = $IPAddress.Split('.')
    [int]$lastByte = $ipParts[3]
    if ($lastByte -lt 255) {
        $lastByte++
        $ipParts[3] = $lastByte.ToString()
        return $ipParts -join '.'
    } else {
        throw "IP Address incrementation exceeded subnet range."
    }
}

# Configuration
$interfaceName = "Ethernet 2"
$subnetMask = "255.255.240.0"
$defaultGateway = "128.255.44.1"
$dnsServers = @("128.255.1.3", "128.255.64.11", "128.255.1.8")

# Attempt to set IP from ip.txt or find a new one
function Attempt-SetIP {
    $ipContent = Get-Content "C:\Users\hussa\Desktop\sparta-aceap\engine\src\utils\ip.txt"
    $takenAddresses = Get-Content "C:\Users\hussa\Desktop\sparta-aceap\engine\src\utils\taken.txt" -ErrorAction SilentlyContinue | Where-Object { $_ -ne "" }
    # add current IP to takenAddresses
    $currentIPAddress = (Get-NetIPAddress -InterfaceAlias $interfaceName -AddressFamily IPv4).IPAddress
    Write-Host "Current IP $currentIPAddress Changing to $ipContent."
    $takenAddresses += $currentIPAddress

    if ($ipContent -ne 'get-ip') {
        # If ip.txt contains a specific IP address, use it directly
        $currentIPAddress = $ipContent
    } else {
        # Find a new IP address not in taken.txt and that can connect to the internet
        $currentIPAddress = (Get-NetIPAddress -InterfaceAlias $interfaceName -AddressFamily IPv4).IPAddress
        do {
            if ($takenAddresses -notcontains $currentIPAddress) {
                Set-IP -interfaceName $interfaceName -ipAddress $currentIPAddress -subnetMask $subnetMask -defaultGateway $defaultGateway -dnsServers $dnsServers
                Start-Sleep -Seconds 30 # Wait for network settings to apply
                $hasInternet = Test-InternetConnection
                if ($hasInternet) {
                    Write-Host "Successfully changed IP to $currentIPAddress and confirmed internet connectivity."
                    break
                }
            }
            $currentIPAddress = Increment-IPAddress -IPAddress $currentIPAddress
            Write-Host "Testing IP $currentIPAddress..."
        } while ($true)
    }
    # Apply the IP address if it's specifically set in ip.txt or found above
    if ($ipContent -ne 'get-ip') {
        Set-IP -interfaceName $interfaceName -ipAddress $currentIPAddress -subnetMask $subnetMask -defaultGateway $defaultGateway -dnsServers $dnsServers
        Start-Sleep -Seconds 30 # Wait for network settings to apply
        $hasInternet = Test-InternetConnection
        if ($hasInternet) {
            Write-Host "Successfully changed IP to $currentIPAddress."
        } else {
            Write-Host "IP $currentIPAddress was set but internet connectivity could not be confirmed."
        }
    }
}

Attempt-SetIP