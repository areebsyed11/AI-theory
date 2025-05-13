import random

tasks = [5, 8, 4, 7, 6, 3, 9]

facilities = {
    1: {"capacity": 24, "costs": [10, 15, 8, 12, 14, 9, 11]},
    2: {"capacity": 30, "costs": [12, 14, 9, 10, 13, 8, 12]},
    3: {"capacity": 28, "costs": [9, 16, 7, 13, 12, 10, 13]}
}

POP_SIZE = 6
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.2
GENERATIONS = 100

def fitness(chromosome):
    total_cost = 0
    facility_time = {1: 0, 2: 0, 3: 0}
    facility_cost = {1: 0, 2: 0, 3: 0}
    
    for task_idx, facility in enumerate(chromosome):
        task_time = tasks[task_idx]
        task_cost = facilities[facility]["costs"][task_idx]
        facility_time[facility] += task_time
        facility_cost[facility] += task_time * task_cost
    
    penalty = 0
    for fac in [1, 2, 3]:
        if facility_time[fac] > facilities[fac]["capacity"]:
            penalty += 1e6
    
    total_cost = sum(facility_cost.values()) + penalty
    return total_cost

def roulette_selection(population):
    fitnesses = [1 / fitness(chrom) for chrom in population]
    total = sum(fitnesses)
    pick = random.uniform(0, total)
    current = 0
    for i, chrom in enumerate(population):
        current += fitnesses[i]
        if current > pick:
            return chrom

def crossover(parent1, parent2):
    if random.random() < CROSSOVER_RATE:
        point = random.randint(1, len(tasks) - 1)
        child = parent1[:point] + parent2[point:]
        return child
    return parent1

def mutate(chromosome):
    if random.random() < MUTATION_RATE:
        i, j = random.sample(range(len(tasks)), 2)
        chromosome[i], chromosome[j] = chromosome[j], chromosome[i]
    return chromosome

def genetic_algorithm():
    population = [[random.randint(1, 3) for _ in tasks] for _ in range(POP_SIZE)]
    
    for _ in range(GENERATIONS):
        new_population = []
        for _ in range(POP_SIZE):
            parent1 = roulette_selection(population)
            parent2 = roulette_selection(population)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)
        population = new_population
    
    best_chromosome = min(population, key=fitness)
    return best_chromosome, fitness(best_chromosome)

best_solution, cost = genetic_algorithm()
print(" Best Assignment :", best_solution)
print("   Total Cost    :", cost)