import jwt
import requests

# -> openssl rand -hex 32
SECRET_KEY = "<secret_key>"


def create_access_token(payload: dict):
    to_encode = payload.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def main():
    payload = {"user": {"username": "user123", "role": "admin"}}
    encoded_token = create_access_token(payload)
    decoded_token = jwt.decode(encoded_token, SECRET_KEY, algorithms=["HS256"])

    response = requests.get(
        "http://localhost:5005/conversations/default/tracker",
        headers={"Authorization": "Bearer {}".format(encoded_token)},
    )

    print("\nAccess token: ", encoded_token)
    print("\nDecoded token: ", decoded_token)
    print(response.text)


if __name__ == "__main__":
    main()
