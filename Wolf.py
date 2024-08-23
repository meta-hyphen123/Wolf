import random
import time
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

console = Console()

class Player:
    def __init__(self, role, is_ai=False):
        self.alive = True
        self.role = role
        self.is_ai = is_ai
        self.potions = {"save": 1, "poison": 1} if role == "女巫" else {}

    def ai_action(self, players, action_type, victim=None):
        if action_type == "werewolf_kill":
            targets = [p for p in players if p.alive and p.role != '狼人']
            return random.choice(targets) if targets else None

        if action_type == "witch_save":
            return self.potions["save"] > 0 and random.choice([True, False])

        if action_type == "witch_poison":
            return self.potions["poison"] > 0 and random.choice([True, False])

        if action_type == "seer_check":
            targets = [p for p in players if p.alive and p != self]
            return random.choice(targets) if targets else None

        if action_type == "vote":
            if random.random() > 0.5:  # 50% 机会投票
                targets = [p for p in players if p.alive and p != self]
                if random.random() < 0.6:  # 60% 几率投狼人
                    targets = [p for p in targets if p.role == '狼人']
                return random.choice(targets) if targets else None
            return None

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

def get_valid_input(prompt_message, valid_range):
    while True:
        try:
            value = int(Prompt.ask(prompt_message)) - 1
            if value in valid_range:
                return value
            else:
                console.print("无效输入，请输入一个有效的编号。")
        except ValueError:
            console.print("输入无效，请输入一个数字。")

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
            console.print(f"{i+1}: 玩家{players.index(target)+1}")

        victim_index = get_valid_input("输入要攻击的玩家编号: ", range(len(targets)))
        victim = targets[victim_index]
        console.clear()
    else:
        victim = werewolves[0].ai_action(players, "werewolf_kill")

    if victim:
        victim.alive = False
        console.print(f"狼人杀害了 玩家{players.index(victim)+1}!", style="bold red")
        time.sleep(2)
        console.clear()
    return victim

def witch_act(players, last_victim):
    # 寻找存活的女巫
    witch = next((p for p in players if p.alive and p.role == '女巫'), None)
    if not witch:
        return

    console.print(Panel("女巫请睁眼...", title="女巫环节"))
    time.sleep(2)

    # 初始化女巫的行动决策变量
    save = False
    poison = False
    poison_target = None

    # 如果女巫是AI，根据AI逻辑决定是否救活和毒杀
    if witch.is_ai:
        save = witch.ai_action(players, "witch_save", last_victim)
        poison = witch.ai_action(players, "witch_poison")

        if poison and witch.potions['poison'] > 0:
            targets = [p for p in players if p.alive and p != witch]
            poison_target = witch.ai_action(players, "witch_poison", targets)
    
    # 如果女巫是真人玩家，通过控制台输入决定行动
    else:
        if witch.potions['save'] > 0 and last_victim and not last_victim.alive:
            console.print(f"玩家{players.index(last_victim)+1} 被杀，你要救他吗？(Y/N)")
            save_choice = Prompt.ask("救活此玩家?", choices=["Y", "N"]).strip().upper()
            save = save_choice == 'Y'

        if witch.potions['poison'] > 0:
            console.print("你要毒谁吗？(Y/N)")
            poison_choice = Prompt.ask("毒杀玩家?", choices=["Y", "N"]).strip().upper()
            if poison_choice == 'Y':
                targets = [p for p in players if p.alive and p != witch]
                for i, target in enumerate(targets):
                    console.print(f"{i+1}: 玩家{players.index(target)+1}")
                victim_index = get_valid_input("输入要毒死的玩家编号: ", range(len(targets)))
                poison_target = targets[victim_index]
                poison = True  # 更新poison变量为True，表示女巫决定毒杀

    # 执行女巫的救活行动
    if save:
        last_victim.alive = True
        witch.potions['save'] -= 1
        console.print(f"女巫救活了 玩家{players.index(last_victim)+1}!", style="bold green")

    # 执行女巫的毒杀行动
    if poison and poison_target:
        poison_target.alive = False
        witch.potions['poison'] -= 1
        console.print(f"女巫毒死了 玩家{players.index(poison_target)+1}!", style="bold red")

    time.sleep(2)
    console.clear()

