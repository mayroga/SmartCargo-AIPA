let currentLang = 'en';

function toggleLanguage() {
    currentLang = currentLang === 'en' ? 'es' : 'en';
    const btn = document.querySelector('.btn-lang');
    btn.innerText = currentLang === 'en' ? 'EN / ES' : 'ES / EN';
    // Aquí se podrían cambiar etiquetas estáticas si se desea más detalle
}

async function runValidation() {
    const resultArea = document.getElementById('result-area');
    const analysisText = document.getElementById('analysis-text');
    const statusPill = document.getElementById('status-pill');

    analysisText.innerText = "Consulting SMARTCARGO-AIPA Database & Regulations...";
    resultArea.style.display = 'block';

    const formData = new FormData();
    const fields = ['mawb', 'hawb', 'role', 'cargo_type', 'weight', 'length', 'width', 'height', 'origin', 'destination', 'dot'];
    
    fields.forEach(field => {
        formData.append(field, document.getElementById(field).value);
    });

    try {
        const response = await fetch('/validate', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        // Manejo de Semáforo
        const statusMap = {
            'GREEN': { text: '🟢 ACCEPTABLE', color: '#10b981' },
            'YELLOW': { text: '🟡 CONDITIONAL / REVIEW', color: '#f59e0b' },
            'RED': { text: '🔴 REJECTED / CRITICAL', color: '#ef4444' }
        };

        statusPill.innerText = statusMap[data.status].text;
        statusPill.style.backgroundColor = statusMap[data.status].color;

        // Renderizar respuesta (Markdown simplificado a HTML)
        analysisText.innerHTML = `
            <p><strong>Volume:</strong> ${data.volume} m³</p>
            <div>${data.analysis.replace(/\n/g, '<br>')}</div>
            <hr style="border:0; border-top:1px solid #334155; margin:20px 0;">
            <small style="color: #94a3b8;">${data.legal_notice}</small>
        `;

    } catch (error) {
        analysisText.innerText = "System error. Please check connection.";
    }
}

function resetForm() {
    document.querySelectorAll('input').forEach(i => i.value = '');
    document.getElementById('result-area').style.display = 'none';
}

function shareWhatsApp() {
    const text = document.getElementById('analysis-text').innerText;
    const url = `https://wa.me/?text=${encodeURIComponent("SMARTCARGO-AIPA REPORT:\n\n" + text)}`;
    window.open(url, '_blank');
}
