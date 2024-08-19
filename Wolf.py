import random
import os

class Player:
    def __init__(self, name, role, is_human):
        self.name = name
        self.role = role
        self.is_human = is_human
        self.alive = True
        self.checked_players = []

    def __str__(self):
        return f"{self.name} - {'真人' if self.is_human else '人机'} - {'存活' if self.alive else '死亡'}"

def assign_roles(players):
    roles = ['狼人', '狼人', '平民', '平民', '预言家', '女巫']
    
    # 根据玩家数量增加平民角色
    if len(players) > len(roles):
        roles += ['平民'] * (len(players) - len(roles))

    random.shuffle(roles)
    for i in range(len(players)):
        players[i].role = roles[i]

def display_roles(players):
    for player in players:
        if player.is_human:
            input(f"按Enter键查看{player.name}的身份...")
            print(f"{player.name}, 你的身份是: {player.role}")
            input("按Enter键继续...")
            os.system("clear")

def werewolves_act(players):
    werewolves = [p for p in players if p.alive and p.role == '狼人']
    targets = [p for p in players if p.alive and p.role != '狼人']

    if not werewolves:
        return None

    print("狼人们，请讨论并选择一个玩家进行攻击...")
    if any(w.is_human for w in werewolves):
        victim_name = input("输入要攻击的玩家名字: ").strip()
        if victim_name in [p.name for p in targets]:
            victim = next(p for p in targets if p.name == victim_name)
        else:
            print(f"{victim_name} 不是一个有效目标。")
            return werewolves_act(players)
    else:
        victim = random.choice(targets)

    print(f"狼人攻击了 {victim.name}!")
    return victim

def witch_act(players, werewolf_victim):
    witches = [p for p in players if p.alive and p.role == '女巫']

    if not witches:
        return

    for witch in witches:
        if witch.is_human:
            heal_choice = input(f"{witch.name}, 你要救 {werewolf_victim.name} 吗? (Y/N): ").strip().upper()
            if heal_choice == 'Y':
                werewolf_victim = None  # 女巫救人
                print(f"{witch.name} 决定救 {werewolf_victim.name}。")
            else:
                print(f"{witch.name} 决定不救 {werewolf_victim.name}。")

            poison_choice = input(f"{witch.name}, 你要毒人吗? (Y/N): ").strip().upper()
            if poison_choice == 'Y':
                poison_target_name = input("输入要毒的玩家名字: ").strip()
                poison_target = next((p for p in players if p.name == poison_target_name and p.alive), None)
                if poison_target:
                    print(f"{witch.name} 毒死了 {poison_target.name}。")
                    poison_target.alive = False
                else:
                    print(f"{poison_target_name} 不是一个有效目标。")
        else:
            if random.choice([True, False]):
                werewolf_victim = None  # AI女巫救人
            if random.choice([True, False]):
                poison_target = random.choice([p for p in players if p.alive and p != werewolf_victim])
                poison_target.alive = False
                print(f"AI女巫毒死了 {poison_target.name}。")

    return werewolf_victim

def seer_act(players):
    seers = [p for p in players if p.alive and p.role == '预言家']

    if not seers:
        return

    for seer in seers:
        if seer.is_human:
            check_target_name = input(f"{seer.name}, 输入你要查验的玩家名字: ").strip()
            check_target = next((p for p in players if p.name == check_target_name), None)
            if check_target:
                seer.checked_players.append((check_target.name, check_target.role))
                print(f"{seer.name} 查验了 {check_target.name}，他们是 {check_target.role}。")
            else:
                print(f"{check_target_name} 不是一个有效目标。")
        else:
            check_target = random.choice([p for p in players if p != seer])
            seer.checked_players.append((check_target.name, check_target.role))
            print(f"AI预言家查验了 {check_target.name}，他们是 {check_target.role}。")

def villagers_vote(players):
    if not [p for p in players if p.alive]:
        return

    print("村民们，现在开始投票！")
    votes = {}

    # 投票过程按顺序进行，真人玩家先投票
    for player in players:
        if player.alive:
            if player.is_human:
                vote = input(f"{player.name}, 你投票淘汰谁? ").strip()
                if vote in [p.name for p in players if p.alive and p.name != player.name]:
                    votes[vote] = votes.get(vote, 0) + 1
                else:
                    print(f"{vote} 不是一个有效目标。")
                    continue
            else:
                # AI投票逻辑
                possible_votes = [p.name for p in players if p.alive and p.name != player.name]
                vote = random.choice(possible_votes)
                votes[vote] = votes.get(vote, 0) + 1
                print(f"{player.name}: {vote}")

    # 显示投票结果
    os.system("clear")
    for player_name, vote_count in votes.items():
        print(f"{player_name} 得到了 {vote_count} 票")
    
    # 选出被淘汰的玩家
    eliminated_player = max(votes, key=votes.get)
    print(f"{eliminated_player} 被投票淘汰出局。")
    next(p for p in players if p.name == eliminated_player).alive = False

def check_game_over(players):
    werewolves = [p for p in players if p.alive and p.role == '狼人']
    villagers = [p for p in players if p.alive and p.role != '狼人']

    if not werewolves:
        print("村民胜利！")
        return True
    if not villagers:
        print("狼人胜利！")
        return True
    return False

def play_game():
    num_human = int(input("请输入真人玩家数量: "))
    num_ai = int(input("请输入AI玩家数量: "))

    players = []
    for i in range(1, num_human + 1):
        players.append(Player(f"玩家{i}", None, True))
    for i in range(1, num_ai + 1):
        players.append(Player(f"AI{i}", None, False))

    assign_roles(players)
    display_roles(players)

    game_over = False
    while not game_over:
        os.system("clear")
        print("天黑请闭眼，开始夜晚行动...")
        victim = werewolves_act(players)
        if victim:
            victim.alive = False

        victim = witch_act(players, victim)
        if victim:
            victim.alive = False

        seer_act(players)

        os.system("clear")
        print("天亮了，请开始讨论并投票...")
        villagers_vote(players)

        game_over = check_game_over(players)

if __name__ == "__main__":
    play_game()
