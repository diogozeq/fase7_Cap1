const { spawn } = require('child_process')
const path = require('path')
const fs = require('fs')

const repoRoot = path.resolve(__dirname, '..')
const dashboardDir = path.join(repoRoot, 'apps', 'dashboard')
const homeScript = path.join(dashboardDir, 'Home.py')

function resolvePython() {
  const apiDir = path.join(repoRoot, 'services', 'api')
  const candidates = [
    process.env.PYTHON,
    path.join(apiDir, '.venv', 'Scripts', 'python.exe'),
    path.join(apiDir, '.venv', 'bin', 'python'),
    'python',
    'python3'
  ].filter(Boolean)

  for (const cmd of candidates) {
    try {
      if (fs.existsSync(cmd)) return cmd
    } catch {}
  }
  return 'python'
}

function startStreamlit() {
  console.log('[start-streamlit] Iniciando Dashboard Streamlit...')
  console.log(`[start-streamlit] Dashboard: ${dashboardDir}`)
  console.log()

  const pythonCmd = resolvePython()

  // Run streamlit
  const proc = spawn(pythonCmd, ['-m', 'streamlit', 'run', 'app.py', '--server.port=8501'], {
    cwd: dashboardDir,
    stdio: 'inherit',
    shell: false,
    env: {
      ...process.env,
      PYTHONPATH: repoRoot,
      PYTHONIOENCODING: 'utf-8'
    }
  })

  proc.on('error', (err) => {
    console.error('[start-streamlit] Erro ao iniciar:', err.message)
    process.exit(1)
  })

  proc.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      console.error(`[start-streamlit] Streamlit finalizou com código ${code}`)
      process.exit(code)
    }
  })

  // Handle cleanup
  process.on('SIGINT', () => {
    console.log('\n[start-streamlit] Encerrando Streamlit...')
    proc.kill('SIGINT')
  })

  process.on('SIGTERM', () => {
    proc.kill('SIGTERM')
  })
}

startStreamlit()
