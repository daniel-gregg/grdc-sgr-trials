## Generate performance comparisons of system categories to baselines at a site level

# base imports
from pyprojroot.here import here
import sys
import os
import pandas as pd
import numpy as np
import datetime

#append path using 'here'
path_root = here()
sys.path.append(str(path_root))

from src.utils.base_paths import get_gross_margin_data_path
from src.utils.base_paths import get_reference_data_path
from src.utils.base_paths import get_system_baseline_comparisons_path

def get_systems_mapping(site = None):
    # identifies baseline system IDs for each site (or for the project as a whole)
    id_systems_mapping = pd.read_csv(get_reference_data_path("plotSystemMapping.csv"))

    if not site:
        return id_systems_mapping

    else:
        # use the 'site' column to subset the data and return that
        subdat = id_systems_mapping[id_systems_mapping['site'] == site.upper()]
        if subdat.empty:
            print(f'Warning: no systems mapping data found for site {site}. Returning full mapping data.')
            return id_systems_mapping
        return subdat

def get_baseline_systems_ids(site = None):

    systems_mapping_data = get_systems_mapping(site)

    # loop through each row and check if 'baseline' is included in the system category string
    sites = systems_mapping_data['site'].unique().tolist()
    baseline_ids = {site: [] for site in sites}
    if site:
        baseline_ids = {site: [row['plot'] for index, row in systems_mapping_data.iterrows() if 'baseline' in row['system_category'].lower()]}
    else:
        for site in sites:
            baseline_ids[site] = [row['plot'] for index, row in systems_mapping_data.iterrows() if 'baseline' in row['system_category'].lower()]

    return baseline_ids

def get_gross_margin_data():
    # returns the latest gross margin data as a daraframe
    # gross margin file has dirs dated by processing date. List these:
    gross_margin_dated_dirs = os.listdir(get_gross_margin_data_path())
    # then get the latest run
    latest_dir = max(gross_margin_dated_dirs, key=lambda x: os.path.getctime(os.path.join(get_gross_margin_data_path(), x)))

    # get the latest processed file in that dir (this is based on the latest processed data)
    gm_dirpath = os.path.join(get_gross_margin_data_path(), latest_dir)
    gm_files = os.listdir(gm_dirpath)

    latest_file = max(gm_files, key=lambda x: os.path.getctime(os.path.join(gm_dirpath, x)))
    gm_data = pd.read_csv(os.path.join(gm_dirpath, latest_file))
    return gm_data

def get_system_category_for_non_baseline_plots(site = None):
    systems_mapping_data = get_systems_mapping(site)
    non_baseline_mapping = systems_mapping_data[~systems_mapping_data['system_category'].str.lower().str.contains('baseline')]

    # loop through sites and categories to create a nested dict with site->category->[list of ids]
    if not site:
        sites = non_baseline_mapping['site'].unique().tolist()
        plots_in_category = {}
        for site in sites:
            site_data = non_baseline_mapping[non_baseline_mapping['site'] == site]
            categories = site_data['system_category'].unique().tolist()
            plots_in_category[site] = {}
            for category in categories:
                plots_in_category[site][category] = site_data[site_data['system_category'] == category]['plot'].tolist()
        return plots_in_category
    else:
        categories = non_baseline_mapping['system_category'].unique().tolist()
        plots_in_category = {}
        for category in categories:
            plots_in_category[category] = non_baseline_mapping[non_baseline_mapping['system_category'] == category]['plot'].tolist()
        return {site: plots_in_category}

