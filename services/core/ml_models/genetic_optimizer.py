"""
Genetic Algorithm optimizer adapted for FarmTech resource allocation.
- Uses real data from the SQLite database (producao, insumos, leituras de sensores).
- Persists the generated dataset to a JSON file for reproducibility.
- Provides multiple strategies (baseline vs. elitista/adaptativa) for selection, crossover and mutation.
"""
from __future__ import annotations

import json
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from services.core.database.models import (
    AjusteAplicacao,
    Cultura,
    InsumoCultura,
    LeituraSensor,
    ProducaoAgricola,
    Talhao,
)
from services.core.database.service import DatabaseService


@dataclass
class GeneticParams:
    population_size: int
    generations: int
    mutation_rate: float
    crossover_rate: float
    elitism: int
    seed: int
    strategy: str
    scenario_key: str


class GeneticOptimizer:
    """
    Genetic Algorithm focussed on optimizing allocation of insumos and agua,
    tailored with real FarmTech data and reproducible dataset persistence.
    """

    def __init__(self, db: DatabaseService, data_dir: Optional[Path] = None):
        self.db = db
        self.data_dir = data_dir or Path(__file__).resolve().parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / "genetic_input.json"

    # ---------- Data handling ----------
    def _to_float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except Exception:
            return default

    def _hydrate_inputs(self) -> Dict[str, Any]:
        """Collect real data from the database to feed the GA."""
        with self.db.get_session() as session:
            producoes = [
                {
                    "id_producao": p.id_producao,
                    "id_cultura": p.id_cultura,
                    "quantidade_produzida": self._to_float(p.quantidade_produzida),
                    "valor_estimado": self._to_float(p.valor_estimado),
                    "area_plantada": self._to_float(p.area_plantada),
                }
                for p in session.query(ProducaoAgricola).limit(180).all()
            ]
            insumos = {
                i.id_cultura: {
                    "coef_insumo_por_m2": self._to_float(i.coef_insumo_por_m2),
                    "custo_por_m2": self._to_float(i.custo_por_m2),
                }
                for i in session.query(InsumoCultura).all()
            }
            culturas = {c.id_cultura: c.nome_cultura for c in session.query(Cultura).all()}
            talhoes_count = session.query(Talhao).count()
            ajustes_count = session.query(AjusteAplicacao).count()
            leituras = (
                session.query(
                    LeituraSensor.valor_umidade,
                    LeituraSensor.precipitacao_mm,
                )
                .order_by(LeituraSensor.data_hora_leitura.desc())
                .limit(400)
                .all()
            )

        umidades = [self._to_float(u) for u, _ in leituras if u is not None]
        precs = [self._to_float(p) for _, p in leituras if p is not None]
        avg_umid = statistics.mean(umidades) if umidades else 65.0
        avg_prec = statistics.mean(precs) if precs else 8.0

        return {
            "producoes": producoes,
            "insumos": insumos,
            "culturas": culturas,
            "talhoes_count": talhoes_count,
            "ajustes_count": ajustes_count,
            "avg_umid": avg_umid,
            "avg_prec": avg_prec,
        }

    def _calc_water_need(self, area_ha: float, avg_umid: float, avg_prec: float) -> float:
        """
        Estimate irrigation need (m3) using real soil humidity and rain.
        Higher humidity -> less water; low rain -> more water.
        """
        humidity_gap = max(0.0, 72.0 - avg_umid)
        rain_factor = max(0.0, 12.0 - avg_prec)
        base = 55.0 + humidity_gap * 6.5 + rain_factor * 4.0
        return max(80.0, base) * max(0.6, min(1.4, area_ha / 10.0))

    def _build_dataset(self) -> Dict[str, Any]:
        data = self._hydrate_inputs()
        avg_umid, avg_prec = data["avg_umid"], data["avg_prec"]
        items = []

        for prod in data["producoes"]:
            area = prod.get("area_plantada", 10.0) or 10.0
            valor_estimado = prod.get("valor_estimado", 0.0) or 0.0
            quantidade = prod.get("quantidade_produzida", 0.0) or 0.0
            cultura_nome = data["culturas"].get(prod["id_cultura"], f"Cultura {prod['id_cultura']}")
            insumo = data["insumos"].get(prod["id_cultura"])

            insumo_coef = insumo.get("coef_insumo_por_m2", 0.06) if insumo else 0.06
            insumo_custo_m2 = insumo.get("custo_por_m2", 5.0) if insumo else 5.0
            area_m2 = area * 10_000

            insumo_qtd = round(insumo_coef * area_m2, 2)
            insumo_custo_total_k = round((insumo_custo_m2 * area_m2) / 1000.0, 2)
            valor_k = round(valor_estimado / 1000.0 if valor_estimado else (quantidade * 450) / 1000.0, 2)
            produtividade = round((quantidade / area) if area else 0.0, 2)
            agua_m3 = round(self._calc_water_need(area, avg_umid, avg_prec), 2)

            items.append(
                {
                    "id": prod["id_producao"],
                    "cultura": cultura_nome,
                    "area_ha": round(area, 2),
                    "valor_estimado_k": valor_k,
                    "insumo_custo_k": insumo_custo_total_k,
                    "insumo_qtd": insumo_qtd,
                    "agua_m3": agua_m3,
                    "produtividade_t_ha": produtividade,
                }
            )

        total_cost = sum(i["insumo_custo_k"] for i in items)
        total_water = sum(i["agua_m3"] for i in items)
        dataset = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "stats": {
                "items": len(items),
                "media_valor_k": round(float(np.mean([i["valor_estimado_k"] for i in items])), 2) if items else 0.0,
                "media_custo_k": round(float(np.mean([i["insumo_custo_k"] for i in items])), 2) if items else 0.0,
                "media_agua_m3": round(float(np.mean([i["agua_m3"] for i in items])), 2) if items else 0.0,
                "culturas": sorted(set(i["cultura"] for i in items)),
                "avg_umidade": round(avg_umid, 2),
                "avg_precipitacao": round(avg_prec, 2),
                "total_custo_k": round(total_cost, 2),
                "total_agua_m3": round(total_water, 2),
            },
            "items": items,
            "source": {
                "producoes": len(data["producoes"]),
                "talhoes": data["talhoes_count"],
                "ajustes": data["ajustes_count"],
            },
            "input_file": str(self.data_file),
        }
        self.data_file.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")
        return dataset

    def load_dataset(self, refresh: bool = False) -> Dict[str, Any]:
        if self.data_file.exists() and not refresh:
            return json.loads(self.data_file.read_text(encoding="utf-8"))
        return self._build_dataset()

    def summarize_dataset(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        items = dataset.get("items", [])
        return {
            "generated_at": dataset.get("generated_at"),
            "input_file": dataset.get("input_file"),
            "stats": dataset.get("stats", {}),
            "sample": items[:6],
        }

    # ---------- Parameter suggestion & scenarios ----------
    def suggest_parameters(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        n = max(1, len(dataset.get("items", [])))
        diversity = float(np.std([i["valor_estimado_k"] for i in dataset["items"]])) if dataset.get("items") else 1.0
        pop = int(min(140, max(40, n // 2)))
        gens = int(min(90, max(28, n // 3)))
        mutation = round(min(0.25, 0.05 + (diversity / 5000)), 3)
        crossover = round(0.78 if diversity > 1500 else 0.82, 2)
        elitism = max(2, int(pop * 0.08))
        return {
            "population_size": pop,
            "generations": gens,
            "mutation_rate": mutation,
            "crossover_rate": crossover,
            "elitism": elitism,
            "strategy": "elitist_adaptive",
        }

    def scenario_options(self, dataset: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        stats = dataset.get("stats", {})
        total_cost = stats.get("total_custo_k", 0.0) or 1.0
        total_water = stats.get("total_agua_m3", 0.0) or 1.0

        def build(name: str, cost_ratio: float, water_ratio: float, desc: str) -> Dict[str, Any]:
            return {
                "name": name,
                "budget_k": round(total_cost * cost_ratio, 2),
                "water_limit_m3": round(total_water * water_ratio, 2),
                "description": desc,
            }

        return {
            "organico": build(
                "Agricultura Organica",
                0.42,
                0.45,
                "Mais restritivo em insumos e agua, prioriza sustentabilidade.",
            ),
            "irrigacao_minima": build(
                "Irrigacao Minima",
                0.35,
                0.38,
                "Segura recursos hidricos, indicada para estiagem prolongada.",
            ),
            "alta_produtividade": build(
                "Alta Produtividade",
                0.65,
                0.82,
                "Foca maximizar margem com uso intensivo e controle por penalidade.",
            ),
        }

    # ---------- Genetic algorithm core ----------
    def _evaluate(self, individual: List[int], items: List[Dict[str, Any]], scenario: Dict[str, Any]) -> Dict[str, float]:
        value = cost = water = 0.0
        for gene, item in zip(individual, items):
            if gene:
                value += item["valor_estimado_k"]
                cost += item["insumo_custo_k"]
                water += item["agua_m3"]
        over_cost = max(0.0, cost - scenario["budget_k"])
        over_water = max(0.0, water - scenario["water_limit_m3"])
        penalty = over_cost * 0.65 + over_water * 0.08
        fitness = value - penalty
        return {
            "fitness": round(fitness, 4),
            "value": round(value, 2),
            "cost": round(cost, 2),
            "water": round(water, 2),
        }

    def _roulette_select(self, population: List[List[int]], fitnesses: List[float], rng: random.Random) -> List[int]:
        min_fit = min(fitnesses)
        adjusted = [f - min_fit + 1.0 for f in fitnesses]
        total = sum(adjusted)
        if total <= 0:
            return rng.choice(population)
        pick = rng.uniform(0, total)
        current = 0.0
        for ind, fit in zip(population, adjusted):
            current += fit
            if current >= pick:
                return ind
        return population[-1]

    def _tournament_select(self, population: List[List[int]], fitnesses: List[float], rng: random.Random, size: int = 4) -> List[int]:
        participants = rng.sample(list(zip(population, fitnesses)), k=min(size, len(population)))
        participants.sort(key=lambda x: x[1], reverse=True)
        return participants[0][0]

    def _crossover(self, p1: List[int], p2: List[int], rng: random.Random, strategy: str, rate: float) -> Tuple[List[int], List[int]]:
        if rng.random() > rate:
            return p1[:], p2[:]
        if strategy == "uniform":
            child1 = [p1[i] if rng.random() < 0.5 else p2[i] for i in range(len(p1))]
            child2 = [p2[i] if rng.random() < 0.5 else p1[i] for i in range(len(p1))]
            return child1, child2
        # single-point crossover (baseline)
        point = rng.randint(1, len(p1) - 2)
        return p1[:point] + p2[point:], p2[:point] + p1[point:]

    def _mutate(self, ind: List[int], rng: random.Random, rate: float, strategy: str, stagnation: int) -> List[int]:
        effective_rate = rate
        if strategy == "adaptive":
            effective_rate = min(0.35, rate * (1 + 0.2 * stagnation))
        return [1 - gene if rng.random() < effective_rate else gene for gene in ind]

    def _initial_population(self, n: int, items: List[Dict[str, Any]], rng: random.Random) -> List[List[int]]:
        population = []
        median_valor = np.median([i["valor_estimado_k"] for i in items]) if items else 0.0
        bias_prob = 0.5
        for _ in range(n):
            individual = []
            for item in items:
                base_prob = 0.35 if item["valor_estimado_k"] < median_valor else 0.55
                individual.append(1 if rng.random() < (base_prob * bias_prob) else 0)
            population.append(individual)
        return population

    def _run_ga(
        self,
        items: List[Dict[str, Any]],
        scenario_key: str,
        scenario: Dict[str, Any],
        params: GeneticParams,
    ) -> Dict[str, Any]:
        rng = random.Random(params.seed)
        population = self._initial_population(params.population_size, items, rng)
        best = None
        history: List[Dict[str, Any]] = []
        stagnation = 0
        start = time.time()

        for gen in range(params.generations):
            evaluations = [self._evaluate(ind, items, scenario) for ind in population]
            fitnesses = [e["fitness"] for e in evaluations]
            best_idx = int(np.argmax(fitnesses))
            generation_best = evaluations[best_idx]

            if not best or generation_best["fitness"] > best["fitness"]:
                best = {**generation_best, "individual": population[best_idx][:], "generation": gen}
                stagnation = 0
            else:
                stagnation += 1

            history.append(
                {
                    "generation": gen,
                    "best_fitness": generation_best["fitness"],
                    "mean_fitness": round(float(np.mean(fitnesses)), 4),
                    "best_cost": generation_best["cost"],
                    "best_water": generation_best["water"],
                    "best_value": generation_best["value"],
                }
            )

            # Next generation
            new_population: List[List[int]] = []
            # Elitism - keep top individuals
            if params.elitism > 0:
                elite_indices = np.argsort(fitnesses)[-params.elitism :]
                for idx in elite_indices:
                    new_population.append(population[int(idx)][:])

            while len(new_population) < params.population_size:
                if params.strategy == "baseline":
                    parent1 = self._roulette_select(population, fitnesses, rng)
                    parent2 = self._roulette_select(population, fitnesses, rng)
                    c1, c2 = self._crossover(parent1, parent2, rng, "single", params.crossover_rate)
                    c1 = self._mutate(c1, rng, params.mutation_rate, "fixed", stagnation)
                    c2 = self._mutate(c2, rng, params.mutation_rate, "fixed", stagnation)
                else:
                    parent1 = self._tournament_select(population, fitnesses, rng, size=5)
                    parent2 = self._tournament_select(population, fitnesses, rng, size=4)
                    c1, c2 = self._crossover(parent1, parent2, rng, "uniform", params.crossover_rate)
                    c1 = self._mutate(c1, rng, params.mutation_rate, "adaptive", stagnation)
                    c2 = self._mutate(c2, rng, params.mutation_rate, "adaptive", stagnation)
                new_population.extend([c1, c2])

            population = new_population[: params.population_size]

        runtime_ms = round((time.time() - start) * 1000, 2)
        selected_items = [items[idx] for idx, g in enumerate(best["individual"]) if g]

        return {
            "scenario_key": scenario_key,
            "best": best,
            "history": history,
            "runtime_ms": runtime_ms,
            "selected_items": selected_items,
            "params": params.__dict__,
        }

    # ---------- Public API ----------
    def run_with_comparison(
        self,
        dataset: Dict[str, Any],
        scenario_key: str,
        user_params: Optional[Dict[str, Any]] = None,
        compare_all: bool = False,
    ) -> Dict[str, Any]:
        items = dataset.get("items", [])
        scenarios = self.scenario_options(dataset)
        scenario = scenarios.get(scenario_key) or list(scenarios.values())[0]
        suggestion = self.suggest_parameters(dataset)

        params_payload = {
            "population_size": user_params.get("population_size", suggestion["population_size"]) if user_params else suggestion["population_size"],
            "generations": user_params.get("generations", suggestion["generations"]) if user_params else suggestion["generations"],
            "mutation_rate": user_params.get("mutation_rate", suggestion["mutation_rate"]) if user_params else suggestion["mutation_rate"],
            "crossover_rate": user_params.get("crossover_rate", suggestion["crossover_rate"]) if user_params else suggestion["crossover_rate"],
            "elitism": user_params.get("elitism", suggestion["elitism"]) if user_params else suggestion["elitism"],
            "seed": user_params.get("seed", int(time.time())) if user_params else int(time.time()),
            "strategy": user_params.get("strategy", "elitist_adaptive") if user_params else "elitist_adaptive",
            "scenario_key": scenario_key,
        }
        params = GeneticParams(**params_payload)

        baseline_params = GeneticParams(
            population_size=params.population_size,
            generations=max(20, int(params.generations * 0.7)),
            mutation_rate=max(0.02, params.mutation_rate * 0.6),
            crossover_rate=0.8,
            elitism=max(1, params.elitism // 2),
            seed=params.seed + 5,
            strategy="baseline",
            scenario_key=scenario_key,
        )

        improved_run = self._run_ga(items, scenario_key, scenario, params)
        baseline_run = self._run_ga(items, scenario_key, scenario, baseline_params)

        comparisons = []
        if compare_all:
            for key, scen in scenarios.items():
                quick_params = GeneticParams(
                    population_size=max(30, params.population_size // 2),
                    generations=22,
                    mutation_rate=params.mutation_rate,
                    crossover_rate=params.crossover_rate,
                    elitism=max(1, params.elitism // 2),
                    seed=params.seed + hash(key) % 1000,
                    strategy="elitist_adaptive",
                    scenario_key=key,
                )
                quick_run = self._run_ga(items, key, scen, quick_params)
                comparisons.append(
                    {
                        "scenario": key,
                        "fitness": quick_run["best"]["fitness"],
                        "cost": quick_run["best"]["cost"],
                        "water": quick_run["best"]["water"],
                        "runtime_ms": quick_run["runtime_ms"],
                    }
                )

        best_improved = improved_run["best"]
        best_baseline = baseline_run["best"]
        delta_fitness = round(best_improved["fitness"] - best_baseline["fitness"], 3)
        delta_runtime = round(improved_run["runtime_ms"] - baseline_run["runtime_ms"], 2)

        return {
            "scenario": {"key": scenario_key, **scenario},
            "suggestion": suggestion,
            "dataset": self.summarize_dataset(dataset),
            "best_solution": {
                "fitness": best_improved["fitness"],
                "value": best_improved["value"],
                "cost": best_improved["cost"],
                "water": best_improved["water"],
                "generation": best_improved["generation"],
                "selected_items": improved_run["selected_items"],
            },
            "history": improved_run["history"],
            "runtime_ms": improved_run["runtime_ms"],
            "benchmark": {
                "baseline": {
                    "fitness": best_baseline["fitness"],
                    "runtime_ms": baseline_run["runtime_ms"],
                    "selection": "roulette",
                    "crossover": "single-point",
                    "mutation": "fixed bitflip",
                },
                "improved": {
                    "fitness": best_improved["fitness"],
                    "runtime_ms": improved_run["runtime_ms"],
                    "selection": "tournament+elitism",
                    "crossover": "uniform",
                    "mutation": "adaptive",
                },
                "delta": {
                    "fitness_gain": delta_fitness,
                    "runtime_diff_ms": delta_runtime,
                },
            },
            "comparisons": comparisons,
            "params_used": params.__dict__,
        }
