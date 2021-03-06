from allauth.socialaccount.models import SocialAccount, SocialToken
import dropbox
import os
from django.core.exceptions import PermissionDenied


class DropboxAdapter():
    def download(self, localPath, remotePath, user, uniqueBatchId):
        token_query = user.profile.tokens.filter(app__provider='dropbox')

        if not token_query.exists():
            raise PermissionDenied('No dropbox token found.')

        token = token_query.get().token

        systemProvider = remotePath.split('/')[1]
        systemId = remotePath.split('/')[2]
        remoteFilePath = '/'.join([''] + remotePath.split('/')[3:])
        downloadDirectory = '/transient/%s/' % uniqueBatchId
        fullLocalPath = downloadDirectory + localPath

        if not os.path.exists(downloadDirectory):
            os.makedirs(downloadDirectory)

        fullLocalDir = '/'.join(fullLocalPath.split('/')[0:-1] + [''])
        if not os.path.exists(fullLocalDir):
            os.makedirs(fullLocalDir)

        dbx = dropbox.Dropbox(token)
        dbx.files_download_to_file(fullLocalPath, remoteFilePath)

    def upload(self, localPath, remotePath, user, uniqueBatchId):
        token_query = user.profile.tokens.filter(app__provider='dropbox')

        if not token_query.exists():
            raise PermissionDenied('No dropbox token found.')

        token = token_query.get().token
        dbx = dropbox.Dropbox(token)

        systemProvider = remotePath.split('/')[1]
        systemId = remotePath.split('/')[2]
        remoteFilePath = '/'.join([''] + remotePath.split('/')[3:])
        fullLocalPath = '/transient/%s/' % uniqueBatchId + localPath

        file_size = os.path.getsize(fullLocalPath)
        CHUNK_SIZE = 4 * 1024 * 1024

        f = open(fullLocalPath, "rb")

        if file_size <= CHUNK_SIZE:
            dbx.files_upload(f.read(), remoteFilePath)
        else:
            upload_session = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
            cursor = dropbox.files.UploadSessionCursor(
                session_id=upload_session.session_id,
                offset=f.tell()
            )
            commit = dropbox.files.CommitInfo(path=remoteFilePath)

            while f.tell() < file_size:
                if (file_size - f.tell()) <= CHUNK_SIZE:
                    dbx.files_upload_session_finish(
                        f.read(CHUNK_SIZE),
                        cursor,
                        commit
                    )
                else:
                    dbx.files_upload_session_append(
                        f.read(CHUNK_SIZE),
                        cursor.session_id,
                        cursor.offset
                    )
                    cursor.offset = f.tell()
                    print(cursor.offset)

        f.close()

    def list_directory(self, path, user):
        token_query = user.profile.tokens.filter(app__provider='dropbox')

        if not token_query.exists():
            raise PermissionDenied('No dropbox token found.')

        token = token_query.get().token
        dbx = dropbox.Dropbox(token)

        systemProvider = path.split('/')[1]
        systemId = path.split('/')[2]
        directoryPath = '/'.join([''] + path.split('/')[3:])

        response = dbx.files_list_folder(directoryPath)
        print(response)

        return {
            'directories': [
                '/'.join(path.split('/')[0:3]) + d.path_display + '/'
                for d in
                filter(lambda x: isinstance(x, dropbox.files.FolderMetadata), response.entries)
            ],
            'files': [
                '/'.join(path.split('/')[0:3]) + f.path_display
                for f in
                filter(lambda x: isinstance(x, dropbox.files.FileMetadata), response.entries)
            ]
        }

    def create_directory(self, path, user):
        pass