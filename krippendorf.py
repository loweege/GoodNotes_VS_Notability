import pandas as pd
import simpledorff

def main():
    Data = pd.read_csv('docs/krippendorf.csv')
    Data.head()

    result = simpledorff.calculate_krippendorffs_alpha_for_df(
                                                    Data,
                                                    experiment_col='document_id',
                                                    annotator_col='annotator_id',
                                                    class_col='annotation')

    print('Krippendorf-alpha: ' + str(result))    

if __name__ == '__main__':
    main()