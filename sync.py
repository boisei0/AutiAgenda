import dropbox
import cPickle
import os

__author__ = 'Rob Derksen (boisei0)'

base_path = os.path.dirname(__file__)


class Sync:
    def __init__(self, app_key, app_secret):
        self._pickle_db_name = os.path.join('data', 'db.pkl')

        app_key = app_key
        app_secret = app_secret

        self.flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

        if os.path.exists(self._pickle_db_name):
            self.client = self._pickle_client_load()
        else:
            self.client = None
        self.uid = None

    def get_auth_url(self):
        return self.flow.start()

    def set_access_token(self, access_token):
        try:
            token, uid = self.flow.finish(access_token)
        except (KeyError, IndexError):  # Strange dropbox... Why shouldn't I fork you and do a complete rewrite :+
            print('Invalid access token')
            return
        self._create_client(token, uid)

    def _create_client(self, access_token, user_id):
        self.client = dropbox.client.DropboxClient(access_token)
        self.uid = user_id
        self._pickle_client_save()

    def _pickle_client_save(self):
        cPickle.dump(self.client, open(self._pickle_db_name, 'wb'))

    def _pickle_client_load(self):
        return cPickle.load(open(self._pickle_db_name, 'rb'))

    def sync_to_dropbox(self, files_list):
        if self.client is None:
            print('Insert access token first')
            return
        for path in files_list:
            with open(path, 'rb') as f:
                if base_path in path:
                    path = path[len(base_path) + 1:]
                self.client.put_file('/{}'.format(path), f)

    def sync_from_dropbox(self, files_list):
        if self.client is None:
            print('Insert access token first')
            return
        for path in files_list:
            if self._file_exists(path):
                out = open(os.path.join(base_path, path), 'wb')
                with self.client.get_file('/{}'.format(path)) as f:
                    out.write(f.read())

    def _file_exists(self, path):
        if self.client is None:
            print('Insert access token first')
            return
        try:
            self.client.metadata(path)
            return True
        except dropbox.rest.ErrorResponse as ex:
            if ex.status == 404:
                return False
            if ex.status == 200:
                return True
            if ex.status == 400:
                return

    def list_files(self, path):
        if self.client is None:
            print('Insert access token first')
            return
        print(self.client.metadata(path))

if __name__ == '__main__':
    db = Sync('', '')
    db.list_files('/')
    # db.sync_to_dropbox([
    #     os.path.join(os.path.join(base_path, 'config'), 'autiagenda.ini'),
    #     os.path.join(os.path.join(base_path, 'config'), 'courses.ini'),
    #     os.path.join(os.path.join(base_path, 'config'), 'courses.json'),
    #     os.path.join(os.path.join(base_path, 'config'), 'datetime.json')
    # ])
    db.sync_from_dropbox(os.path.join('data', 'asdf'))