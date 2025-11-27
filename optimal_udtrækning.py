import pandas as pd
import scipy.stats as stats
import numpy as np
import tqdm
import matplotlib.pyplot as plt
import hashlib

# Antal personer i stikprøven
sample_size = 50
# Antal iterationer i søgningen
n_iter = 5000

variables = ['Køn', 'Etnicitet', 'Uddannelse', 'Alder']


def add_row_hash(df):
    """
    Tilføjer en kolonne 'row_hash' med MD5 hash af alle kolonner som streng per række.
    """
    df = df.copy()

    # Konverter hver celle til string og lav en tuple pr række
    row_tuples = df.apply(lambda row: tuple(row.values.astype(str)), axis=1)

    # Beregn MD5 hash for hver tuple
    df['row_hash'] = row_tuples.apply(lambda x: hashlib.md5('-'.join(x).encode()).hexdigest())

    return df

def categorize_age(df_sample, df_population):
    """
    Kategoriserer df_sample['Alder'] i de aldersgrupper, der er defineret i df_population.

    Parametre:
        df_sample (pd.DataFrame): DataFrame med numerisk 'Alder' kolonne.
        df_population (pd.DataFrame): Population med 'Variabel', 'Kategori', 'Brøkdel'.

    Returnerer:
        pd.DataFrame: Kopi af df_sample med 'Alder' overskrevet med kategorier.
    """
    df_sample = df_sample.copy()

    # Filtrer population for alder
    df_age = df_population[df_population['Variabel'] == "Alder"].copy()
    age_labels = df_age['Kategori'].tolist()

    # Byg bins fra venstre grænse af hvert interval
    age_bins = []
    for cat in age_labels:
        if '+' in cat:  # sidste åben gruppe
            left = int(cat.replace('+', ''))
            age_bins.append(left)
        else:
            left = int(cat.split('-')[0])
            age_bins.append(left)
    age_bins.append(np.inf)  # øverste grænse

    # Anvend pd.cut
    df_sample['Alder'] = pd.cut(
        df_sample['Alder'],
        bins=age_bins,
        labels=age_labels,
        right=False
    )

    return df_sample

def rep_score(df_population, df_sample, variables):
    """
    Beregn samlet repræsentativitet for stikprøven.
    Variabler med mange kategorier vejer ikke tungere end variabler med få.

    Returnerer et enkelt score-tal: jo lavere, desto mere repræsentativ stikprøven.
    """
    total_score = 0.0
    for var in variables:
        # Population for variablen
        df_pop_var = df_population[df_population['Variabel'] == var].drop(columns='Variabel')

        # Stikprøve for variablen
        df_sample_var = df_sample[[var]]

        # Observerede frekvenser
        obs = df_sample_var[var].value_counts().reindex(df_pop_var['Kategori']).fillna(0).values

        # Forventede frekvenser
        n = len(df_sample_var)
        exp = df_pop_var['Brøkdel'].values * n

        # Chi² / df
        chi2, p = stats.chisquare(f_obs=obs, f_exp=exp)
        df_chi = len(obs) - 1
        total_score += chi2 / df_chi  # Normaliseret per df

    return total_score


def plot_representativitet(df_population, df_sample, variables):
    for var in variables:
        # Population og stikprøvefordeling
        df_pop_var = df_population[df_population['Variabel'] == var].drop(columns='Variabel')
        pop_freq = df_pop_var.set_index('Kategori')['Brøkdel']

        sample_counts = df_sample[var].value_counts().reindex(pop_freq.index).fillna(0)
        sample_freq = sample_counts / sample_counts.sum()  # relative frekvenser

        # Plot side-by-side
        x = np.arange(len(pop_freq))
        width = 0.35

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(x - width / 2, pop_freq.values, width, label='Population', color='skyblue')
        ax.bar(x + width / 2, sample_freq.values, width, label='Stikprøve', color='orange')

        ax.set_xticks(x)
        ax.set_xticklabels(pop_freq.index, rotation=45, ha='right')
        ax.set_ylabel('Frekvens')
        ax.set_title(f'Repræsentativitet for {var}')
        ax.legend()
        plt.tight_layout()
        plt.show()

# Indlæser populationen. Brøkdele fordelt på de forskellige kategorier
df_population = pd.read_csv('population_fordeling.csv')

# Indlæser bruttolisten
df_sample_full = pd.read_csv('tilfaeldige_personer.csv')

# Gruppeinddeler lige på alder
df_sample_full = categorize_age(df_sample_full,df_population)

# Indlæser forhåndsvalgte og vetolisten
df_always = categorize_age(pd.read_csv('forhåndsvalgte.csv'),df_population)
df_never = categorize_age(pd.read_csv('vetoliste.csv'),df_population)

# Beregner entydig identifier for hver række
df_sample_full = add_row_hash(df_sample_full)
df_always = add_row_hash(df_always)
df_never = add_row_hash(df_never)

# Fjerner "de specielle" fra bruttolisten
df_sample_full = df_sample_full[~df_sample_full['row_hash'].isin(df_never['row_hash'])].copy()
df_sample_full = df_sample_full[~df_sample_full['row_hash'].isin(df_always['row_hash'])].copy()

# Dropper hashen igen
df_sample_full.drop(columns=['row_hash'], inplace=True)
df_always.drop(columns=['row_hash'], inplace=True)
n_always = len(df_always)

best_score = np.inf
best_sample = None

for i in tqdm.tqdm(range(n_iter)):
    # Træk en tilfældig stikprøve
    df_sample = pd.concat([df_always,df_sample_full.sample(n=sample_size-n_always, replace=False)])

    # Beregn repræsentativitetsscore
    score = rep_score(df_population, df_sample, variables)

    # Gem, hvis denne stikprøve er bedre
    if score < best_score:
        best_score = score
        best_sample = df_sample.copy()

print(f"Bedste repræsentativitetsscore fundet: {best_score}")
# best_sample er nu den optimale stikprøve
best_sample.reset_index(drop=True, inplace=True)

plot_representativitet(df_population, best_sample, variables)

print(best_sample)

pass