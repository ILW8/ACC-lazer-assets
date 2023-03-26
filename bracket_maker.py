import csv
import json
from collections import defaultdict
from pprint import pprint


class User:
    def __init__(self, user_name, user_id):
        self.user_name = user_name
        self.user_id = user_id

    def __str__(self):
        return f"{self.user_name} ({self.user_id})"

    def __repr__(self):
        return f"{self.user_name} ({self.user_id})"


class Team:
    def __init__(self, team_name: str, team_members: list, team_acronym=None):
        self.team_name: str = team_name
        self.team_members: list[User] = team_members
        self.team_acronym = team_acronym  # will normalize `None`s later

    def __str__(self):
        return f"{self.team_name} ({self.team_acronym}) [{', '.join(str(tm) for tm in self.team_members)}]"


class Teams:
    def __init__(self, teams=None):
        self.teams: list[Team] = teams if teams is not None else list()
        self.acronyms = dict()
        self.populate_team_acronyms()

    def __repr__(self):
        return f"[{', '.join([str(team) for team in self.teams])}]"

    def add_team(self, team: Team):
        self.teams.append(team)

    def populate_team_acronyms(self):
        for team in self.teams:
            if team.team_acronym is not None:
                self.acronyms[team.team_acronym] = team
                continue

            if len(team.team_name.split()) > 1:
                # generate acronym using first letter of each word
                tentative_acronym = "".join([word[0] for word in team.team_name.split()])
                if tentative_acronym in self.acronyms:
                    # pad with number until unique
                    counter = 0
                    new_acronym = tentative_acronym
                    while new_acronym in self.acronyms:
                        new_acronym = f"{tentative_acronym}{counter}"
                    tentative_acronym = new_acronym
                team.team_acronym = tentative_acronym
                self.acronyms[tentative_acronym] = team
                continue
            # else generate using first n letters
            # TODO: finish this
        pass


def build_bracket(teams: Teams):
    pass


def print_teams_json(teams: Teams):
    template = {
        "FullName":        "a",
        "FlagName":        "",
        "Acronym":         "",
        "SeedingResults":  [],
        "Seed":            "1",
        "LastYearPlacing": 1,
        "Players":         [
            {
                "id": 12344,
            }
        ]
    }
    output_list = list()
    for team in teams.teams:
        team_json = template.copy()
        team_json["FullName"] = team.team_name
        team_json["Players"] = [{"id": tm.user_id} for tm in team.team_members]
        output_list.append(team_json)
    print(json.dumps(output_list))


MATCH_TEMPLATE = {
    "ID":                 1,
    "Team1Score":         None,
    "Team2Score":         None,
    "Completed":          False,
    "Losers":             False,
    "PicksBans":          [],
    "Current":            False,
    "Date":               "2023-03-26T05:42:36.527195+01:00",
    "ConditionalMatches": [],
    "Position":           {
        "X": 196,
        "Y": 209
    },
    "Acronyms":           []
}

# noinspection PyStatementEffect
{
    "Matches": [
        {
            "ID":                 1,
            "Team1Score":         None,
            "Team2Score":         None,
            "Completed":          False,
            "Losers":             False,
            "PicksBans":          [],
            "Current":            False,
            "Date":               "2023-03-26T05:42:36.527195+01:00",
            "ConditionalMatches": [],
            "Position":           {
                "X": 196,
                "Y": 209
            },
            "Acronyms":           []
        },
        {
            "ID":                 3,
            "Team1Score":         None,
            "Team2Score":         None,
            "Completed":          False,
            "Losers":             False,
            "PicksBans":          [],
            "Current":            False,
            "Date":               "2023-03-26T05:42:37.404566+01:00",
            "ConditionalMatches": [],
            "Position":           {
                "X": 196,
                "Y": 360
            },
            "Acronyms":           []
        },
        {
            "ID":                 2,
            "Team1Score":         None,
            "Team2Score":         None,
            "Completed":          False,
            "Losers":             False,
            "PicksBans":          [],
            "Current":            False,
            "Date":               "2023-03-26T05:42:38.002846+01:00",
            "ConditionalMatches": [],
            "Position":           {
                "X": 556,
                "Y": 292
            },
            "Acronyms":           []
        },
        {
            "ID":                 4,
            "Team1Score":         None,
            "Team2Score":         None,
            "Completed":          False,
            "Losers":             False,
            "PicksBans":          [],
            "Current":            False,
            "Date":               "2023-03-26T05:42:38.814613+01:00",
            "ConditionalMatches": [],
            "Position":           {
                "X": 557,
                "Y": 532
            },
            "Acronyms":           []
        }
    ],
}

PROGRESSION_TEMPLATE = {
    "SourceID": 3,
    "TargetID": 4,
    "Losers":   True
}
# noinspection PyStatementEffect
{
    "Progressions": [
        {
            "SourceID": 1,
            "TargetID": 2
        },
        {
            "SourceID": 3,
            "TargetID": 2
        },
        {
            "SourceID": 1,
            "TargetID": 4,
            "Losers":   True
        },
        {
            "SourceID": 3,
            "TargetID": 4,
            "Losers":   True
        }
    ],
}


