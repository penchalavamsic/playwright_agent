$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$scenes = Get-Content -LiteralPath (Join-Path $projectPath 'storyboard.json') -Raw | ConvertFrom-Json
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice('Microsoft Zira Desktop')
$voice.Rate = 2
$voice.Volume = 100
foreach ($scene in $scenes) {
    $wavePath = Join-Path $projectPath ('assets/' + $scene.id + '.wav')
    $voice.SetOutputToWaveFile($wavePath)
    $voice.Speak($scene.voice)
    $voice.SetOutputToNull()
}
$voice.Dispose()
Write-Output 'Narration generated for all demo chapters.'
