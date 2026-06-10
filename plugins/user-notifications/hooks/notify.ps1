param(
    [string]$event = "stop",
    [string]$pluginRoot = ""
)

$soundFile = Join-Path $pluginRoot "sounds\notification-sound.wav"

if (Test-Path $soundFile) {
    $player = New-Object System.Media.SoundPlayer $soundFile
    $player.Play()
} else {
    switch ($event) {
        "permission" { [Console]::Beep(1200, 300) }
        default      { [Console]::Beep(880, 200) }
    }
}