def print_bracket(max_round_of: int):
    if (max_round_of & (max_round_of - 1) != 0) and max_round_of != 0 or max_round_of <= 0:
        # not a power of 2
        print(f"{max_round_of} not a power of 2")

    matches_structure = defaultdict(lambda: defaultdict(list))  # helper for building connections
    matches = list()

    stage = 0
    stage_lb = stage
    num_matches = max_round_of // 2
    match_id = 0
    match_block_offset_y = 96
    match_block_offset_x = 256
    winner_y_offset = 64
    losers_y_offset = max_round_of * 48 + 128
    losers_x_offset = (match_block_offset_x * 3) // 4
    while num_matches > 0:
        # let n be the number of starting matches,
        # there are n/2 losers bracket matches
        # there are n/2 winners bracket matches on the next stage
        for match_block_index in range(num_matches):
            match_id += 1
            # print(f"{match_id:>02} WB stage {stage}")
            match = MATCH_TEMPLATE.copy()
            match["id"] = match_id
            match["Position"] = {
                "X": stage * (match_block_offset_x * (2 if stage > 1 else 1)) - (match_block_offset_x * (stage > 1)),
                "Y": winner_y_offset + match_block_index * match_block_offset_y * (stage * 2 if stage > 0 else 1) +
                int(max(0, stage - 0.5) * match_block_offset_y)
            }
            # print(f"{match_id:>02} WB stage {stage}: {match['Position']}")

            matches.append(match)
            matches_structure[stage]["WB"].append(match_id)

        lb_first_half_count = (1 if stage % 3 == 0 else 2) * num_matches // 2
        should_add_another_lb_stage = stage % 3 != 0

        for match_block_index in range(lb_first_half_count
                                       + (0 if not should_add_another_lb_stage else num_matches // 2)):
            match_id += 1
            is_second_half_lb = 0 if match_block_index < lb_first_half_count else 1

            match = MATCH_TEMPLATE.copy()
            match["id"] = match_id

            num_step = match_block_index if not is_second_half_lb else match_block_index - lb_first_half_count
            y_step_size = match_block_offset_y * ((2 * stage // 2) + is_second_half_lb if stage > 0 else 1)
            ladder_inset_offset = int(max(0, (2 * is_second_half_lb + stage) // 2 - 0.5) * match_block_offset_y)
            y = losers_y_offset + num_step * y_step_size + ladder_inset_offset
            match["Position"] = {
                "X": losers_x_offset +
                     (stage_lb + (1 if match_block_index >= lb_first_half_count else 0)) * match_block_offset_x,
                "Y": y
            }
            matches_structure[stage][f"LB{0 if match_block_index < lb_first_half_count else 1}"].append(match_id)

            # print(f"{match_id:>02} LB stage {stage} "
            #       f"({0 if match_block_index < lb_first_half_count else 1}): {match['Position']}")

            matches.append(match)
        if should_add_another_lb_stage:
            stage_lb += 1

        num_matches //= 2
        stage += 1
        stage_lb += 1
    print("Copy paste into `bracket.json`'s `Matches` key:")
    print(json.dumps(matches))
    print()

    # create Progressions
    # print(json.dumps(matches_structure))
    progressions = list()
    for stage, matches_sets in matches_structure.items():
        if not stage:
            continue

        # print(stage, matches_sets)
        # print(f"Link matches from {matches_structure[stage - 1]['WB']} to {matches_sets['WB']}")
        for matchset_index, match_id in enumerate(matches_structure[stage - 1]['WB']):
            # do WB

            progression = {
                "SourceID": match_id,
                "TargetID": matches_sets['WB'][matchset_index // 2],
                "Losers":   False,
            }
            progressions.append(progression)

            # do WB to LB
            progression = {
                "SourceID": match_id,
                "TargetID": matches_structure[stage - 1]['LB0'][matchset_index // (1 if stage > 1 else 2)],
                "Losers":   True,
            }
            progressions.append(progression)

        # intra-stage LB progressions
        if "LB1" in matches_sets:
            for matchset_index, match_id in enumerate(matches_sets["LB0"]):
                progression = {
                    "SourceID": match_id,
                    "TargetID": matches_sets['LB1'][matchset_index // 2],
                    "Losers":   False,
                }
                progressions.append(progression)

        # inter-stage LB progressions
        prev_stage_source = "LB1" if "LB1" in matches_structure[stage - 1] else "LB0"
        # for matchset_index, match_id in enumerate(matches_structure[stage - 1][prev_stage_source]):
        for matchset_index, match_id in enumerate(matches_sets["LB0"]):
            progression = {
                "SourceID": matches_structure[stage - 1][prev_stage_source][matchset_index],
                "TargetID": match_id,
                "Losers":   False,
            }
            progressions.append(progression)

    print("Copy paste into `bracket.json`'s `Progressions` key:")
    print(json.dumps(progressions))


def main():
    # parse team list
    data = defaultdict(lambda: defaultdict(list))  # key: team name, value: team data

    with open("./ACC Waiter - Teams.csv", "r") as infile:
        csv_reader = csv.reader(infile)
        for row in csv_reader:
            try:
                user_id = int(row[5])
                user_name = row[6]
                team_name = row[8]
                user = User(user_name, user_id)
                data[team_name]["user_name"].append(user)
            except ValueError:
                pass  # probably table header
    # pprint(data)

    teams = Teams()
    for team_name, team_data in data.items():
        teams.add_team(Team(team_name, team_data["user_name"]))
    teams.populate_team_acronyms()

    # print(teams)
    print_teams_json(teams)


if __name__ == "__main__":
    # main()
    print_bracket(16)
