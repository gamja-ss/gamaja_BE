import requests
from django.utils import timezone

from .models import Baekjoon


def get_boj_profile(bj_id):
    url = f"https://solved.ac/api/v3/user/show?handle={bj_id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "username": data["handle"],
            "tier": data["tier"],
            "solved": data["solvedCount"],
            "score": data["rating"],
            "bio": data["bio"],
        }
    else:
        return None


def set_initial_baekjoon_info(user):
    profile = get_boj_profile(user.baekjoon_id)
    if profile is not None:
        user.baekjoon_initial_sovled = profile["solved"]
        user.baekjoon_initial_score = profile["score"]
        user.baekjoon_initial_date = timezone.now().date()
        user.save()

        Baekjoon.objects.create(
            user=user,
            date=user.baekjoon_initial_date,
            defaults={
                "solved": profile["solved"],
                "score": profile["score"],
                "tier": profile["tier"],
            },
        )

        print(f"초기 Baekjoon 정보 설정 완료: 사용자 {user.username}")
        return True
    return False


def update_user_baekjoon_info(user):
    if not user.baekjoon_id:
        print(f"Baekjoon 정보 없음: 사용자 {user.id}")
        return None

    profile = get_boj_profile(user.baekjoon_id)
    if profile is None:
        return None

    today = timezone.now().date()
    baekjoon, created = Baekjoon.objects.update_or_create(
        user=user,
        date=today,
        defaults={
            "solved": profile["solved"],
            "score": profile["score"],
            "tier": profile["tier"],
        },
    )

    print(f"Baekjoon 커밋 수 업데이트 성공: 사용자 {user.username}")
    return baekjoon
