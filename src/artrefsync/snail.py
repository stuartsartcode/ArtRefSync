import sys
import time
import math
import random
from enum import StrEnum

last = ""

def set_last(l):
    globals()['last'] = l

def get_last():
    return globals()['last']

class CURS(StrEnum):
    U = "\033[1A"
    D = "\033[1B"
    R = "\033[1C"
    L = "\033[1D"
    SCROLLD = "\033[1S"
    HIDE = "\033[?25l"
    SHOW = "\033[?25h"
    STARTD = "\033[1E"
    STARTU = "\033[1F"
    CLEAR = '\033[K'
    SAVE = "\033[s"
    RESTORE = "\033[u"

# sys.stdout.write(CURS.HIDE)
# sys.stdout.flush()


def curs_print(input, line = 0):
    cursor = CURS.STARTD * line if line >= 0 else CURS.STARTU * (-line)
    rcursor = CURS.STARTU * line if line >= 0 else CURS.STARTD * (-line)
    # print("\r" + repr(cursor))
    # print("\r" + repr(rcursor))
    return f"\r{cursor}\r{CURS.CLEAR}{input}{rcursor}"
    # return f"\r{CURS.SAVE}{cursor}\r{CURS.CLEAR}{input}{CURS.RESTORE}"

    


    

def loading(percent, prefix = "Loading", width = 20, snail = "🐌", trail = "_", line = 1, suffix = "", boxed = False):
    output = ""
    percent_str = str(int(percent*100)).rjust(3)
    snail_str = str(trail*int(percent * width - 1) + snail).ljust(width)
    bar_str = f"{prefix}: {percent_str}%[{snail_str}]{suffix}"
    if boxed:
        bar_str = f"│ {bar_str} │"
        output += curs_print(f"╭{'─'* (len(bar_str)-1)}╮", line)
        output += curs_print(bar_str, line + 1)
        output += curs_print(f"╰{'─'* (len(bar_str)-1)}╯\n{CURS.STARTU}", line+2)
    else:
        output = curs_print(bar_str, line)

    set_last(output)
    sys.stdout.write(output)
    sys.stdout.flush()

# def snail_print(input):
#     # sys.stdout.write(f"\r{get_last()}\r{CURS.CLEAR}{input}\n{CURS.CLEAR}")
#     if get_last() =="":
#         print(input)
#     else:
#         output = f"{CURS.STARTD*2}\r{CURS.CLEAR}{input}\n{CURS.CLEAR}\n\n\n{CURS.STARTD*3}{get_last()}"
#         sys.stdout.write(output)
#         sys.stdout.flush()

def snail_print(input):
    # sys.stdout.write(f"\r{get_last()}\r{CURS.CLEAR}{input}\n{CURS.CLEAR}")
    output = ""
    if get_last() =="":
        print(input)
    else:
        # output = f"{CURS.STARTD*4}\n{CURS.STARTU*4}\r{CURS.CLEAR}{input}\n{CURS.CLEAR}\n\n\n{CURS.STARTD*5}{get_last()}"
        # output += curs_print("\n",3)
        output += f"\n\r{CURS.CLEAR}{input}\r"
        output += get_last()
        sys.stdout.write(output)
        sys.stdout.flush()

def main():
    snails = 8
    width = 40
    run_time = 10

    if len(sys.argv) > 1:
        try:
            snails=int(sys.argv[1])
            width=int(sys.argv[2])
            run_time=int(sys.argv[3])
        except Exception:
            pass
    # snail_race(snails, width, time)

    # snail = "🐌"
    # ordsnail = ord(snail)
    # for i in range(10):
    #     print(chr(ordsnail + i))
    print(f"{'\n' * 4}{CURS.STARTU*4}")
    
    for i in range (101):
        if i % 10 == 0:
            snail_print(f"I = {i}")
            time.sleep(.1)
        else:
            loading(i / 100, boxed=True)
            time.sleep(.1)

def done(prefix = "Loading"):
    sys.stdout.write(f"\r{prefix}: Done\n") # Overwrite and add a newline at the end


def snail_race(num_snails = 8, track_width = 40, race_duration = 10):
    race_width = track_width-14
    print(f"╭{'─'* (track_width-2)}╮")
    print(f"│ {num_snails} SNAIL RACE".ljust(track_width-1) + "│" )
    print(f"│ ⚫⚫⚫⚫⚫".ljust(track_width-6) + "│" )
    print(f"├{'─'* (track_width-2)}┤")
    snail = "🐌"
    ordsnail = ord(snail)

    row_count = (track_width - 4)//2

    rows = 0
    row = ""
    for i in range(num_snails):
        row += chr(ordsnail + i)
        if len(row) == row_count:
            print(f"│ {row}".ljust(row_count+2) + " │" )
            rows += 1
            row = ""

    if row != "":

        print(f"│ {row}{" " *(track_width - (4+2*len(row)))} │")
        rows +=1

    print(f"├{'─'* (track_width-2)}┤")
    sys.stdout.write(f"{CURS.HIDE}{CURS.SAVE}{'\n'*(num_snails)}")
    sys.stdout.write(f"\r╰{'─'* (track_width-2)}╯")
    sys.stdout.flush()
    snails = {}
    for i in range(num_snails):
        snails[i] = 0

    # print(f"└{'─'* (track_width-2)}┘")
    r = race_duration / 200
    round=0
    winners = []
    winners_time = {}
    start_time = time.time()
    while len(winners) < num_snails:
        for i in range(num_snails):
            #snails[i] += random.randint(0,1)
            if snails[i] >= 100:
                if i not in winners:
                    winners.append(i)
                    winners_time[i] = (time.time() - start_time) * 100 / snails[i]
            else:
                snails[i] += random.randrange(0, 10) / 10

            loading(snails[i]/100, f"│ {chr(ordsnail + i)}", snail=chr(ordsnail + i), width= race_width, trail=" ",  line=-(num_snails -i), suffix="│")
        if round == 0:
            lights = ["🟡⚫⚫⚫⚫", "⚫🟡⚫⚫⚫", "⚫⚫🟡⚫⚫", "⚫⚫⚫🟢⚫"]
            for j in range(len(lights)):
                time.sleep(.6)
                sys.stdout.write(f"\r{CURS.SAVE}{CURS.U * (num_snails + 3 + rows)}│ {lights[j]}{CURS.RESTORE}")
            start_time = time.time()
        round += 1
        sys.stdout.flush() # Ensure the output is immediately displayed
        time.sleep(r)
    # snail_list = list(snails.keys())
    # snail_list = sorted(snail_list, key=lambda k: snails[k], reverse=True)
    print(f"\r├{'─'* (track_width-2)}┤")
    winners = sorted(winners, key=lambda k: winners_time[k])
    for i in range(len(winners)):
        print(f"│ #{i+1} - {chr(ordsnail + winners[0 + i])} TIME: {winners_time[winners[i]]}".ljust(track_width-2) + "│")
        if i == 2:
            break
    # print(f"└{'─'* (track_width-2)}┘{CURS.SHOW}")
    print(f"╰{'─'* (track_width-2)}╯{CURS.SHOW}")

# old_print = print
# print = snail_print

if __name__ == "__main__":
    main()