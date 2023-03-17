import json
import logging
import sqlite3
from pathlib import Path
from subprocess import check_output

import aiobungie

logging.basicConfig(
    format='{asctime} | {name} | {levelname} | {message}',
    datefmt='%Y-%m-%d %H:%M:%S',
    style='{',
    level=logging.INFO
)
LOGGER = logging.getLogger('triumph-tracker')
# these are how the manifest labels them, not the rewarded titles
WANTED_SEALS = [
    'Root of Nightmares',
    'King\'s Fall',
    'Last Wish',
    'Vow of the Disciple',
    'Deep Stone Crypt',
    'Vault of Glass',
    'Spire of the Watcher',
    'Duality'
]
MANIFEST_DATA = Path(__file__).parent / '../manifest.sqlite3'
CLAN_DATA = Path(__file__).parent / '../clan_data.sqlite3'
api_key = check_output('echo $API_KEY', shell=True).decode('utf-8').strip()
if api_key == '':
    raise KeyError("Cannot find env var: 'API_KEY'")
AIO_CLIENT = aiobungie.Client(api_key)


def get_raid_hashes(wanted_seals: list) -> dict:
    '''Uses the manifest to retrieve the item hashes for the seals we want'''
    con = sqlite3.connect(f'file:{MANIFEST_DATA}?mode=ro', uri=True)
    with con:
        # load the json column data (actually a blob) as dict
        presentation_nodes = [
            json.loads(item[0])
            for item in con.execute("SELECT json FROM DestinyPresentationNodeDefinition;").fetchall()
        ]
        record_defns = [
            json.loads(item[0])
            for item in con.execute("SELECT json FROM DestinyRecordDefinition;").fetchall()
        ]
    con.close()
    #  make the sql result nicer to use later
    presentation_nodes = {node['hash']: node for node in presentation_nodes}
    record_defns = {record['hash']: record for record in record_defns}
    seals_data = [
        item for item in presentation_nodes.values() 
        if item['nodeType'] == 3
        and item['displayProperties']['name'] in wanted_seals
    ]
    assert len(seals_data) > 0
    raid_hashes = {}
    for seal in seals_data:
        raid_hashes.update({
            seal['displayProperties']['name']: {
                'records': {
                    record['recordHash']: (
                        record_defns.get(
                            record['recordHash']
                        )['displayProperties']['name'],
                        record_defns.get(
                            record['recordHash']
                        )['displayProperties']['description']
                    )
                    for record in seal['children']['records']
                },
                'hash': seal['hash'],
                'title': record_defns.get(
                    seal['completionRecordHash']
                )['titleInfo']['titlesByGender']
            }
        })
    return raid_hashes

async def get_player_completion(bungie_name, bungie_code, raid_hashes) -> dict:
    '''Uses the item hashes with player data to get completion information'''
    async with AIO_CLIENT.rest:
        # identify the main membershiptype (i.e. the one you picked during cross-save setup)
        profiles = await AIO_CLIENT.fetch_player(bungie_name, bungie_code)
        main_membershiptype = list(set([f.crossave_override for f in profiles])).pop()
        # get the actual profile that bungie-api will be happy to work with
        main_profile = await AIO_CLIENT.fetch_player(bungie_name, bungie_code, main_membershiptype)
        profile_id = main_profile.pop()
        profile = await profile_id.fetch_self_profile([aiobungie.ComponentType.RECORDS])
    # get the objective hashes from manifest
    con = sqlite3.connect(MANIFEST_DATA)
    with con:
        objective_defns = [
            json.loads(item[0]) 
            for item in con.execute("SELECT json FROM DestinyObjectiveDefinition;").fetchall()
        ]
    con.close()
    objective_defns = {item['hash']: item for item in objective_defns}
    player_data = {}
    for raid, hashmap in raid_hashes.items():
        player_data.update({
            raid: {
                'title': hashmap['title'],
                'triumphs': {}
            }
        })
        for key, (triumph, description) in hashmap['records'].items():
            # add Raid: prefix for King's Fall due to Dennis labelling 2 triumphs the same
            if raid == 'King\'s Fall' and 'Trophies' in description:
                triumph = f'Raid: {triumph}'
            record = profile.profile_records.get(key)
            objective_list = record.objectives if record.objectives is not None else record.interval_objectives
            objective_data = [
                (
                    objective.hash,
                    description,
                    key,
                    objective_defns.get(objective.hash)['progressDescription'],
                    objective.complete
                )
                for objective in objective_list
            ]
            player_data[raid]['triumphs'].update({
                triumph: objective_data
            })
    return {bungie_name: player_data}

