import pandas as pd

def main():
    Data = pd.read_csv('docs/krippendorf.csv') 
    numbers = Data['annotation']
    total_units = int(len(numbers) / 3)
    concordant_units = 0

    for idx in range(0, len(numbers), 3):
        if numbers[idx] == numbers[idx+1] and numbers[idx] == numbers[idx+2]:
            concordant_units += 1

    percentage_observer_agreement = concordant_units / total_units
    print('Percentage Observer Agreement: '+ str(percentage_observer_agreement))

if __name__ == '__main__':
    main()
