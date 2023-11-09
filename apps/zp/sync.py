# sync.py
import logging
import time

from apps.teams.models import Team
from apps.zp.fetch import ZPSession
from apps.zp.models import Profile, TeamRiders


class TeamRidersUpdater:
    def __init__(self):
        self.zps = ZPSession()
        self.try_count = 0

    def update_teamriders(self):
        zp_team_ids = Team.objects.values_list("zp_id", flat=True)
        for zp_team_id in zp_team_ids:
            logging.info(f"Get team data: {zp_team_id}")
            try:
                data_set = self.zps.get_api(id=zp_team_id, api="team_riders")
                data_set = data_set["team_riders"]["data"]
                if len(data_set) > 0:
                    tr, created = TeamRiders.objects.get_or_create(zp_id=zp_team_id, team_riders=data_set)
                    logging.info(f"Created new TeamRider entry: {created} for team: {zp_team_id}")

            except:
                self.try_count += 1
                logging.info(f"Retry get team data: {zp_team_id}")
                if self.try_count >= 4:
                    logging.warning(f"Retry get team data: {zp_team_id}")
                    break
            time.sleep(5 + self.try_count * 30)


class ProfilesFromTeams:
    def add_profiles_from_teams(self):
        zp_team_riders = TeamRiders.objects.all()
        for team in zp_team_riders:
            for rider in team.team_riders:
                Profile.objects.get_or_create(zp_id=rider["zwid"])


class ZPProfileUpdater:
    def __init__(self):
        self.zps = ZPSession()
        self.try_count = 0

    def update_profiles(self):
        zp_profiles = Profile.objects.all()
        for zp_profile in zp_profiles:
            try:
                data_set = self.zps.get_api(id=zp_profile.zp_id, api="profile_profile")
                data_set = data_set["profile_profile"]["data"]
                if len(data_set) > 0:
                    zp_profile.profile = data_set
                    zp_profile.save()
            except:
                self.try_count += 1
            if self.try_count >= 4:
                break
            time.sleep(5 + self.try_count * 30)
