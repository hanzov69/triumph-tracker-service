import json
import logging
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

MANIFEST_DATA = Path(__file__).parent / 'manifest.json'
OUT_JSON = Path(__file__).parent / 'clan_data.json'
AIO_CLIENT = aiobungie.Client(getenv('API_KEY'))

def load_manifest():
    '''does 1 thing'''
    with MANIFEST_DATA.open() as f:
        data = json.load(f)
    return data

def get_raid_hashes(wanted_seals, manifest):
    '''Uses the manifest to retrieve the item hashes for the seals we want'''
    raid_hashes = {}
    seals_item = [
        item for item in manifest['DestinyPresentationNodeDefinition'].values()
        if item['displayProperties']['name'] == 'Seals'
    ]
    assert len(seals_item) == 1
    seals_item = seals_item[0]
    for seal in seals_item['children']['presentationNodes']:
        nodehash = seal['presentationNodeHash']
        nodematch = manifest['DestinyPresentationNodeDefinition'].get(str(nodehash))
        if nodematch['displayProperties']['name'] in wanted_seals:
            raid_hashes.update({
                nodematch['displayProperties']['name']: {
                    'records': {
                        record['recordHash']: (
                            manifest['DestinyRecordDefinition'].get(
                                str(record['recordHash'])
                            )['displayProperties']['name'],
                            manifest['DestinyRecordDefinition'].get(
                                str(record['recordHash'])
                            )['displayProperties']['description']
                        )
                        for record in nodematch['children']['records']
                    },
                    'title': manifest['DestinyRecordDefinition'].get(
                        str(nodematch['completionRecordHash'])
                    )['titleInfo']['titlesByGender']
                }
            })
    return raid_hashes
    
async def get_player_completion(bungie_name, bungie_code, raid_hashes, manifest):
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
                    manifest['DestinyObjectiveDefinition'].get(str(objective.hash))['progressDescription'],
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
    manifest = load_manifest()
    hashes = get_raid_hashes(WANTED_SEALS, manifest)
    clan_data = {}
    # TODO:make this parallel somehow
    for player, (bungie_name, bungie_id) in PLAYERS.items():
        LOGGER.info('Pulling data for %s' % player)
        try:
            player_data = await get_player_completion(bungie_name, bungie_id, hashes, manifest)
        except Exception as e:
            print(e)
            continue
        clan_data[player] = player_data[bungie_name]
    with OUT_JSON.open('w') as f:
        f.write(json.dumps(clan_data, indent=2))
    LOGGER.info('Dumped to %s' % OUT_JSON)

if __name__ == '__main__':
    AIO_CLIENT.run(main())
