$uri = "http://localhost:8000/api/v1/question/generate"
$body = @{
    chapter = "trigonometry"
    concept = "heights_and_distances"
    difficulty = 0.6
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json"

Write-Host "`nQUESTION GENERATED" -ForegroundColor Green
Write-Host "Source: $($response.source)"
Write-Host "Question: $($response.text)"
Write-Host "Has JSXGraph: $($response.jsxgraph_code -ne $null)"
Write-Host "Answer: $($response.metadata.correct_answer.value)"
