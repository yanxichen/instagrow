import sys, os
import schedule
import time
from .instagrow import InstaGrow
from .constants import *
from PyInquirer import style_from_dict, Token, prompt, Validator, ValidationError

like_count = 0

dirname = os.path.dirname(__file__)
login_file = os.path.join(dirname, 'login.csv')
preset_file = os.path.join(dirname, 'preset.csv')
follow_list_file = os.path.join(dirname, 'follow_list.csv')

print('InstaGrow is an automation tool that likes & follows users on Instagram on your behalf.',
      'If this is your first time launching InstaGrow, it\'s recommended that you review the settings first.')
print('Logging in...')


class NumberValidator(Validator):
    def validate(self, document):
        try:
            float(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))


def login_no_prompt():
    with open(login_file, 'r') as csvfile:
        filereader = csv.reader(csvfile, delimiter=',')
        for row in filereader:
            info = {'username': row[0],
                    'password': row[1]}
    try:
        return info
    except UnboundLocalError:
        print('Cannot access login info. Please manually log in.')


def login_prompt():
    questions = [
        {
            'type': 'input',
            'message': 'Enter your Instagram username',
            'name': 'username'
        },
        {
            'type': 'password',
            'message': 'Enter your Instagram password',
            'name': 'password'
        }]
    answers = prompt(questions)
    with open(login_file, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
        filewriter.writerow([answers['username'], answers['password']])
    return answers


if not os.path.isfile(login_file):
    login_info = login_prompt()
else:
    login_info = login_no_prompt()
    if login_info is None:
        login_info = login_prompt()

try:
    bot = InstaGrow(user=login_info['username'],
                password=login_info['password'],
                like_count=like_count)
except TypeError:
    print('Cannot log in. Please try again.')


def run_hashtag_campaign():
        bot.hashtag_campaign()
        global like_count
        like_count = bot.like_count
        print("current likes at: ")
        print(like_count)


def run_maintain_folllowing_user():
    if not os.path.isfile(follow_list_file):
        print('You have not yet followed any users through InstaGrow.')
        return
    bot.maintain_following_user()


def launch_hashtag_campaign():

    schedule_prompt = {
        'type': 'list',
        'name': 'schedule',
        'message': 'How would you like the campaign to run?',
        'choices': ['Every few minutes until daily max number of pictures are liked', 'Just this once',
                    'Back to previous menu']
    }

    answers = prompt(schedule_prompt)

    if answers['schedule'] == 'Every few minutes until daily max number of pictures are liked':
        interval_prompt = {
            'type': 'input',
            'name': 'interval',
            'message': 'How many minutes between each campaign?',
            'validate': NumberValidator
        }
        interval = prompt(interval_prompt)['interval']

        schedule.every(int(interval)).minutes.do(run_hashtag_campaign)

        print('Launching campaign every ' + interval + ' minutes...',
              'Press Ctrl+C to exit to the previous menu')
        while like_count < MAX_DAILY_LIKES:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                print('Exit to main menu...')
                main_menu()
                break

        sys.exit()

    elif answers['schedule'] == 'Just this once':
        run_hashtag_campaign()

    else:
        main_menu()


style = style_from_dict({
    Token.Separator: '#6C6C6C',
    Token.QuestionMark: '#FF9D00 bold',
    Token.Selected: '',  # default
    Token.Pointer: '#FF9D00 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#5F819D bold',
    Token.Question: '',
})


def main():

    main_menu()


def main_prompt():
    login = [
        {
            'type': 'list',
            'name': 'menu',
            'message': 'What would you like to do?',
            'choices': ['Launch Hashtag Campaign', 'Launch Influencer Campaign (WIP)',
                        'Schedule Campaign', 'Follower Retention',
                        'Settings', 'Help', 'Exit']
        }
    ]

    answers = prompt(login)
    return answers


def settings():
    try:
        with open(preset_file, 'r') as csvfile:
            filereader = csv.reader(csvfile, delimiter=',')
            preset = {}
            for row in filereader:
                preset[row[0]] = row[1]
        print(preset)
    except IOError:
        print('Settings file corrupted')
        pass
        # TODO allow user to recreate preset

    preset_list = []
    for key in preset:
        preset_list.append(key)
    preset_list.append('Cancel')

    settings_prompt = {
        'type': 'list',
        'name': 'settings',
        'message': 'Change settings',
        'choices': preset_list
    }

    answers = prompt(settings_prompt)
    if answers['settings'] == 'Cancel':
        main_menu()
    else:
        for setting in preset_list:
            if answers['settings'] == setting:
                print('Current ' + setting + ' at: ' + preset[setting])
                sub_prompt = {
                    'type': 'list',
                    'name': 'sub_setting',
                    'message': 'What would you like to do?',
                    'choices': [
                        'Modify',
                        'Cancel'
                    ]
                }
                if prompt(sub_prompt)['sub_setting'] == 'Modify':
                    modify_prompt = {
                        'type': 'input',
                        'message': 'Enter new setting',
                        'name': 'modify',
                        'validate': NumberValidator
                    }
                    new_value = prompt(modify_prompt)['modify']
                    rows = []
                    for key in preset:
                        if key == setting:
                            preset[setting] = new_value
                        rows.append([key, preset[key]])

                    with open(preset_file, 'w') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')
                        writer.writerows(rows)

                else:
                    settings()

    main_menu()


def main_menu():
    menu_selection = main_prompt()
    if menu_selection['menu'] == 'Launch Hashtag Campaign':
        print('launching hashtag campaign...')
        launch_hashtag_campaign()
    elif menu_selection['menu'] == 'Launch Influencer Campaign':
        pass
    elif menu_selection['menu'] == 'Follower Retention':
        run_maintain_folllowing_user()
        main_menu()
    elif menu_selection['menu'] == 'Settings':
        settings()
    elif menu_selection['menu'] == 'Help':
        pass
    else:
        sys.exit()


if __name__ == '__main__':
    main()