def get_comparisons(site = None):
    ##  NEED TO DO:
    #   1. make sure baseline ids are a dict by site not a basic list
    #   2. make comparisons by phase, not across phases - accounts for common year effects in the loop below

    ### Read in data ###
    baseline_ids = get_baseline_systems_ids(site)
    gross_margin_data = get_gross_margin_data()
    site_systems_dict = get_system_category_for_non_baseline_plots(site)
    if site:
        sites = [site]
    else:
        sites = gross_margin_data['site'].unique().tolist()

    # create a separate series of gross margin observations for each system type as a dictionary
    # keys are system category names
    # values are lists of gross margin observations for that system type
    # these are nested in a dictionary with site as the top level key
    # these are system categories for non-baseline systems ONLY

    # Start with creating a dict of gross margin data for baseline and non baseline systems by site
    baseline_data_by_site = {}
    non_baseline_data_by_site = {}
    for site_name in sites:
        site_data = gross_margin_data[gross_margin_data['site'] == site_name]
        baseline_data_by_site[site_name] = site_data[site_data['plot'].isin(baseline_ids[site_name.upper()])]
        non_baseline_data_by_site[site_name] = site_data[site_data['plot'].isin(baseline_ids[site_name.upper()])]
        non_baseline_categories = site_systems_dict[site_name.upper()].keys()
        site_category_dict = {category: [] for category in non_baseline_categories}
        for category_name in non_baseline_categories:
            category_plot_ids = site_systems_dict[site_name.upper()][category_name]
            site_category_data = site_data[site_data['plot'].isin(category_plot_ids)]
            site_category_dict[category_name] = site_category_data
        non_baseline_data_by_site[site_name] = site_category_dict

    # then loop through sites and system categories to get gross margin data for each system category
    gm_diffs_by_site_and_system_category = {site: {} for site in sites}

    for site_name in sites:
        site_baseline_data = baseline_data_by_site[site_name]
        site_categories = site_systems_dict[site_name.upper()].keys()
        gm_diffs_categories_dict = {category: [] for category in site_categories}
        for category in site_categories:
            site_system_data = non_baseline_data_by_site[site_name][category]
            years = site_system_data['year'].unique().tolist()
            for year in years:
                site_category_year_data = site_system_data[site_system_data['year'] == year]
                baseline_site_year_data = site_baseline_data[site_baseline_data['year'] == year]

                ids_in_category_year = site_category_year_data['plot'].unique().tolist()
                ids_in_baseline_year = baseline_site_year_data['plot'].unique().tolist()

                for cat_id in ids_in_category_year:
                    cat_id_data = site_category_year_data[site_category_year_data['plot'] == cat_id]
                    cat_id_gm_data = cat_id_data['gross_margin'].tolist()
                    for base_id in ids_in_baseline_year:
                        base_id_data = baseline_site_year_data[baseline_site_year_data['plot'] == base_id]
                        base_id_gm_data = base_id_data['gross_margin'].tolist()

                        # form the difference for each combination of system and baseline observations
                        for cat_gm in cat_id_gm_data:
                            for base_gm in base_id_gm_data:
                                gm_diffs_categories_dict[category].append(cat_gm - base_gm)

                # form the difference for each combination of system and baseline observations

            gm_differences = []
            for baseline_obs in site_baseline_gm_data:
                for system_obs in site_category_gm_data:
                    gm_differences.append(system_obs - baseline_obs)
            gm_diffs_by_site_and_system_category[site.upper()][category] = gm_differences
    return gm_diffs_by_site_and_system_category

# generate summary statistics and identify significant differences
def summarise_comparisons(gm_differences_by_site_and_system_category):

    sig_differences = pd.DataFrame(
        columns=['site', 'system_category', 'mean_difference', 'prob>0', 'count', 'significantly_better_than_baseline']
    )
    for site, categories in gm_differences_by_site_and_system_category.items():
        for category, differences in categories.items():
            mean_diff = np.mean(differences)
            std_dev = np.std(differences)
            n = len(differences)
            # calculate probability that mean difference is greater than 0

            prob_greater_than_zero = len([diffs for diffs in gm_differences_by_site_and_system_category[site][category] if diffs > 0]) / n
            if std_dev == 0 or n == 0:
                pval_zscore = np.nan
            else:
                se = std_dev / np.sqrt(n)
                z_score = mean_diff / se
                pval_zscore = 1 - (0.5 * (1 + np.math.erf(z_score / np.sqrt(2))))

            significantly_better = pval_zscore > 0.95

            sig_differences = sig_differences.append({
                'site': site,
                'system_category': category,
                'mean_difference': mean_diff,
                'prob>0': prob_greater_than_zero,
                'count': n,
                'pval_zscore': pval_zscore,
                'significantly_better_than_baseline': significantly_better
            }, ignore_index=True)

    # write
    return sig_differences

def gen_system_baseline_comparison_results(site = None):
    results_df = summarise_comparisons(get_comparisons(site))
    today_date = datetime.datetime.now().strftime("%Y%m%d")
    if site:
        filename = f'system_baseline_comparisons_{site}_{today_date}.csv'
        results_df.to_csv(os.path.join(get_system_baseline_comparisons_path(), filename), index=False)
    else:
        for site in results_df['site'].unique():
            site_results_df = results_df[results_df['site'] == site]
            filename = f'system_baseline_comparisons_{site}_{today_date}.csv'
            site_results_df.to_csv(os.path.join(get_system_baseline_comparisons_path(), filename), index=False)
        filename = f'system_baseline_comparisons_all_sites_{today_date}.csv'
        results_df.to_csv(os.path.join(get_system_baseline_comparisons_path(), filename), index=False)
