from ranking import Ranking
import csv

def print_stats(debugmode, 
                cases_number, 
                items, 
                margins, 
                ranking, 
                means, 
                victories, 
                logfile, 
                singlelog):
    
    summary = ''

    if debugmode:
        print(singlelog)
    logfile += singlelog

    singlelog = "Cases processed: %d \n" % cases_number
    
    if debugmode:
        print(singlelog)
    logfile += singlelog
    summary += singlelog 
    singlelog = "Items: " + str(items) + '\n' + 'Final Ranking: ' + str(ranking) + '\n' + 'Mean rankings: ' + str(means) + '\n'
    if debugmode:
        print(singlelog)
    logfile += singlelog
    summary += singlelog    

    singlelog = 'Cumulated Margins: ' + str(margins) + '\n'
    if debugmode:
        print(singlelog)
    logfile += singlelog
    summary += singlelog

    singlelog = 'Final Number of victories: ' + str(victories) 
    if debugmode:
        print(singlelog)
    logfile += singlelog
    summary += singlelog

    print('--------------------------General-info--------------------------------------')
    print(summary)
    print('----------------------------------------------------------------------------')

def priority_bands_computation(
                debugmode, 
                scores, 
                unsorted_scores, 
                evaluation_number, 
                victories, 
                margins, 
                logfile, 
                ranking, 
                item_number, 
                outputfile, 
                rows, 
                podium, 
                max_rank):
    
    priority_bands = [[0, 0] for _ in range(item_number)]

    # row --> scores given by an evaluator for all the problems
    for row in scores:
            singlelog = "About to process row no. %d , that is: %s \n" % (rows, row)
            if debugmode:
                print(singlelog)
            logfile += singlelog
            
            # Ensure unsorted_scores has enough elements to store scores for this row
            if len(unsorted_scores) < len(row):
                unsorted_scores.extend([0] * (len(row) - len(unsorted_scores)))
                
            for i, elem in enumerate(row):
                if elem != '' and elem != '.':
                    unsorted_scores[i] = int(elem)
                    evaluation_number[i] += 1
                    for k, secondelem in enumerate(row):
                        if secondelem != '' and secondelem != '.':
                            if i != k:
                                margin = int(elem) - int(secondelem)
                                if margin > 0:
                                    victories[i] += 1
                                margins[i] += margin
                else:
                    unsorted_scores[i] = None

            singlelog = '====Evaluations: ' + str(unsorted_scores) + '=======\n'
            if debugmode:
                print(singlelog)
            logfile += singlelog
            input_sorted = sorted([score for score in unsorted_scores if score is not None], reverse=True)
            singlelog = 'Ordered evaluations: ' + str(input_sorted) + '\n'
            if debugmode:
                print(singlelog)
            logfile += singlelog

            partial_ranking = {}
            for rank, score in Ranking(input_sorted, no_score=''):
                singlelog = 'rank: %s, score %s \n' % (rank, score)
                if debugmode:
                    print(singlelog)
                logfile += singlelog
                if rank is not None:
                    partial_ranking[score] = rank + 1
                else:
                    partial_ranking[score] = 0

            singlelog = 'Partial ranking: ' + str(partial_ranking) + '\n'
            if debugmode:
                print(singlelog)
            logfile += singlelog
            singlelog = 'Old ranking: ' + str(ranking) + '\n'
            if debugmode:
                print(singlelog)
            logfile += singlelog
            newrow = ''
            for var in range(item_number):
                valutation = unsorted_scores[var]
                if valutation in partial_ranking:
                    if valutation is not None:
                        pos = partial_ranking[valutation]
                        ranking[var] += pos
                        singlelog = 'New position: ' + str(pos) + '(' + str((var + 1)) + 'a)' + '\n'
                        if debugmode:
                            print(singlelog)
                        logfile += singlelog
                        newrow += str(pos) + ','
                        if pos <= max_rank:
                            podium[var][pos - 1] += 1
                            priority_bands[var][0] += 1
                        else:
                            priority_bands[var][1] += 1
                    else:
                        newrow += ','
                else:
                    newrow += ','
            singlelog = 'New ranking: ' + str(ranking) + '\n'
            if debugmode:
                print(singlelog)
            logfile += singlelog
            newrow = newrow.strip(',')
            outputfile += newrow + '\n'
            rows += 1

    return priority_bands

def main():
    ranking = [0]
    unsorted_scores = [0]
    evaluation_number = [0]
    means = [0.00]
    singlelog = ''
    outputfile = ''
    newrow = ''
    logfile = ''
    rows = 0
    filename = 'na_matrix.csv'
    
    item_number = 0

    with open(filename, 'r') as csvfile:
        scores = csv.reader(csvfile, delimiter=',', quotechar='|')
        items = next(scores)
        item_number = len(items)
        for elem in items:
            word = str(elem)
            outputfile += word.strip(' []\'\"') + ','
        outputfile = outputfile.strip(',') + '\n'

        for _ in range(item_number - 1):
            ranking.append(0)
            unsorted_scores.append(0)
            means.append(0.00)
            evaluation_number.append(0)     

        # Define podium based on maximum rank
        max_rank = 3  
        podium = [[0 for _ in range(max_rank)] for _ in range(item_number)]
        victories = [0 for _ in range(item_number)]
        margins = [0 for _ in range(item_number)]

        priority_bands = priority_bands_computation(
                False,
                scores, 
                unsorted_scores, 
                evaluation_number, 
                victories, 
                margins, 
                logfile, 
                ranking, 
                item_number, 
                outputfile, 
                rows, 
                podium, 
                max_rank)

    cases_number = rows
    
    for i in range(item_number):
        if evaluation_number[i] != 0:
            means[i] = round((ranking[i] / evaluation_number[i]), 2)

    print_stats(False, cases_number, items, margins, ranking, means, victories, logfile, singlelog)

    results = '\nPodium: ' + str(podium) + '\n' + 'Priority bands distribution: ' + str(priority_bands) + '\n'
    print(results)

if __name__ == "__main__":
    main()
