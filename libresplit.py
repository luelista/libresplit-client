
import requests

class LibreSplitClient(object):
    def __init__(self, api_root, token):
        self.base_url = api_root
        self.token = token
        self.headers = {
                'Authorization': 'Bearer '+token,
                'Accept': 'application/json'
        }

    def get_group_by_id(self, id):
        return LibreSplitGroup(self, '/group/' + id)

    def get_groups(self):
        out = []
        for g in self._get('/groups', {})['groups']:
            go = LibreSplitGroup(self, '/group/' + g['id'])
            go._info = g
            out.append(go)
        return out

    def _get(self, url, params):
        resp = requests.get(self.base_url + url, headers=self.headers, params=params)

        if resp.status_code != 200:
            raise Exception("Return code not 200: " + resp.content.decode("utf-8"))

        return resp.json()

    def _req(self, method, url, payload):
        resp = requests.request(method, self.base_url + url, headers=self.headers, data=payload)

        if resp.status_code != 200:
            print("Request failed")
            print("Payload was: ", payload)
            raise Exception("Return code not 200: " + resp.content.decode("utf-8"))

        return resp.json()


class LibreSplitGroup(object):
    def __init__(self, client, url):
        self.client = client
        self.url = url
        self._info = None
        self._expenses = None

    def __str__(self):
        return self.get_info()['name']

    def fetch(self):
        resp = self.client._get(self.url, {})
        self._info = resp['group']
        self._expenses = resp['expenses']

    def get_info(self):
        if self._info == None:
            self.fetch()
        return self._info

    def get_expenses(self):
        if self._expenses == None:
            self.fetch()
        return self._expenses

    def add_expense(self, date, who_paid, amount, description, split):
        payload = { 'split[' + str(k) + ']' : v for (k,v) in split.iteritems() }
        payload['who_paid'] = who_paid,
        payload['amount'] = amount,
        payload['description'] = description,
        payload['date'] = date
        response = self.client._req('POST', self.url + '/expenses', payload)
        if response['success'] != True:
            raise Exception("add_expense returned error message: "+response['msg'])
        return response['id']


def fairsplit(amount, people):
    amount = int(amount*100)
    splitam = { p: int(amount/3) for p in people }
    while sum(splitam.values()) < amount:
        splitam[random.choice(splitam.keys())] += 1
    return splitam


