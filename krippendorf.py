import pandas as pd
from collections import Counter

def nominal_metric(x, y):
    return 1 if x != y else 0
def interval_metric(x,y):
    return (x-y)**2

def calculate_de(frequency_dicts, metric_fn):
    """
    Calculates the expected disagreement by chance
    :param frequency_dicts: The output of data_transforms.calculate_frequency_dicts e.g.:
        {
            unit_freqs:{ 1:2..},
            class_freqs:{ 3:4..},
            total:7
        }
    :param metric_fn metric function such as nominal_metric
    :return: De a float
    """
    De = 0
    class_freqs = frequency_dicts["class_freqs"]
    class_names = list(class_freqs.keys())
    for i, c in enumerate(class_names):
        for k in class_names:
            De += class_freqs[c] * class_freqs[k] * metric_fn(c, k)
    return De


def calculate_do(vbu_table_dict, frequency_dicts, metric_fn):
    """

    :param vbu_table_dict: Output of data_transforms.make_value_by_unit_table_dict
    :param frequency_dicts: The output of data_transforms.calculate_frequency_dicts e.g.:
        {
            unit_freqs:{ 1:2..},
            class_freqs:{ 3:4..},
            total:7
        }
    :param metric_fn: metric_fn metric function such as nominal_metric
    :return:  Do a float
    """
    Do = 0
    unit_freqs = frequency_dicts["unit_freqs"]
    unit_ids = list(unit_freqs.keys())
    for unit_id in unit_ids:
        unit_classes = list(vbu_table_dict[unit_id].keys())
        if unit_freqs[unit_id] < 2:
            pass
        else:
            weight = 1 / (unit_freqs[unit_id] - 1)
            for i, c in enumerate(unit_classes):
                for k in unit_classes:
                    Do += (
                        vbu_table_dict[unit_id][c]
                        * vbu_table_dict[unit_id][k]
                        * weight
                        * metric_fn(c, k)
                    )
    return Do


def calculate_krippendorffs_alpha(ea_table_df, metric_fn=nominal_metric):
    """

    :param ea_table_df: The Experiment/Annotator table, output from data_transforms.df_to_experiment_annotator_table
    :param metric_fn: The metric function. Defaults to nominal
    :return: Alpha, a float
    """
    vbu_table_dict = make_value_by_unit_table_dict(ea_table_df)
    frequency_dict = calculate_frequency_dicts(vbu_table_dict)
    observed_disagreement = calculate_do(
        vbu_table_dict=vbu_table_dict,
        frequency_dicts=frequency_dict,
        metric_fn=metric_fn,
    )
    expected_disagreement = calculate_de(
        frequency_dicts=frequency_dict, metric_fn=metric_fn
    )
    N = frequency_dict['total']
    alpha = 1 - (observed_disagreement / expected_disagreement)*(N-1)
    return alpha


def calculate_krippendorffs_alpha_for_df(
    df, experiment_col, annotator_col, class_col, metric_fn=nominal_metric
):
    """

        :param df: A Dataframe we wish to transform with that contains the response of an annotator to an experiment
            |    |   document_id | annotator_id   |   annotation |
            |---:|--------------:|:---------------|-------------:|
            |  0 |             1 | A              |            1 |
            |  1 |             1 | B              |            1 |
            |  2 |             1 | D              |            1 |
            |  4 |             2 | A              |            2 |
            |  5 |             2 | B              |            2 |

    :param experiment_col: The column name that contains the experiment (unit)
    :param annotator_col: The column name that identifies an annotator
    :param class_col: The column name that identifies the annotators response (class)
    :return: Alpha, a float

    """
    ea_table_df = df_to_experiment_annotator_table(
        df,
        experiment_col=experiment_col,
        annotator_col=annotator_col,
        class_col=class_col,
    )
    alpha = calculate_krippendorffs_alpha(ea_table_df=ea_table_df, metric_fn=metric_fn)
    return alpha



def df_to_experiment_annotator_table(df, experiment_col, annotator_col, class_col):
    """

    :param df: A Dataframe we wish to transform with that contains the response of an annotator to an experiment
            |    |   document_id | annotator_id   |   annotation |
            |---:|--------------:|:---------------|-------------:|
            |  0 |             1 | A              |            1 |
            |  1 |             1 | B              |            1 |
            |  2 |             1 | D              |            1 |
            |  4 |             2 | A              |            2 |
            |  5 |             2 | B              |            2 |

    :param experiment_col: The column name that contains the experiment (unit)
    :param annotator_col: The column name that identifies an annotator
    :param class_col: The column name that identifies the annotators response (class)
    :return: A dataframe indexed by annotators, with experiments as columns and the responses in the cells
            | annotator_id   |   1 |   2 |   3 |   4 |   5 |   6 |   7 |   8 |   9 |   10 |   11 |   12 |
            |:---------------|----:|----:|----:|----:|----:|----:|----:|----:|----:|-----:|-----:|-----:|
            | A              |   1 |   2 |   3 |   3 |   2 |   1 |   4 |   1 |   2 |  nan |  nan |  nan |
            | B              |   1 |   2 |   3 |   3 |   2 |   2 |   4 |   1 |   2 |    5 |  nan |    3 |
            | C              | nan |   3 |   3 |   3 |   2 |   3 |   4 |   2 |   2 |    5 |    1 |  nan |
            | D              |   1 |   2 |   3 |   3 |   2 |   4 |   4 |   1 |   2 |    5 |    1 |  nan |

    """
    return df.pivot_table(
        index=annotator_col, columns=experiment_col, values=class_col, aggfunc="first"
    )


def make_value_by_unit_table_dict(experiment_annotator_df):
    """

    :param experiment_annotator_df: A dataframe that came out of  df_to_experiment_annotator_table
    :return: A dictionary of dictionaries (e.g. a table) whose rows (first level) are experiments and columns are responses
            {1: Counter({1.0: 1}),
             2: Counter(),
             3: Counter({2.0: 2}),
             4: Counter({1.0: 2}),
             5: Counter({3.0: 2}),
            """
    data_by_exp = experiment_annotator_df.T.sort_index(axis=1).sort_index()
    table_dict = {}
    for exp, row in data_by_exp.iterrows():
        vals = row.dropna().values
        table_dict[exp] = Counter()
        for val in vals:
            table_dict[exp][val] += 1
    return table_dict


def calculate_frequency_dicts(vbu_table_dict):
    """

    :param vbu_table_dict: A value by unit table dictionary, the output of  make_value_by_unit_table_dict
    :return: A dictionary of dictonaries
        {
            unit_freqs:{ 1:2..},
            class_freqs:{ 3:4..},
            total:7
        }
    """
    vbu_df = (
        pd.DataFrame.from_dict(vbu_table_dict, orient="index")
        .T.sort_index(axis=0)
        .sort_index(axis=1)
        .fillna(0)
    )
    ubv_df = vbu_df.T
    vbu_df_masked = ubv_df.mask(ubv_df.sum(1) == 1, other=0).T
    return dict(
        unit_freqs=vbu_df_masked.sum().to_dict(),
        class_freqs=vbu_df_masked.sum(1).to_dict(),
        total=vbu_df_masked.sum().sum(),
    )

'''
use 1.0 as sad 2.0 as normal and 3.0 as happy
'''
def main():
    Data = pd.read_csv('krippendorf.csv') #Load Your Dataframe
    Data.head()

    result = calculate_krippendorffs_alpha_for_df(Data,experiment_col='document_id',
                                                    annotator_col='annotator_id',
                                                    class_col='annotation')
    
    print(result)
    
if __name__ == '__main__':
    main()