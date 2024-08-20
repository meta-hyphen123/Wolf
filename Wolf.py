import random
import time
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.align import Align

console = Console()

class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.alive = True
        self.role = None
        self.is_ai = is_ai
        self.potions = {"save": 1, "poison": 1}

    def speak(self, message):
        console.print(f"[bold yellow]{self.name}[/bold yellow]: {message}")

def assign_roles(players):
    num_players = len(players)
    roles = ['狼人', '狼人', '女巫', '预言家', '平民', '平民', '平民', '平民']

    if num_players < len(roles):
        roles = roles[:num_players]
    else:
        roles += ['平民'] * (num_players - len(roles))

    random.shuffle(roles)
    
    for i in range(num_players):
        players[i].role = roles[i]
        console.print(f"{players[i].name} 被分配为 {roles[i]}")
        time.sleep(1)
        console.clear()

def get_valid_input(prompt, choices):
    while True:
        choice = Prompt.ask(prompt, choices=[str(i+1) for i in range(len(choices))])
        return int(choice) - 1

def show_roles(players):
    console.print(Panel("游戏开始！", title="狼人杀"))
    for player in players:
        if not player.is_ai:
            console.print(Panel(f"[bold yellow]{player.name}[/bold yellow] 的身份是 [bold red]{player.role}[/bold red]"))
            time.sleep(1)
            console.clear()

def werewolves_act(players):
    werewolves = [p for p in players if p.alive and p.role == '狼人']
    targets = [p for p in players if p.alive and p.role != '狼人']

    if not werewolves:
        return None

    console.print(Panel("狼人请睁眼...", title="狼人环节"))
    time.sleep(2)
    console.print("狼人们，请讨论并选择一个玩家进行攻击...")

    for i, target in enumerate(targets):
        console.print(f"{i+1}: {target.name}")

    for wolf in werewolves:
        if wolf.is_ai:
            victim = random.choice(targets)
            wolf.speak(f"我觉得我们应该攻击 {victim.name}")
        else:
            victim_index = get_valid_input("输入要攻击的玩家编号: ", targets)
            victim = targets[victim_index]

    console.print(f"狼人攻击了 {victim.name}!", style="bold red")
    time.sleep(2)
    console.clear()
    return victim

def witch_act(players, last_victim):
    witches = [p for p in players if p.alive and p.role == '女巫']
    if not witches or last_victim is None:
        return

    for witch in witches:
        console.print(Panel("女巫请睁眼...", title="女巫环节"))
        time.sleep(2)

        if witch.potions['save'] > 0 and last_victim.alive is False:
            console.print(f"女巫 {witch.name}，{last_victim.name} 被杀，你要救他吗？(Y/N)")
            if witch.is_ai:
                save = random.choice([True, False])
                witch.speak("我决定救他" if save else "我不救他")
            else:
                save = Prompt.ask("救活此玩家?", choices=["Y", "N"]).strip().upper() == 'Y'

            if save:
                console.print(f"女巫救活了 {last_victim.name}!", style="bold green")
                last_victim.alive = True
                witch.potions['save'] -= 1
            else:
                console.print(f"{last_victim.name} 仍然死亡。", style="bold red")
                last_victim.alive = False

        if witch.potions['poison'] > 0:
            console.print("你要毒谁吗？(Y/N)")
            if witch.is_ai:
                poison = random.choice([True, False])
                witch.speak("我决定毒人" if poison else "我不毒人")
            else:
                poison = Prompt.ask("使用毒药?", choices=["Y", "N"]).strip().upper() == 'Y'

            if poison:
                targets = [p for p in players if p.alive and p != witch]
                if targets:
                    for i, target in enumerate(targets):
                        console.print(f"{i+1}: {target.name}")
                    victim_index = get_valid_input("输入要毒死的玩家编号: ", targets)
                    victim = targets[victim_index]
                    console.print(f"女巫毒死了 {victim.name}!", style="bold red")
                    victim.alive = False
                    witch.potions['poison'] -= 1

        time.sleep(2)
        console.clear()

def seer_act(players):
    seers = [p for p in players if p.alive and p.role == '预言家']
    if not seers:
        return

    for seer in seers:
        console.print(Panel("预言家请睁眼...", title="预言家环节"))
        time.sleep(2)
        console.print(f"预言家 {seer.name}，请选择一个玩家进行查验...")

        targets = [p for p in players if p.alive and p != seer]
        if targets:
            for i, target in enumerate(targets):
                console.print(f"{i+1}: {target.name}")

            if seer.is_ai:
                target = random.choice(targets)
                seer.speak(f"我觉得 {target.name} 很可疑")
            else:
                target_index = get_valid_input("输入要查验的玩家编号: ", targets)
                target = targets[target_index]

            console.print(f"{target.name} 的身份是: {target.role}", style="bold yellow")

        time.sleep(2)
        console.clear()

def voting(players):
    if not any(p.alive for p in players):
        return

    console.print(Panel("现在开始投票环节...", title="投票环节"))
    time.sleep(2)
    votes = {p: 0 for p in players if p.alive}

    for player in players:
        if player.alive:
            console.print(f"玩家 {player.name}，请输入你要投票淘汰的玩家编号:")
            targets = [p for p in players if p.alive and p != player]
            if targets:
                for i, target in enumerate(targets):
                    console.print(f"{i+1}: {target.name}")

                if player.is_ai:
                    vote_index = random.choice(range(len(targets)))
                    player.speak(f"我决定投票 {targets[vote_index].name}")
                else:
                    vote_index = get_valid_input("投票: ", targets)

                votes[targets[vote_index]] += 1

    if votes:
        most_voted = max(votes, key=votes.get)
        console.print(f"{most_voted.name} 被投票淘汰出局。", style="bold red")
        most_voted.alive = False

    time.sleep(2)
    console.clear()

def play_game():
    console.clear()
    num_players = int(Prompt.ask("请输入总玩家数"))
    num_real_players = int(Prompt.ask("请输入真人玩家数"))
    num_ai_players = num_players - num_real_players

    players = []
    for i in range(num_real_players):
        name = Prompt.ask(f"请输入真人玩家 {i+1} 的名字")
        players.append(Player(name))

    for i in range(num_ai_players):
        name = f"AI玩家{i+1}"
        players.append(Player(name, is_ai=True))

    random.shuffle(players)

    assign_roles(players)
    show_roles(players)

    while any(p.alive for p in players):
        victim = werewolves_act(players)
        if victim:
            witch_act(players, victim)
        seer_act(players)
        voting(players)

    console.print("游戏结束！")

play_game()