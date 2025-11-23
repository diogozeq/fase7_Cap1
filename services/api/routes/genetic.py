from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import Optional

from services.core.ml_models.genetic_optimizer import GeneticOptimizer

router = APIRouter(prefix="/genetic", tags=["Ir Além - Algoritmo Genético"])


class RunGeneticRequest(BaseModel):
    scenario: str = Field(default="alta_produtividade", description="organico | irrigacao_minima | alta_produtividade")
    population_size: Optional[int] = None
    generations: Optional[int] = None
    mutation_rate: Optional[float] = None
    crossover_rate: Optional[float] = None
    elitism: Optional[int] = None
    seed: Optional[int] = None
    refresh_dataset: bool = False
    compare_all: bool = True
    strategy: Optional[str] = Field(default=None, description="baseline | elitist_adaptive")


@router.get("/scenarios")
async def get_scenarios(request: Request, refresh: bool = False):
    """Retorna cenários pré-definidos, sugestão automática de parâmetros e o caminho do dataset salvo."""
    optimizer = GeneticOptimizer(request.app.state.db)
    dataset = optimizer.load_dataset(refresh=refresh)
    return {
        "dataset": optimizer.summarize_dataset(dataset),
        "scenarios": optimizer.scenario_options(dataset),
        "suggestion": optimizer.suggest_parameters(dataset),
    }


@router.post("/run")
async def run_genetic(request: Request, payload: RunGeneticRequest):
    """
    Executa o algoritmo genético usando dados reais do banco, salvando/recuperando o dataset de entrada.
    Também executa uma compara��o contra a estrat��gia baseline para medir ganho de qualidade e tempo.
    """
    optimizer = GeneticOptimizer(request.app.state.db)
    dataset = optimizer.load_dataset(refresh=payload.refresh_dataset)
    params = {
        "population_size": payload.population_size,
        "generations": payload.generations,
        "mutation_rate": payload.mutation_rate,
        "crossover_rate": payload.crossover_rate,
        "elitism": payload.elitism,
        "seed": payload.seed,
        "strategy": payload.strategy or "elitist_adaptive",
    }
    result = optimizer.run_with_comparison(
        dataset=dataset,
        scenario_key=payload.scenario,
        user_params=params,
        compare_all=payload.compare_all,
    )
    return result
