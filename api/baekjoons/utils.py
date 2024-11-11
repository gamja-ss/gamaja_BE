import requests


def get_boj_profile(bj_id):
    url = f"https://solved.ac/api/v3/user/show?handle={bj_id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "username": data["handle"],
            "tier": data["tier"],
            "solved_count": data["solvedCount"],
            "rating": data["rating"],
        }
    else:
        return None
