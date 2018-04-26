import datetime

import main

ENV_DB = 'Dev'


class Recommend:
    """Class to recommend events to users.

    Gets user interests based on categories from the database and events corresponding to interests.
    """
    def __init__(self, user):
        self.user = user
        self.most_interested = []

    def get_user_interests_with_categories(self):
        """Gets user interests from categories.

        :return: list of user interests.
        """
        database = main.connect_to_cloudsql()
        cursor = database.cursor()
        cursor.execute("SELECT tag, category FROM " + ENV_DB +
                       ".UserTags WHERE username='" + self.user.username + "'")
        data = cursor.fetchall()
        database.close()
        return list((i[0], i[1]) for i in data)

    def get_user_interests(self):
        """Gets user interests from tags.

        :return: None.
        """
        database = main.connect_to_cloudsql()
        cursor = database.cursor()
        cursor.execute("SELECT tag FROM " + ENV_DB +
                       ".UserTags WHERE username='" + self.user.username + "'")
        data = cursor.fetchall()
        database.close()

        self.most_interested = sorted([i[0] for i in data])
        return self.most_interested

    def get_events(self):
        """Gets all events based on username.

        :return: List of data.
        """
        database = main.connect_to_cloudsql()
        cursor = database.cursor()

        query = """
                SELECT DISTINCT E.eid, E1.ename, E1.description,
                E.category, E1.start_date, E1.end_date, E1.num_cap,
                E1.num_attending, L.lname, L.address_1, E.tag, L.lat, L.lon
                FROM {}.EventTags AS E, {}.UserTags AS U, {}.Events as E1, {}.Locations as L
                WHERE U.username='{}' AND
                    E.tag = U.tag AND
                    E1.eid = E.eid AND
                    E1.lid = L.lid AND
                    E1.start_date >= {}
                ORDER by E1.start_date
                """.format(
                    ENV_DB,
                    ENV_DB,
                    ENV_DB,
                    ENV_DB,
                    self.user.username,
                    str(datetime.date.today())
                    )

        cursor.execute(query)
        data = cursor.fetchall()
        database.close()

        return [i for i in data]


class GroupRecommend:
    """Class to recommend events to groups.

    Gets interests of each member and merges into similar interests.
    """
    def __init__(self, g_id):
        self.g_id = g_id
        self.members = self.get_members()
        self.interests = self.get_group_interests()

    def get_members(self):
        """Gets members of the group.

        :return: List of members.
        """
        database = main.connect_to_cloudsql()
        cursor = database.cursor()
        query = ("SELECT username from " + ENV_DB + ".Groups WHERE gid='{}'").format(self.g_id)
        cursor.execute(query)
        data = cursor.fetchall()
        database.close()
        return list(i[0] for i in data)

    def get_interests_each_member(self, username):
        """Gets interests of each individual member of the group.

        :param username: String username.
        :return: Set of interests for each member.
        """
        database = main.connect_to_cloudsql()
        cursor = database.cursor()
        cursor.execute("SELECT tag FROM " + ENV_DB + ".UserTags WHERE username='" + username + "'")
        data = cursor.fetchall()
        database.close()
        return set([i[0] for i in data])

    def get_group_interests(self):
        """Gets group's interests after pulling each member's interests.

        :return: List of common interests for the group.
        """
        common_tags = set()
        for mem in self.members:
            if len(common_tags) == 0:
                common_tags = self.get_interests_each_member(mem)
            else:
                common_tags = common_tags.intersection(self.get_interests_each_member(mem))
        return list(common_tags)

    def get_events(self):
        """Gets events for common tags.

        :return: List of events with common tags for each group.
        """
        database = main.connect_to_cloudsql()
        cursor = database.cursor()

        result = []
        for tag in self.interests:
            query = """
                    SELECT DISTINCT E.eid, E1.ename, E1.description,
                    E.category, E1.start_date, E1.end_date, E1.num_cap,
                    E1.num_attending, L.lname, L.address_1, E.tag, L.lat, L.lon
                    FROM {}.EventTags AS E, {}.UserTags AS U, {}.Events as E1, {}.Locations as L
                    WHERE E.tag = '{}' AND
                        E1.eid = E.eid AND
                        E1.lid = L.lid AND
                        E1.start_date > {}
                    ORDER by E1.start_date
                    """.format(
                        ENV_DB,
                        ENV_DB,
                        ENV_DB,
                        ENV_DB,
                        tag,
                        str(datetime.date.today())
                        )

            cursor.execute(query)
            data = cursor.fetchall()
            result.extend([i for i in data])

        database.close()

        return result
