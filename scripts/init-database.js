const fs = require('fs')
const path = require('path')

const repoRoot = path.resolve(__dirname, '..')
const dbPath = path.join(repoRoot, 'farmtech.db')

function ensureDatabaseFile() {
  if (fs.existsSync(dbPath)) {
    console.log(`[init-database] OK: usando banco existente em ${dbPath}`)
    return
  }

  // Cria arquivo vazio; o FastAPI cria as tabelas na subida
  try {
    fs.writeFileSync(dbPath, '')
    console.log(`[init-database] Banco criado em ${dbPath}`)
  } catch (err) {
    console.error('[init-database] Falha ao criar banco:', err)
    process.exit(1)
  }
}

ensureDatabaseFile()
