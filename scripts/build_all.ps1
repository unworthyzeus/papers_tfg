$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$papers = @(
    (Join-Path $root 'drafts\conference_attenuation_priors'),
    (Join-Path $root 'drafts\journal_harpnet')
)

foreach ($paper in $papers) {
    Write-Host "Building $paper"
    Push-Location $paper
    try {
        latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex
    }
    finally {
        Pop-Location
    }
}
