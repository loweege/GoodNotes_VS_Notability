def standard_competition_ranking(scores):
    # Initialize a list to store the rankings
    rankings = [0] * len(scores)
    # Sort the indices based on the scores in descending order
    sorted_indices = sorted(range(len(scores)), key=lambda x: scores[x], reverse=True)
    # Initialize the rank counter
    rank = 1
    # Assign rankings
    for i in range(len(scores)):
        if i == 0:
            rankings[sorted_indices[i]] = rank
        elif scores[sorted_indices[i]] == scores[sorted_indices[i - 1]]:
            rankings[sorted_indices[i]] = rankings[sorted_indices[i - 1]]
        else:
            rank = i + 1
            rankings[sorted_indices[i]] = rank
    return rankings

# Example scores for each participant in each round
scores = [
    [3, 3, 1],  # Scores for PB1
    [4, 5, 3]   # Scores for PB2
]

# Calculate rankings for each participant
for i, participant_scores in enumerate(scores):
    participant_rankings = standard_competition_ranking(participant_scores)
    print(f"Rankings for PB{i+1}: {participant_rankings}")
