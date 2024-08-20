import random
import time
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

class Player:
    def __init__(self, role, is_ai=False):
        self.alive = True
        self.role = role
        self.is_ai = is_ai
        self.potions = {"save": 1, "poison": 1}

def assign_roles(num_players, num_real_players):
    roles = ['狼人', '狼人', '女巫', '预言家'] + ['平民'] * (num_players - 4)
    random.shuffle(roles)
    
    players = []
    for i in range(num_players):
        is_ai = i >= num_real_players
        players.append(Player(roles[i], is_ai))
    
    return players

def show_roles(players):
    console.print(Panel("游戏开始！", title="狼人杀"))
    for i, player in enumerate(players):
        if not player.is_ai:
            console.print(Panel(f"[bold yellow]玩家{i+1} 的身份是 [bold red]{player.role}[/bold red]", title="身份显示"))
            Prompt.ask("按下 Enter 清除屏幕以继续")
            console.clear()

def werewolves_act(players):
    werewolves = [p for p in players if p.alive and p.role == '狼人']
    targets = [p for p in players if p.alive and p.role != '狼人']

    if not werewolves:
        return None

    victim = None
    if any(not wolf.is_ai for wolf in werewolves):
        console.print(Panel("狼人请睁眼...", title="狼人环节"))
        time.sleep(2)
        console.print("狼人请讨论并选择一个玩家进行攻击...")
        for i, target in enumerate(targets):
            console.print(f"{i+1}: 玩家{i+1}")

        victim_index = int(Prompt.ask("输入要攻击的玩家编号: ")) - 1
        victim = targets[victim_index]
        console.clear()
    else:
        victim = random.choice(targets)

    if victim:
        victim.alive = False
        console.print(f"狼人杀害了 玩家{players.index(victim)+1}!", style="bold red")
        time.sleep(2)
        console.clear()
    return victim

def witch_act(players, last_victim):
    witch = next((p for p in players if p.alive and p.role == '女巫' and not p.is_ai), None)
    if not witch or last_victim is None:
        return

    console.print(Panel("女巫请睁眼...", title="女巫环节"))
    time.sleep(2)

    if witch.potions['save'] > 0 and not last_victim.alive:
        console.print(f"玩家{players.index(last_victim)+1} 被杀，你要救他吗？(Y/N)")
        save = Prompt.ask("救活此玩家?", choices=["Y", "N"]).strip().upper() == 'Y'
        if save:
            last_victim.alive = True
            witch.potions['save'] -= 1
            console.print(f"女巫救活了 玩家{players.index(last_victim)+1}!", style="bold green")
        else:
            console.print(f"玩家{players.index(last_victim)+1} 仍然死亡。", style="bold red")

    if witch.potions['poison'] > 0:
        poison = Prompt.ask("你要毒谁吗？(Y/N)").strip().upper() == 'Y'
        if poison:
            targets = [p for p in players if p.alive and p != witch]
            for i, target in enumerate(targets):
                console.print(f"{i+1}: 玩家{players.index(target)+1}")
            victim_index = int(Prompt.ask("输入要毒死的玩家编号: ")) - 1
            victim = targets[victim_index]
            victim.alive = False
            witch.potions['poison'] -= 1
            console.print(f"女巫毒死了 玩家{players.index(victim)+1}!", style="bold red")

    time.sleep(2)
    console.clear()

def seer_act(players):
    seer = next((p for p in players if p.alive and p.role == '预言家' and not p.is_ai), None)
    if not seer:
        return

    console.print(Panel("预言家请睁眼...", title="预言家环节"))
    time.sleep(2)
    console.print("请选择一个玩家进行查验...")
    targets = [p for p in players if p.alive and p != seer]
    for i, target in enumerate(targets):
        console.print(f"{i+1}: 玩家{players.index(target)+1}")

    target_index = int(Prompt.ask("输入要查验的玩家编号: ")) - 1
    target = targets[target_index]
    console.print(f"玩家{players.index(target)+1} 的身份是: {target.role}", style="bold yellow")

    time.sleep(2)
    console.clear()

def voting(players):
    console.print(Panel("现在开始投票环节...", title="投票环节"))
    time.sleep(2)
    votes = {p: 0 for p in players if p.alive}

    for player in players:
        if player.alive and not player.is_ai:
            console.print(f"玩家{players.index(player)+1} 请输入你要投票淘汰的玩家编号:")
            targets = [p for p in players if p.alive and p != player]
            for i, target in enumerate(targets):
                console.print(f"{i+1}: 玩家{players.index(target)+1}")

            vote_index = int(Prompt.ask("投票: ")) - 1
            votes[targets[vote_index]] += 1

    most_voted = max(votes, key=votes.get)
    most_voted.alive = False
    console.print(f"玩家{players.index(most_voted)+1} 被投票淘汰出局，身份是 {most_voted.role}。", style="bold red")

    time.sleep(2)
    console.clear()

def check_winner(players):
    alive_werewolves = any(p.alive and p.role == '狼人' for p in players)
    alive_civilians = any(p.alive and p.role != '狼人' for p in players)
    
    if not alive_werewolves:
        console.print("平民胜利！")
        return True
    if not alive_civilians:
        console.print("狼人胜利！")
        return True
    return False

def play_game():
    console.clear()
    num_players = int(Prompt.ask("请输入总玩家数"))
    num_real_players = int(Prompt.ask("请输入真人玩家数"))

    players = assign_roles(num_players, num_real_players)
    show_roles(players)

    while any(p.alive for p in players) and not check_winner(players):
        last_victim = werewolves_act(players)
        witch_act(players, last_victim)
        seer_act(players)
        voting(players)
    
    console.print("游戏结束！")

play_game()
