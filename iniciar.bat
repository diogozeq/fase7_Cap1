@echo off
REM Inicia frontend (Nuxt) e backend (FastAPI) com um clique, usando o npm run dev já configurado.
setlocal

REM Ir para a pasta do script
cd /d "%~dp0"

REM Mostrar caminho e comando que será executado
echo ===============================================
echo  Iniciando FarmTech (frontend + backend)
echo  Diretório: %CD%
echo  Comando: npm run dev
echo ===============================================
echo.

REM Executa o npm run dev (inclui predev, API e web em paralelo)
npm run dev

endlocal
