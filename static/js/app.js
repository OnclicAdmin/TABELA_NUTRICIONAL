const API_BASE = 'http://127.0.0.1:5000/api';

const productNameInput = document.getElementById('productName');
const servingTypeSelect = document.getElementById('servingType');
const ingredientCountInput = document.getElementById('ingredientCount');
const addIngredientsBtn = document.getElementById('addIngredientsBtn');
const ingredientsList = document.getElementById('ingredientsList');
const calculateBtn = document.getElementById('calculateBtn');
const resultContainer = document.getElementById('resultContainer');
const newCalculationBtn = document.getElementById('newCalculationBtn');
const printBtn = document.getElementById('btn-print-table') || document.getElementById('printBtn');
const downloadBtn = document.getElementById('btn-export-pdf-table') || document.getElementById('downloadBtn');

if (addIngredientsBtn) addIngredientsBtn.addEventListener('click', addIngredientFields);
if (calculateBtn) calculateBtn.addEventListener('click', calculateRecipe);
if (newCalculationBtn) newCalculationBtn.addEventListener('click', resetForm);

// Função robusta para exportar/imprimir APENAS a tabela nutricional com estilos inline
function exportTableToWindow(areaId, title = 'Tabela Nutricional') {
    const area = document.getElementById(areaId);
    if (!area) {
        showNotification('Nenhuma tabela gerada para exportar.', 'warning');
        return;
    }

    // Extrai conteúdo limpo (sem scripts, eventos, etc)
    const tableHtml = area.innerHTML;

    const fullHtml = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        @page {
            size: A4;
            margin: 15mm;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #fff;
            padding: 20px;
        }
        
        h5 {
            color: #28a745;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            border-bottom: 2px solid #28a745;
            padding-bottom: 10px;
        }
        
        .row {
            display: flex;
            flex-wrap: wrap;
            margin-bottom: 15px;
            gap: 20px;
        }
        
        .col-md-6 {
            flex: 0 0 calc(50% - 10px);
            min-width: 250px;
        }
        
        .col-md-6 strong {
            color: #28a745;
            font-weight: 600;
        }
        
        .alert {
            padding: 15px;
            margin: 15px 0;
            border-radius: 6px;
            border-left: 4px solid #17a2b8;
            background-color: #d1ecf1;
            color: #0c5460;
        }
        
        .alert h6 {
            margin-top: 0;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .alert-light {
            background-color: #f8f9fa;
            border-left-color: #6c757d;
            color: #212529;
        }
        
        .table-responsive {
            overflow-x: auto;
            margin: 20px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        thead {
            background-color: #f8f9fa;
            border-bottom: 2px solid #28a745;
        }
        
        th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #28a745;
            border: 1px solid #dee2e6;
        }
        
        td {
            padding: 10px 12px;
            border: 1px solid #dee2e6;
            text-align: left;
        }
        
        tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        tbody tr:hover {
            background-color: #e8f5e9;
        }
        
        .table-primary {
            background-color: #e8f5e9 !important;
            font-weight: 600;
            color: #155724;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            background-color: #17a2b8;
            color: white;
        }
        
        .badge.bg-warning {
            background-color: #ffc107 !important;
            color: #000 !important;
        }
        
        .badge.bg-info {
            background-color: #17a2b8 !important;
            color: #fff !important;
        }
        
        .text-muted {
            color: #6c757d;
        }
        
        .text-dark {
            color: #212529;
        }
        
        small {
            font-size: 0.875em;
        }
        
        @media print {
            body {
                padding: 0;
            }
            
            @page {
                margin: 10mm;
            }
        }
    </style>
</head>
<body>
    ${tableHtml}
</body>
</html>`;

    // Abre nova janela com conteúdo
    const w = window.open('', '_blank', 'width=1000,height=800');
    if (!w) {
        showNotification('O navegador bloqueou a abertura de popup. Verifique as configurações.', 'danger');
        return;
    }

    w.document.open();
    w.document.write(fullHtml);
    w.document.close();

    // Aguarda carregar e imprime
    w.onload = () => {
        w.focus();
        setTimeout(() => {
            w.print();
        }, 250);
    };
}

// Associa botões
if (printBtn) {
    printBtn.addEventListener('click', () => exportTableToWindow('nutrition-print-area', 'Imprimir Tabela Nutricional'));
}
if (downloadBtn) {
    downloadBtn.addEventListener('click', () => exportTableToWindow('nutrition-print-area', 'Exportar Tabela Nutricional'));
}

if (ingredientsList) {
    ingredientsList.addEventListener('click', function (event) {
        const chip = event.target.closest && event.target.closest('.suggestion-chip');
        if (chip) {
            const value = chip.dataset.value;
            const index = chip.dataset.index;
            const row = document.querySelector(`.ingredient-name[data-index="${index}"]`);
            if (row) {
                row.value = value;
                row.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    });
}

function addIngredientFields() {
    const defaultCount = 3;
    const count = parseInt(ingredientCountInput?.value || String(defaultCount), 10) || defaultCount;
    ingredientsList.innerHTML = '';
    for (let i = 0; i < count; i++) {
        const ingredientRow = document.createElement('div');
        ingredientRow.className = 'row mb-3 ingredient-row';
        ingredientRow.innerHTML = `
            <div class="col-md-6">
                <label class="form-label">Ingrediente ${i + 1}</label>
                <input type="text" class="form-control ingredient-name" placeholder="Ex: Farinha" data-index="${i}">
                <div class="mt-1" id="suggestion-${i}"></div>
            </div>
            <div class="col-md-3">
                <label class="form-label">Quantidade</label>
                <input type="number" class="form-control ingredient-quantity" placeholder="200" step="0.1" data-index="${i}">
            </div>
            <div class="col-md-3">
                <label class="form-label">Unidade</label>
                <input type="text" class="form-control ingredient-unit" placeholder="g" value="g" data-index="${i}">
            </div>
        `;
        ingredientsList.appendChild(ingredientRow);

        const ingredientInput = ingredientRow.querySelector('.ingredient-name');
        if (ingredientInput) {
            ingredientInput.addEventListener('input', searchIngredient);
        }
    }
}

async function searchIngredient(e) {
    const query = e.target.value || '';
    const index = e.target.dataset.index;
    const suggestionDiv = document.getElementById(`suggestion-${index}`);
    if (!suggestionDiv) return;

    if (query.length < 2) {
        suggestionDiv.innerHTML = '';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/search-ingredient?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Erro ao buscar sugestões');
        const suggestions = await response.json();
        suggestionDiv.innerHTML = suggestions.length === 0
            ? '<small class="text-muted">Nenhuma sugestão encontrada.</small>'
            : suggestions.map(s => `
                <button type="button" class="btn btn-sm btn-outline-secondary suggestion-chip me-1 mb-1"
                    data-index="${index}"
                    data-value="${s.food}">
                    ${s.food}
                </button>`).join('');
    } catch (error) {
        console.error('Erro ao buscar sugestões:', error);
    }
}

async function calculateRecipe() {
    const productName = productNameInput?.value || 'Produto';
    const servingType = servingTypeSelect?.value || '100g';
    const ingredients = [];

    document.querySelectorAll('.ingredient-row').forEach(row => {
        const name = row.querySelector('.ingredient-name')?.value.trim() || '';
        const quantityRaw = row.querySelector('.ingredient-quantity')?.value;
        const quantity = quantityRaw !== undefined && quantityRaw !== '' ? parseFloat(quantityRaw) : NaN;
        const unit = row.querySelector('.ingredient-unit')?.value.trim() || '';
        if (name && !Number.isNaN(quantity)) {
            ingredients.push({ name, quantity, unit });
        }
    });

    if (ingredients.length === 0) {
        showNotification('Por favor, preencha pelo menos um ingrediente válido.', 'warning');
        return;
    }

    if (calculateBtn) {
        calculateBtn.disabled = true;
        calculateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Calculando...';
    }

    try {
        const response = await fetch(`${API_BASE}/calculate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_name: productName, serving_type: servingType, ingredients })
        });

        const text = await response.text();
        let result;
        try {
            result = JSON.parse(text);
        } catch {
            throw new Error(text || 'Resposta inválida do servidor');
        }

        if (!response.ok) {
            throw new Error(result.error || 'Erro ao calcular');
        }

        displayResult(result);
    } catch (error) {
        console.error('Erro:', error);
        showNotification(`Erro ao calcular: ${error.message}`, 'danger');
    } finally {
        if (calculateBtn) {
            calculateBtn.disabled = false;
            calculateBtn.innerHTML = '<i class="fas fa-calculator"></i> Calcular Tabela Nutricional';
        }
    }
}

