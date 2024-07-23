def standard_competition_ranking(scores):
    rankings = [0] * len(scores)
    sorted_indices = sorted(range(len(scores)), key=lambda x: scores[x], reverse=True)
    rank = 1
    for i in range(len(scores)):
        if i == 0:
            rankings[sorted_indices[i]] = rank
        elif scores[sorted_indices[i]] == scores[sorted_indices[i - 1]]:
            rankings[sorted_indices[i]] = rankings[sorted_indices[i - 1]]
        else:
            rank = i + 1
            rankings[sorted_indices[i]] = rank
    return rankings


def main():
    # Example scores for each participant in each round
    scores = [
        [3, 3, 1], 
        [4, 5, 3] 
    ]

    for i, participant_scores in enumerate(scores):
        participant_rankings = standard_competition_ranking(participant_scores)
        print(f"Rankings for PB{i+1}: {participant_rankings}")

if __name__ == '__main__':
    main()
