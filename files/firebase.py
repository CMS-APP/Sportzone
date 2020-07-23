import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('sz_firebase_admin.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


class FireBase():
    def check_username(self, username):
        username_free = True
        docs = db.collection('user').where('username', '==', f'{username}').stream()
        for doc in docs:
            username_free = False
            print(doc.id, doc.to_dict())
        return (username_free)

    def check_email(self, email):
        email_free = True
        docs = db.collection('user').where('email', '==', f'{email.lower()}').stream()
        for doc in docs:
            email_free = False
            print(doc.id, doc.to_dict())
        return (email_free)

    def sign_in(self):
        pass
