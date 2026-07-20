param(
    [string]$BaseUrl = "http://localhost/quiz-pengupil-main"
)

$ErrorActionPreference = "Stop"
$env:BASE_URL = $BaseUrl
$env:DB_HOST = if ($env:DB_HOST) { $env:DB_HOST } else { "127.0.0.1" }
$env:DB_USER = if ($env:DB_USER) { $env:DB_USER } else { "root" }
$env:DB_PASSWORD = if ($null -ne $env:DB_PASSWORD) { $env:DB_PASSWORD } else { "" }
$env:DB_NAME = if ($env:DB_NAME) { $env:DB_NAME } else { "quiz_pengupil" }
$env:CI = "true"

Write-Host "Memeriksa aplikasi: $env:BASE_URL" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$env:BASE_URL/login.php" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -ne 200) { throw "HTTP status bukan 200" }
} catch {
    Write-Error "Halaman aplikasi tidak dapat diakses. Pastikan Apache XAMPP aktif dan URL benar. Detail: $($_.Exception.Message)"
    exit 1
}

New-Item -ItemType Directory -Force -Path artifacts | Out-Null
Write-Host "Menjalankan 20 testcase Selenium..." -ForegroundColor Cyan
python -m pytest tests/ -v --junitxml=artifacts/report.xml
$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Host "Test selesai tanpa kegagalan assertion." -ForegroundColor Green
} else {
    Write-Warning "Test selesai dengan exit code $exitCode. Periksa artifacts/report.xml dan screenshot."
}
exit $exitCode
