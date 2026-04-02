# CodigodoDestino

SaaS de previsões baseado em astrologia e numerologia com engine determinística + IA.

---

# 🧠 Arquitetura

- Backend: FastAPI + PostgreSQL + Redis
- Frontend: Next.js + Tailwind
- Engine:
  - Astrologia (Swiss Ephemeris)
  - Numerologia
  - Regras simbólicas
- Cache: Redis
- Migrations: Alembic
- IA: OpenRouter (fallback automático)

---

# ⚙️ Setup Backend

```bash
cd backend

# criar ambiente virtual
python -m venv .venv

# ativar (Mac/Linux)
source .venv/bin/activate

# ativar (Windows)
.venv\Scripts\activate

# instalar dependências
pip install -r requirements.txt