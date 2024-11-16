import requests
from django.conf import settings
from django.utils import timezone

from .models import Programmers

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
                solved = user_data.get("codingTest", {}).get("solved")
                rank = user_data.get("ranking", {}).get("rank")

                return {
                    "level": level,
                    "score": score,
                    "solved": solved,
                    "rank": rank,
                }
            else:
                print(f"사용자 정보 요청 실패: {user_response.status_code}")
        else:
            print(f"로그인 실패: {login_response.status_code}")
    except Exception as e:
        print(f"에러 발생: {str(e)}")
    return None


def set_initial_programmers_info(user):
    programmers_data = get_programmers_data(
        user.programmers_id, user.programmers_password
    )
    if programmers_data is not None:
        user.programmers_initial_score = (programmers_data["score"],)
        user.programmers_initial_solved = (programmers_data["solved"],)
        user.programmers_initial_date = timezone.now().date()
        user.save()

        Programmers.objects.create(
            user=user,
            date=user.programmers_initial_date,
            defaults={
                "level": programmers_data["level"],
                "score": programmers_data["score"],
                "solved": programmers_data["solved"],
                "rank": programmers_data["rank"],
            },
        )
        print(f"초기 Programmers 정보 설정 완료: 사용자 {user.username}")
        return True
    return False


def update_user_programmers_info(user):
    if not user.programmers_id and user.programmers_password:
        print(f"Programmers 정보 없음: 사용자 {user.id}")
        return None

    programmers_data = get_programmers_data(
        user.programmers_id, user.programmers_password
    )
    if programmers_data is None:
        return None

    today = timezone.now().date()
    programmers, created = Programmers.objects.update_or_create(
        user=user,
        date=today,
        defaults={
            "level": programmers_data["level"],
            "score": programmers_data["score"],
            "solved": programmers_data["solved"],
            "rank": programmers_data["rank"],
        },
    )

    print(f"Programmers 커밋 수 업데이트 성공: 사용자 {user.username}")
    return programmers
