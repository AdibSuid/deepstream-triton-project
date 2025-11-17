Write-Host "Available Models:" -ForegroundColor Cyan

try {
    $yolo = Invoke-RestMethod -Uri "http://localhost:8000/v2/models/yolo11n" -UseBasicParsing
    Write-Host "`n✓ yolo11n" -ForegroundColor Green
    Write-Host "  Platform: $($yolo.platform)"
    Write-Host "  Versions: $($yolo.versions -join ', ')"
    Write-Host "  Input: $($yolo.inputs[0].name) - $($yolo.inputs[0].shape -join 'x')"
    Write-Host "  Output: $($yolo.outputs[0].name) - $($yolo.outputs[0].shape -join 'x')"
} catch {
    Write-Host "✗ yolo11n not available" -ForegroundColor Red
}

try {
    $rfdetr = Invoke-RestMethod -Uri "http://localhost:8000/v2/models/rf-detr-nano" -UseBasicParsing
    Write-Host "`n✓ rf-detr-nano" -ForegroundColor Green
    Write-Host "  Platform: $($rfdetr.platform)"
    Write-Host "  Versions: $($rfdetr.versions -join ', ')"
    Write-Host "  Input: $($rfdetr.inputs[0].name) - $($rfdetr.inputs[0].shape -join 'x')"
    Write-Host "  Output: $($rfdetr.outputs[0].name) - $($rfdetr.outputs[0].shape -join 'x')"
} catch {
    Write-Host "✗ rf-detr-nano not available" -ForegroundColor Red
}