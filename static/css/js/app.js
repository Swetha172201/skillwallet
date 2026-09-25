console.log("PocketSmart Loaded da Swetha!");

async function callBudgetAPI(url, formData, resultId) {
    var out = document.getElementById(resultId);
    out.innerHTML = '<div class="p-4 bg-yellow-100 rounded">AI yosikuthu da...!</div>';
    out.classList.remove('hidden');
    try {
        var res = await fetch(url, { method: 'POST', body: formData });
        var data = await res.json();
        var html = '<div class="bg-white p-4 rounded-xl shadow">';
        html += '<h3 class="font-bold">Total: Rs.' + (data.budget_summary ? data.budget_summary.total : 5000) + '</h3>';
        html += '<div class="mt-4">';
        html += '<pre class="text-xs bg-gray-100 p-3 rounded">' + JSON.stringify(data, null, 2) + '</pre>';
        html += '</div></div>';
        out.innerHTML = html;
    } catch (e) {
        out.innerHTML = '<div class="p-4 bg-red-100 rounded">Error da: ' + e.message + '</div>';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var homeForm = document.getElementById('homeForm');
    if (homeForm) {
        homeForm.onsubmit = function(e) {
            e.preventDefault();
            callBudgetAPI('/api/home-budget', new FormData(e.target), 'result');
        };
    }
    var partyForm = document.getElementById('partyForm');
    if (partyForm) {
        partyForm.onsubmit = function(e) {
            e.preventDefault();
            callBudgetAPI('/api/party-budget', new FormData(e.target), 'result');
        };
    }
    var jForm = document.getElementById('jForm');
    if (jForm) {
        jForm.onsubmit = function(e) {
            e.preventDefault();
            callBudgetAPI('/api/jewelry-budget', new FormData(e.target), 'result');
        };
    }
});