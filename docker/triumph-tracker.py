# builtin
import re
from datetime import datetime
from io import StringIO
from json import dumps
from pathlib import Path

# third-party
import lxml.etree as ET
import pandas as pd

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 200)
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT_DELAYS = 45 # seconds
BROWSER_OPTS = webdriver.FirefoxOptions()
BROWSER_OPTS.add_argument("--headless")
BROWSER_OPTS.add_argument("--disable-gpu")
BROWSER_OPTS.add_argument("--no-sandbox")
RAID_CSS_SELECTOR_MAP = {
    'rivensbane': (
        '#mat-expansion-panel-header-0', # apparently d2checklist does numerical-codes for seals so this will have to update if any layout changes occur
        '.checklist-table'
    ),
    'disciple-slayer': (
        '#mat-expansion-panel-header-16',
        '.checklist-table'
    ),
    'kingslayer': (
        '#mat-expansion-panel-header-22',
        '.checklist-table'
    )
}
GREYDERS_TRANSLATE = {
    'rivensbane': pd.DataFrame(
        data={
            'meaning': [
                'Badge', 'Finish Raid', 'Bro-Down', 'Wish Wall', 'Hidden Chests',
                'Plant Flags', 'Nope', 'All Arc', 'All Void', 'All Solar',
                'Same Class', 'Kali Challenge', 'Shuro Chi Challenge', 'Morgeth Challenge',
                'Vault Challenge', 'Riven Challenge'
            ]
        },
        # this is where we can force a sorting if we want
        index=pd.Index(
            data=[
                'Raid: Last Wish', 'O Murderer Mine', 'Clan Night: Last Wish',
                'Habitual Wisher', 'Treasure Trove', 'Put a Flag on It', "Petra's Run",
                'Thunderstruck', 'Night Owl', 'Sunburn', 'The New Meta',
                'Summoning Ritual', 'Coliseum Champion', 'Forever Fight', 'Keep Out',
                'Strength of Memory'
            ],
            name='Rivensbane Triumphs'
       ),
    ),
    'disciple-slayer': pd.DataFrame(
        data={
            'meaning': [
                'Finish Raid', 'Finish Master Raid', 'Bro-Down', 'All Arc', 'All Void',
                'All Solar', 'Same Class', 'Hidden Chests', 'Acquisition Challenge', 
                'Let Shieldybois Attack Obelisk', 'Caretaker Challenge', 'Everyone stun each floor',
                'Exhibition Challenge', 'Kill Glyphkeeper pair within 5s', 'Rhulk Challenge',
                'Dunks within 5s', 'Challenges in Master Mode', 'Lore Books', 'Badge'
            ]
        },
        index=pd.Index(
            data=[
                'Vow of the Disciple', 'Master Difficulty "Vow of the Disciple"', 'Clan Fieldtrip',
                'Dark Charge', 'Dark Abyss', 'Dark Flame', 'Together in the Deep', 'Secrets of the Sunken Pyramid',
                'Swift Destruction', 'On My Go', 'Base Information', 'Handle With Care',
                'Defenses Down', 'Glyph to Glyph', 'Looping Catalyst', 'Symmetrical Energy',
                'Pyramid Conqueror', '"Vow of the Disciple" Lore Book Unlocks', 'Raid: Vow of the Disciple'
            ],
            name='Disciple-Slayer Triumphs'
        )
    ),
    'kingslayer': pd.DataFrame(
        data={
            'meaning': [
                'Finish Raid', "One of each Secret Chest", "Bro-Down", 'All Arc', 'All Solar',
                'All Void', 'Same Class', 'Opening - swap dunkers', 'Totems Challenge', 
                'Totems - only 1 player on plate at a time', 'Warpiest Challenge', 'Warpiest - swap brandkillers',
                'Golgy Challenge', 'Golgy - swap taunters', 'Daughters Challenge',
                "Daughters - taken player can't touch the ground", 'Oryx Challenge', 'Oryx - get last stand in 1 round', 
                'Finish Master Raid', 'Challenges in Master Mode', 'Badge'
            ]
        },
        index=pd.Index(
            data=[
                "King's Fall", "King's Ransom", "Court of Jesters", "Spark of Defiance", "Sunburst",
                "The Abyssal Society", "Hive Mind", "Controlled Dunks", "The Grass is Always Greener",
                "Overzealous", "Devious Thievery", "Brand Buster", "Gaze Amaze", "Taking Turns",
                "Under Construction", "The Floor is Lava", "Hands Off", "Overwhelming Power",
                "One True King", "King of Kings", "Raid: King's Fall"
            ],
            name='Kingslayer Triumphs'
        )
    )
}

