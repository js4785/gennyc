import main

ENV_DB = 'Dev'


class Recommend:

    def __init__(self, user):
        self.user = user
        self.most_interested = []

    def get_user_interests_with_categories(self):
        db = main.connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute("SELECT tag, category FROM " + ENV_DB + ".UserTags WHERE username='" + self.user.username + "'")
        data = cursor.fetchall()
        db.close()
        return list((i[0], i[1]) for i in data)

    def get_user_interests(self):
        db = main.connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute("SELECT tag FROM " + ENV_DB + ".UserTags WHERE username='" + self.user.username + "'")
        data = cursor.fetchall()
        db.close()

        self.most_interested = sorted([i[0] for i in data])
        return self.most_interested

        # values = main.query_for_survey(self.user)
        # survey_results = []
        # iterresults = iter(values)
        # next(iterresults)

        # for x in iterresults:
        #     if len(x) > 1:
        #         survey_results.append(x)
        #     else:
        #         pass

        # self.most_interested = sorted(survey_results)
        # return self.most_interested


    def get_events(self):
        db = main.connect_to_cloudsql()
        cursor = db.cursor()

        query = """
                SELECT DISTINCT E.eid, E1.ename, E1.description, E1.start_date, E1.end_date, E1.num_cap,
                E1.num_attending, L.lname, L.address_1, E.tag, L.lat, L.lon
                FROM {}.EventTags AS E, {}.UserTags AS U, {}.Events as E1, {}.Locations as L
                WHERE U.username='{}' AND
                    E.tag = U.tag AND
                    E1.eid = E.eid AND
                    E1.lid = L.lid
                """.format(
                        ENV_DB,
                        ENV_DB,
                        ENV_DB,
                        ENV_DB,
                        self.user.username
                    )

        cursor.execute(query)
        data = cursor.fetchall()
        db.close()

        return [i for i in data]


class GroupRecommend:
    def __init__(self, g_id):
        self.g_id = g_id
        self.members = self.get_members()
        self.interests = self.get_group_interests()

    def get_members(self):
        db = main.connect_to_cloudsql()
        cursor = db.cursor()
        query = ("SELECT username from " + ENV_DB + ".Groups WHERE gid='{}'").format(self.g_id)
        cursor.execute(query)
        data = cursor.fetchall()
        db.close()
        return list(i[0] for i in data)

    def get_interests_each_member(self, username):
        db = main.connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute("SELECT tag FROM " + ENV_DB + ".UserTags WHERE username='" + username + "'")
        data = cursor.fetchall()
        db.close()
        return set([i[0] for i in data])

    def get_group_interests(self):
        common_tags = set()
        for mem in self.members:
            if len(common_tags) == 0:
                common_tags = self.get_interests_each_member(mem)
            else:
                common_tags = common_tags.intersection(self.get_interests_each_member(mem))
        return list(common_tags)

    def get_events(self):
        db = main.connect_to_cloudsql()
        cursor = db.cursor()

        result = []
        for tag in self.interests:
            query = """
                    SELECT DISTINCT E.eid, E1.ename, E1.description, E1.start_date, E1.end_date, E1.num_cap,
                    E1.num_attending, L.lname, L.address_1, E.tag, L.lat, L.lon
                    FROM {}.EventTags AS E, {}.UserTags AS U, {}.Events as E1, {}.Locations as L
                    WHERE E.tag = '{}' AND
                        E1.eid = E.eid AND
                        E1.lid = L.lid
                    """.format(
                            ENV_DB,
                            ENV_DB,
                            ENV_DB,
                            ENV_DB,
                            tag
                        )

            cursor.execute(query)
            data = cursor.fetchall()
            result.extend([i for i in data])

        db.close()

        return result
