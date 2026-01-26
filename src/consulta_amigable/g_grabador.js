(() => {
    if (!window.clicks) window.clicks = [];
    if (window._clickListenerInjected) return;
    window._clickListenerInjected = true;

    let nivelActual = Math.floor(window.clicks.filter(c => c.tag === 'INPUT').length);

    function getValor(elemento) {
        try {
            const tr = elemento.closest('tr');
            if (tr) {
                const tdLeft = tr.querySelector('td[align="left"]');
                if (tdLeft && tdLeft.innerText.trim()) return tdLeft.innerText.trim();
            }
            return elemento.innerText?.trim() || elemento.value || '';
        } catch(e) {
            return elemento.innerText?.trim() || elemento.value || '';
        }
    }

    function guardarClick(elemento) {
        const tag = elemento.tagName;
        const tipo = elemento.type || '';
        const valor = getValor(elemento);

        const click = {
            tag,
            valor,
            tipo,
            timestamp: Date.now()
        };

        window.clicks.push(click);
        if (tag === 'INPUT') nivelActual++;

        try {
            localStorage.setItem('_macro_clicks', JSON.stringify(window.clicks));
            localStorage.setItem('_macro_nivel', nivelActual.toString());
        } catch(e) {}
    }

    function deshacerAlVolver() {
        if (window.clicks.length === 0) return;

        const ultimoClick = window.clicks[window.clicks.length - 1];
        
        if (ultimoClick.tag === 'TD') {
            let tdsEliminados = 0;
            for (let i = window.clicks.length - 1; i >= 0 && tdsEliminados < 2; i--) {
                if (window.clicks[i].tag === 'TD') {
                    window.clicks.splice(i, 1);
                    tdsEliminados++;
                }
            }
            
            for (let i = window.clicks.length - 1; i >= 0; i--) {
                if (window.clicks[i].tag === 'INPUT') {
                    window.clicks.splice(i, 1);
                    nivelActual--;
                    break;
                }
            }
        } 
        else if (ultimoClick.tag === 'INPUT') {
            window.clicks.pop();
            nivelActual--;
            
            for (let i = window.clicks.length - 1; i >= 0; i--) {
                if (window.clicks[i].tag === 'TD') {
                    window.clicks.splice(i, 1);
                    break;
                }
            }
        }
        
        try {
            localStorage.setItem('_macro_clicks', JSON.stringify(window.clicks));
            localStorage.setItem('_macro_nivel', nivelActual.toString());
        } catch(e) {}
    }

    window.addEventListener('pageshow', (event) => {
        if (event.persisted || performance.navigation.type === 2) {
            setTimeout(() => {
                try {
                    const nivelGuardado = parseInt(localStorage.getItem('_macro_nivel') || '0');
                    const inputsActuales = window.clicks.filter(c => c.tag === 'INPUT').length;
                    
                    if (nivelGuardado > inputsActuales) {
                        deshacerAlVolver();
                    }
                } catch(e) {}
            }, 100);
        }
    });

    document.addEventListener('click', (e) => {
        if (e.target.tagName === 'INPUT' && e.target.type === 'submit') return;
        guardarClick(e.target);
    }, true);

    document.addEventListener('mousedown', (e) => {
        if (e.target.tagName === 'INPUT' && e.target.type === 'submit') {
            const valor = getValor(e.target);
            
            if (valor.toLowerCase().includes('volver') || 
                valor.toLowerCase().includes('atrás') ||
                valor.toLowerCase().includes('retroceder')) {
                deshacerAlVolver();
                return;
            }
            
            guardarClick(e.target);
        }
    }, true);

    try {
        const saved = localStorage.getItem('_macro_clicks');
        if (saved) {
            window.clicks = JSON.parse(saved);
            nivelActual = parseInt(localStorage.getItem('_macro_nivel') || '0');
        }
    } catch(e) {}
})();