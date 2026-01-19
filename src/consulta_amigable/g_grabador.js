// Grabador de clicks para macros (vibecodeado)

() => {
    // Inicializar si no existe
    if (!window.clicks) {
        window.clicks = [];
    }
    
    // Evitar duplicar listeners
    if (window._clickListenerInjected) {
        return;
    }
    window._clickListenerInjected = true;
    
    // Función para guardar click
    function guardarClick(elemento) {
        const tag = elemento.tagName;
        const texto = elemento.innerText?.trim() || '';
        const valor = elemento.value || '';
        const tipo = elemento.type || '';
        
        const click = {
            tag: tag,
            texto: texto.substring(0, 100),
            valor: valor,
            tipo: tipo,
            timestamp: Date.now()
        };
        
        window.clicks.push(click);
        console.log(`[CLICK #${window.clicks.length}] ${tag}: ${texto.substring(0, 40) || valor}`);
        
        // GUARDAR EN LOCALSTORAGE INMEDIATAMENTE (para botones)
        try {
            localStorage.setItem('_macro_clicks', JSON.stringify(window.clicks));
        } catch(e) {}
    }
    
    // CAPTURAR CLICKS NORMALES (filas, etc)
    document.addEventListener('click', (e) => {
        // NO capturar botones submit aquí (ya se capturaron en mousedown)
        if (e.target.tagName === 'INPUT' && e.target.type === 'submit') {
            return;
        }
        guardarClick(e.target);
    }, true);
    
    // CAPTURAR CLICKS EN BOTONES (ANTES de que se envíe el form)
    document.addEventListener('mousedown', (e) => {
        if (e.target.tagName === 'INPUT' && e.target.type === 'submit') {
            guardarClick(e.target);
        }
    }, true);
    
    // Restaurar clicks de localStorage si existen
    try {
        const saved = localStorage.getItem('_macro_clicks');
        if (saved) {
            window.clicks = JSON.parse(saved);
            console.log(`[GRABADOR] Restaurados ${window.clicks.length} clicks previos`);
        }
    } catch(e) {}                        
}