function displayResult(data) {
    document.getElementById('resultProductName').textContent = `Tabela Nutricional - ${data.product_name}`;
    document.getElementById('resultPortion').textContent = data.portion || '100g';
    document.getElementById('resultServings').textContent = data.servings_per_package ?? '-';

    const highlights = data.highlights || [];
    const highlightsHtml = highlights.length
        ? highlights.map(label => `<span class="badge bg-warning text-dark me-1">${label}</span>`).join('')
        : '<span class="text-muted">Nenhum alerta de alto teor.</span>';
    document.getElementById('highlightLabels').innerHTML = highlightsHtml;

    document.getElementById('ingredientsUsedList').innerHTML = data.ingredients_used.map(ing => `
        <div class="row mb-2">
            <div class="col-md-6">${ing.original} → <strong>${ing.matched || 'não encontrado'}</strong></div>
            <div class="col-md-3"><small class="text-muted">${ing.quantity_grams} g</small></div>
            <div class="col-md-3"><small class="badge bg-info">Score: ${ing.match_score}%</small></div>
        </div>
    `).join('');

    document.getElementById('nutritionTableBody').innerHTML = data.nutrition_table.map(nutrient => `
        <tr${nutrient.mandatory ? ' class="table-primary"' : ''}>
            <td><strong>${nutrient.nutrient}</strong></td>
            <td>${nutrient.value_per_serving} ${nutrient.unit}</td>
            <td>${nutrient.daily_value_percent ? nutrient.daily_value_percent + '%' : '-'}</td>
        </tr>
    `).join('');

    resultContainer.classList.remove('d-none');
    resultContainer.scrollIntoView({ behavior: 'smooth' });
}

function resetForm() {
    if (productNameInput) productNameInput.value = '';
    if (servingTypeSelect) servingTypeSelect.value = '100g';
    if (ingredientCountInput) ingredientCountInput.value = '3';
    if (ingredientsList) ingredientsList.innerHTML = '';
    if (resultContainer) resultContainer.classList.add('d-none');
    addIngredientFields();
}

function showNotification(message, type = 'info') {
    const toast = document.getElementById('notificationToast');
    const body = document.getElementById('notificationBody');
    if (body) {
        body.textContent = message;
        body.className = `toast-body alert alert-${type} mb-0`;
    }
    if (toast) new bootstrap.Toast(toast).show();
}

document.addEventListener('DOMContentLoaded', () => {
    addIngredientFields();
});