def get_data_for_player(browser, seal, player_name, url):
    seal_selector, table_selector = RAID_CSS_SELECTOR_MAP.get(seal, (-1, -1))
    if seal_selector == -1:
        raise NotImplementedError('No CSS selector defined for seal: %s' % seal)
    browser.get(url)
    # need to click the seal to get the triumph table
    WebDriverWait(browser, TIMEOUT_DELAYS).until(
         EC.element_to_be_clickable((By.CSS_SELECTOR, seal_selector))
    )
    wait = WebDriverWait(browser, timeout=40, poll_frequency=1)
    element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, seal_selector)))

    button = browser.find_element(By.CSS_SELECTOR, seal_selector)
    button.click()
    # get triumph table for wanted seal
    WebDriverWait(browser, TIMEOUT_DELAYS).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, table_selector))
    )
    table = browser.find_element(By.CSS_SELECTOR, table_selector)
    html = table.get_attribute('innerHTML')
    # this is janky but works for rivensbane - the triumph text label is not stored in a conventional element
    label_end_matches = list(re.finditer(' <!----><!----><fa-icon _ngcontent-', html))
    labels = [html[match.start()-40:match.start()].split('> ')[-1].strip() for match in label_end_matches]
    parser = ET.HTMLParser()
    root = ET.fromstring(html, parser)
    triumphs = root.xpath('/html/body/tbody/tr')
    # check indicates that the triumph is complete
    is_ticked = [
        True if triumph.xpath('.//fa-icon')[0].xpath('.//svg')[0].attrib.get('class') == 'svg-inline--fa fa-square-check' else False
        for triumph in triumphs
    ]
    data = {
        player_name: {
            triumph: finished
            for triumph, finished in zip(labels, is_ticked)
        }
    }
    return data

def json_to_df(data, seal):
    '''
    Convert player data nested dict containing triumph labels into dataframe with greyder-compatible labels
    '''
    translator = GREYDERS_TRANSLATE.get(seal)
    if not isinstance(translator, pd.DataFrame):
        raise NotImplementedError('No Greyders translation for seal: %s' % seal)
    df = pd.merge(
        translator,
        pd.read_json(StringIO(dumps(data))),
        left_index=True,
        right_index=True
    )
    return df

def df_to_csv(df, seal):
    '''
    Output only the not-completed-by-everyone triumphs for the given seal
    '''
    out_csv = Path(f'./out_csv/{seal}_status_{datetime.today().strftime("%Y%m%d")}.csv')
    if not out_csv.parent.exists():
        out_csv.parent.mkdir()
    if out_csv.exists():
        out_csv.unlink()
    # only keep the triumphs we still need to get
    remaining = df.loc[~df[df.columns[1:]].all(axis=1)].copy()
    # ensure common column width for later whitespace-diffing
    remaining.index = remaining.index.str.pad(
        df.index.str.len().max(), # use the max-possible index value length
        side='right'
    )
    remaining['meaning'] = remaining['meaning'].str.pad(
        df['meaning'].str.len().max(), # use the max-possible meaning value length
        side='left'
    )
    with out_csv.open('w', encoding='utf-8') as f:
        f.write(str(remaining))

def df_to_csv_pretty(df, seal):
    '''
    Just because
    '''
    out_csv = Path(f'./out_csv/{seal}_status_{datetime.today().strftime("%Y%m%d")}_pretty.csv')
    if not out_csv.parent.exists():
        out_csv.parent.mkdir()
    if out_csv.exists():
        out_csv.unlink()    
    cols = df.columns
    vals = df.values
    first_col_width = max([len(val) for val in df.index])
    second_col_width = max([len(val[0]) for val in vals])
    col_widths = [len(col) for col in cols]
    buffer = ['═' * col_width for col_width in col_widths[1:]]
    first_line = '╔' + '═' * first_col_width + '╦' + '═' * second_col_width + '╦' + '╦'.join(buffer) + '╗'
    header = '║' + ' ' * first_col_width + '║' + 'meaning'.rjust(second_col_width) + '║' + '║'.join(cols[1:]) + '║'
    footer = '╠' + '═' * first_col_width + '╬' + '═' * second_col_width + '╬' + '╬'.join(buffer) + '╣'
    table = '\n'.join([first_line, header, footer])
    for idx, row in enumerate(vals):
        padded = [str(v).rjust(i) for v,i in zip(row[1:], col_widths[1:])]
        row_text = '║' + df.index[idx].ljust(first_col_width) + '║' + row[0].rjust(second_col_width) + '║' + '║'.join(padded) + '║'
        table += f'\n{row_text}'
        footer_cap = True if idx == len(vals) - 1 else False
        if footer_cap:
            cap = '╚' + '═' * first_col_width + '╩' + '═' * second_col_width + '╩' + '╩'.join(buffer) + '╝'
            table += f'\n{cap}'
        else:
            table += f'\n{footer}'
    if not out_csv.exists():
        with out_csv.open(mode='w', encoding='utf-8') as f:
            f.out_csv(table)

if __name__ == '__main__':
    repo_dir = Path(__file__).parent
    cfg_file = Path('./config')
    if not cfg_file.exists():
        raise FileNotFoundError('Cannot find .config - use the template to make your own')
    with cfg_file.open() as f:
        lines = [
            line.strip().split(',') for line in f.readlines()
            if not line.startswith('#') and not len(line) < 10
        ]
    if len(lines) == 0:
        print('No lines to process in config')
        exit()
    browser = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),

        options=BROWSER_OPTS,
        service_log_path=(repo_dir / 'geckodriver' / 'geckodriver.log')
    )
    print(f"Using Firefox v{browser.capabilities.get('browserVersion')} and geckodriver v{browser.capabilities.get('moz:geckodriverVersion')}")
    for seal in sorted(set([line[0] for line in lines])):
        print('Scraping data for seal: %s' % seal)
        seal_lines = [line for line in lines if line[0] == seal]
        seal_dict = {}
        for line in seal_lines:
            print(line[1], end=' ', flush=True)
            seal_dict.update(get_data_for_player(browser, *line))
        print('')
        df = json_to_df(seal_dict, seal)
        df_to_csv(df, seal)
        #df_to_csv_pretty(df, seal)
    browser.close()