def init_clan_db(db: Path) -> None:
    '''Generates the Earl Greyders Raid Seal Data Base of Data'''
    create_tables = '''
        BEGIN;
        CREATE TABLE raids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash INTEGER,
            name TEXT,
            seal TEXT
        );
        CREATE TABLE players (
            id INTEGER PRIMARY KEY,
            label TEXT,
            bungie_name TEXT,
            bungie_code INTEGER
        );
        CREATE TABLE progress (
            id INTEGER PRIMARY KEY,
            player INTEGER NOT NULL,
            cheevo INTEGER,
            complete BOOL,
            FOREIGN KEY (player) REFERENCES players(id)
            FOREIGN KEY (cheevo) REFERENCES cheevos(id)
        );
        CREATE TABLE cheevos (
            id INTEGER PRIMARY KEY,
            raid INTEGER NOT NULL,
            name TEXT,
            desc TEXT,
            FOREIGN KEY (id) REFERENCES progress(cheevo),
            FOREIGN KEY (raid) REFERENCES raids(id)
        );
        COMMIT;
    '''
    con = sqlite3.connect(db)
    with con:
        # setup db schema
        con.executescript(create_tables)
        # add player data
        con.executemany(
            "INSERT INTO players(label, bungie_name, bungie_code) VALUES(?, ?, ?)",
            [
                ('Felix', 'Felix', 3964),
                ('Hanzo', 'MrChristian', 4697),
                ('Chuck', 'Chuckm', 8947),
                ('Zrg', 'Spaceballs: The Username', 5169),
                ('Tam', 'Tamarzan', 6907),
                ('Maha', 'Maharunn', 5435),
                ('Polaris', 'Polaris', 7833),
                ('Roland', 'Rolandgunslingr', 8593),
            ]
        )
    con.close()
    return

def get_player_info(db: Path) -> dict:
    '''Get player data from sqlite db'''
    con = sqlite3.connect(db)
    with con:
        player_data = con.execute('''
            SELECT label,bungie_name,bungie_code,id
            FROM players;'''
        ).fetchall()
    con.close()
    assert len(player_data) > 0
    # dict it up
    player_data = {
        pd[0]: (pd[1], pd[2], pd[3])
        for pd in player_data
    }
    return player_data

def insert_raid_cheevos(db: Path, raids: list, cheevos: list) -> None:
    '''Insert Raid and Triumph data to sqlite db'''
    con = sqlite3.connect(db)
    with con:
        # truncate the raids/cheevos tables before inserting new data (probably faster than update checks)
        con.execute("DELETE FROM raids")
        con.executemany("INSERT INTO raids(id, hash, name, seal) VALUES(?, ?, ?, ?)", raids)
        con.execute("DELETE FROM cheevos")
        con.executemany("INSERT INTO cheevos(id, raid, name, desc) VALUES(?, ?, ?, ?)", cheevos)
    con.close()
    return

def insert_progress(db: Path, progress: list) -> None:
    '''Insert player progression to sqlite db'''
    con = sqlite3.connect(db)
    with con:
        # truncate the progress table before inserting new data (probably faster than update checks)
        con.execute("DELETE FROM progress")
        con.executemany("INSERT INTO progress(id, player, cheevo, complete) VALUES(?, ?, ?, ?)", progress)
    con.close()
    return    

async def main():
    '''main loop'''
    # setup clan_data db
    if not CLAN_DATA.exists():
        LOGGER.info('Initialize EGRSDBoD')
        init_clan_db(CLAN_DATA)
    # retrieve our player info from EGRSDBoD
    players = get_player_info(CLAN_DATA)
    # read-only just in case I do a stupid
    hashes = get_raid_hashes(WANTED_SEALS)
    # prepare raid/cheevo manifest data for import to EGRSDBoD
    raid_data = [
        (idx, hashes[raidname]['hash'], raidname, hashes[raidname]['title']['Female'])
        for idx, raidname in enumerate(hashes.keys(), start=1)
    ]
    cheevo_data = [
        (cheevo_id, raid_id, cheevo[0], cheevo[1])
        # DENNIS
        if cheevo != ("King's Fall", 'Trophies from the "King\'s Fall" raid.')
        else (cheevo_id, raid_id, f'Raid: {cheevo[0]}', cheevo[1])
        for raid_id, _, raidname, _ in raid_data
        for cheevo_id, cheevo in hashes[raidname]['records'].items()
    ]
    # slam that info into EGRSDBoD who cares what's already there
    insert_raid_cheevos(CLAN_DATA, raid_data, cheevo_data)
    clan_progress = []
    # TODO: make this parallel somehow
    # TODO: decide if autoincrement or use shitty_idx
    shitty_idx = 1
    for player, (bungie_name, bungie_id, player_sql_id) in players.items():
        LOGGER.info('Pulling data for %s' % player)
        try:
            player_data = await get_player_completion(bungie_name, bungie_id, hashes)
        except Exception as e:
            print(e)
            continue
        # prepare progress data for import to EGRSDBoD
        for seal in WANTED_SEALS:
            for objectives in player_data[bungie_name][seal]['triumphs'].values():
                is_complete = all([o[-1] for o in objectives])
                progress = (
                    shitty_idx,
                    player_sql_id,
                    objectives[0][2], # cheevo hash
                    is_complete
                )
                clan_progress.append(progress)
                shitty_idx += 1
    # save that garbage
    insert_progress(CLAN_DATA, clan_progress)
    return

if __name__ == '__main__':        
    AIO_CLIENT.run(main())