def seer_act(players):
    seer = next((p for p in players if p.alive and p.role == '预言家'), None)
    if not seer or not any(not p.is_ai for p in players if p.role == '预言家'):
        return

    console.print(Panel("预言家请睁眼...", title="预言家环节"))
    time.sleep(2)
    console.print("请选择一个玩家进行查验...")
    targets = [p for p in players if p.alive and p != seer]
    
    if seer.is_ai:
        target = seer.ai_action(players, "seer_check")
    else:
        for i, target in enumerate(targets):
            console.print(f"{i+1}: 玩家{players.index(target)+1}")
        target_index = get_valid_input("输入要查验的玩家编号: ", range(len(targets)))
        target = targets[target_index]

    console.print(f"玩家{players.index(target)+1} 的身份是: {target.role}", style="bold yellow")

    time.sleep(2)
    console.clear()

def daytime_discussion(players):
    console.print(Panel("天亮了，现在开始讨论...", title="白天讨论"))
    for player in players:
        if player.alive:
            if player.is_ai:
                dialogue = ""
                if player.role == '狼人':
                    dialogue = f"玩家{players.index(player)+1}: 我是平民，我认为狼人可能是..."
                elif player.role == '预言家':
                    checked_player = next((p for p in players if p.alive and p != player and p.role != '预言家'), None)

                    dialogue = f"玩家{players.index(player)+1}: 我是预言家，昨晚查验了玩家{players.index(checked_player)+1}，他的身份是 {checked_player.role}。" if checked_player else "没有线索，过。"
                elif player.role == '女巫':
                    dialogue = f"玩家{players.index(player)+1}: 我是女巫，昨晚我使用了 {'解药' if player.potions['save'] < 1 else '毒药'}。" if random.random() < 0.4 else "没有线索，过。"
                else:
                    dialogue = f"玩家{players.index(player)+1}: 没有线索，过。"
                
                for char in dialogue:
                    console.print(char, end='', style="bold cyan")
                    time.sleep(0.05)
                console.print("\n")
            else:
                console.print(f"玩家{players.index(player)+1}: 请发言。")
                Prompt.ask("按下 Enter 继续")
            time.sleep(2)

    console.clear()

def voting(players):
    console.print(Panel("现在开始投票环节...", title="投票环节"))
    time.sleep(2)
    
    # 初始化每个玩家的票数为0
    votes = {p: 0 for p in players if p.alive}

    # 循环每个玩家进行投票
    for player in players:
        if player.alive:
            if player.is_ai:
                # AI角色的投票逻辑
                target = player.ai_action(players, "vote")
                if target:
                    votes[target] += 1
                    console.print(f"玩家{players.index(player)+1} 投票给了 玩家{players.index(target)+1}。", style="bold cyan")
            else:
                # 真人玩家的投票逻辑
                console.print(f"玩家{players.index(player)+1}: 请投票。")
                targets = [p for p in players if p.alive and p != player]
                for i, target in enumerate(targets):
                    console.print(f"{i+1}: 玩家{players.index(target)+1}")
                
                vote_index = get_valid_input("投票: ", range(len(targets)))
                selected_target = targets[vote_index]
                votes[selected_target] += 1
                console.print(f"你投票给了 玩家{players.index(selected_target)+1}。", style="bold cyan")
            time.sleep(1)

    # 统计最多票数的玩家
    most_voted_count = max(votes.values())
    most_voted_players = [p for p, count in votes.items() if count == most_voted_count]

    # 如果有平票情况，随机选一个淘汰
    if len(most_voted_players) > 1:
        most_voted = random.choice(most_voted_players)
        console.print("出现平票情况，随机淘汰一名玩家...", style="bold yellow")
    else:
        most_voted = most_voted_players[0]

    # 淘汰得票最多的玩家
    most_voted.alive = False
    console.print(f"玩家{players.index(most_voted)+1} 被投票淘汰出局，身份是 [bold red]{most_voted.role}[/bold red]。", style="bold red")

    time.sleep(2)
    console.clear()


def check_winner(players):
    alive_werewolves = any(p.alive and p.role == '狼人' for p in players)
    alive_civilians = any(p.alive and p.role != '狼人' for p in players)
    
    if not alive_werewolves:
        console.print("平民胜利！", style="bold green")
        return True
    if not alive_civilians:
        console.print("狼人胜利！", style="bold red")
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
        
        if any(not p.is_ai for p in players if p.role == '女巫'):
            witch_act(players, last_victim)

        if any(not p.is_ai for p in players if p.role == '预言家'):
            seer_act(players)
            
        daytime_discussion(players)
        voting(players)
    
    console.print("游戏结束！")

play_game()
