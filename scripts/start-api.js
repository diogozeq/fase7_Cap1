const { spawn } = require('child_process')
const path = require('path')
const fs = require('fs')

const repoRoot = path.resolve(__dirname, '..')
const apiDir = path.join(repoRoot, 'services', 'api')
const startApiScript = path.join(repoRoot, 'start_api.py')

function resolvePython() {
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

function startApi() {
  console.log('[start-api] Iniciando FarmTech API...')
  console.log(`[start-api] Projeto: ${repoRoot}`)
  console.log()

  const pythonCmd = resolvePython()
  // Run start_api.py from the repo root directory
  const proc = spawn(pythonCmd, ['start_api.py'], {
    cwd: repoRoot,
    stdio: 'inherit',
    shell: false,
    env: {
      ...process.env,
      PYTHONPATH: repoRoot,
      PYTHONIOENCODING: 'utf-8'
    }
  })

  proc.on('error', (err) => {
    console.error('[start-api] Erro ao iniciar:', err.message)
    process.exit(1)
  })

  proc.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      console.error(`[start-api] API finalizou com código ${code}`)
      process.exit(code)
    }
  })

  // Handle cleanup
  process.on('SIGINT', () => {
    console.log('\n[start-api] Encerrando API...')
    proc.kill('SIGINT')
  })

  process.on('SIGTERM', () => {
    proc.kill('SIGTERM')
  })
}

startApi()
