import requests
from django.conf import settings

PROGRAMMERS_SIGN_IN = "https://programmers.co.kr/api/v1/account/sign-in"
PROGRAMMERS_USER_RECORD = "https://programmers.co.kr/api/v1/users/record"


def get_programmers_data(programmers_id, programmers_password):
    try:
        # 로그인 요청
        login_payload = {
            "user": {"email": programmers_id, "password": programmers_password}
        }

        # 로그인 요청 보내기
        login_response = requests.post(PROGRAMMERS_SIGN_IN, json=login_payload)

        if login_response.status_code == 200:
            # 로그인 성공, 쿠키를 이용하여 사용자 정보 요청
            cookies = login_response.cookies
            user_response = requests.get(PROGRAMMERS_USER_RECORD, cookies=cookies)

            if user_response.status_code == 200:
                # 사용자 정보 가져오기 성공
                user_data = user_response.json()

                # 필요한 정보 추출
                level = user_data.get("skillCheck", {}).get("level")
                score = user_data.get("ranking", {}).get("score")
                solved_tests = user_data.get("codingTest", {}).get("solved")
                rank = user_data.get("ranking", {}).get("rank")

                return {
                    "level": level,
                    "score": score,
                    "solved_tests": solved_tests,
                    "rank": rank,
                }
            else:
                print(f"사용자 정보 요청 실패: {user_response.status_code}")
        else:
            print(f"로그인 실패: {login_response.status_code}")
    except Exception as e:
        print(f"에러 발생: {str(e)}")
    return None
