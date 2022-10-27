import json
import logging
import sqlite3
from os import getenv
from pathlib import Path

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
    'King\'s Fall',
#    'Last Wish',
#    'Vow of the Disciple'
]
# Label, (Bungie Name, Bungie Code)
PLAYERS = {
    'Felix': ('Felix', 3964),
    'Hanzo': ('MrChristian', 4697),
    'Chuck': ('Chuckm', 8947),
    'Zrg': ('Spaceballs: The Username', 5169),
    'Tam': ('Tamarzan', 6907),
    'Maha': ('Maharunn', 5435),
    'Polaris': ('Polaris', 7833),
    'Roland': ('Rolandgunslingr', 8593),
}
MANIFEST_DATA = Path(__file__).parent / 'manifest.sqlite3'
OUT_JSON = Path(__file__).parent / 'clan_data.json'
AIO_CLIENT = aiobungie.Client(getenv('API_KEY'))


def get_raid_hashes(wanted_seals, cursor):
    '''Uses the manifest to retrieve the item hashes for the seals we want'''
    raid_hashes = {}
    # load the sql result (actually a json blob) as dict
    presentation_nodes = [
        json.loads(item[0])
        for item in cursor.execute("SELECT json FROM DestinyPresentationNodeDefinition;").fetchall()
    ]
    #  make the sql result nicer to use later
    presentation_nodes = {node['hash']: node for node in presentation_nodes}
    record_defns = [
        json.loads(item[0])
        for item in cursor.execute("SELECT json FROM DestinyRecordDefinition;").fetchall()
    ]
    record_defns = {record['hash']: record for record in record_defns}
    seals_item = [
        item for item in presentation_nodes.values()
        if item['displayProperties']['name'] == 'Seals'
    ]
    assert len(seals_item) == 1
    seals_item = seals_item[0]
    for seal in seals_item['children']['presentationNodes']:
        nodehash = seal['presentationNodeHash']
        nodematch = presentation_nodes.get(nodehash)
        if nodematch['displayProperties']['name'] in wanted_seals:
            raid_hashes.update({
                nodematch['displayProperties']['name']: {
                    'records': {
                        record['recordHash']: (
                            record_defns.get(
                                record['recordHash']
                            )['displayProperties']['name'],
                            record_defns.get(
                                record['recordHash']
                            )['displayProperties']['description']
                        )
                        for record in nodematch['children']['records']
                    },
                    'title': record_defns.get(
                        nodematch['completionRecordHash']
                    )['titleInfo']['titlesByGender']
                }
            })
    return raid_hashes

async def get_player_completion(bungie_name, bungie_code, raid_hashes, cursor):
    '''Uses the item hashes with player data to get completion information'''
    async with AIO_CLIENT.rest:
        # identify the main membershiptype (i.e. the one you picked during cross-save setup)
        profiles = await AIO_CLIENT.fetch_player(bungie_name, bungie_code)
        main_membershiptype = list(set([f.crossave_override for f in profiles])).pop()
        # get the actual profile that bungie-api will be happy to work with
        main_profile = await AIO_CLIENT.fetch_player(bungie_name, bungie_code, main_membershiptype)
        profile_id = main_profile.pop()
        profile = await profile_id.fetch_self_profile([aiobungie.ComponentType.RECORDS])
    player_data = {}
    objective_defns = [
        json.loads(item[0]) 
        for item in cursor.execute("SELECT json FROM DestinyObjectiveDefinition;").fetchall()
    ]
    objective_defns = {item['hash']: item for item in objective_defns}
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
                    description,
                    objective_defns.get(objective.hash)['progressDescription'],
                    objective.complete
                )
                for objective in objective_list
            ]
            player_data[raid]['triumphs'].update({
                triumph: objective_data
            })
    return {bungie_name: player_data}

async def main():
    '''main loop'''
    con = sqlite3.connect(f'file:{MANIFEST_DATA}?mode=ro', uri=True)
    cursor = con.cursor()    
    hashes = get_raid_hashes(WANTED_SEALS, cursor)
    clan_data = {}
    # TODO:make this parallel somehow
    for player, (bungie_name, bungie_id) in PLAYERS.items():
        LOGGER.info('Pulling data for %s' % player)
        try:
            player_data = await get_player_completion(bungie_name, bungie_id, hashes, cursor)
        except Exception as e:
            print(e)
            continue
        clan_data[player] = player_data[bungie_name]
    cursor.close()
    con.close()
    with OUT_JSON.open('w') as f:
        f.write(json.dumps(clan_data, indent=2))
    LOGGER.info('Dumped to %s' % OUT_JSON)
    return

if __name__ == '__main__':
    AIO_CLIENT.run(main())
