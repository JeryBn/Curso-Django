const tipo = new URLSearchParams(location.search).get('tipo');
if (['class','key','raiz'].includes(tipo)) import(`./practica-errores/${tipo}.jsx`);
