from passlib.hash import sha256_crypt


def hashpasswd(plain_password):
    return sha256_crypt.encrypt(plain_password)


# def checkpasswd(plain_password, hash_user):
#     if hashed == hash_user:
#         return True
#     else:
#         return False
