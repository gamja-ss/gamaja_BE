import requests
from coins.models import Coin
from django.db import transaction
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
        user.baekjoon_initial_solved = profile["solved"]
        user.baekjoon_initial_score = profile["score"]
        user.baekjoon_initial_date = timezone.now().date()
        user.save()

        Baekjoon.objects.create(
            user=user,
            date=user.baekjoon_initial_date,
            solved=profile["solved"],
            score=profile["score"],
            tier=profile["tier"],
        )

        print(f"초기 Baekjoon 정보 설정 완료: 사용자 {user.username}")
        return True
    return False


@transaction.atomic
def update_user_baekjoon_info(user):
    if not user.baekjoon_id:
        print(f"Baekjoon 정보 없음: 사용자 {user.id}")
        return None

    profile = get_boj_profile(user.baekjoon_id)
    if profile is None:
        return None

    now_score = profile["score"]
    now = timezone.now()

    previous_baekjoon = Baekjoon.objects.filter(user=user).order_by("-date").first()

    if previous_baekjoon:
        score_difference = now_score - previous_baekjoon.score
        if score_difference > 0:
            coins_earned = score_difference
            exp_earned = score_difference

            Coin.objects.create(
                user=user,
                verb="baekjoon",
                coins=coins_earned,
                timestamp=now,
            )

            user.increase_exp(exp_earned)

    baekjoon, created = Baekjoon.objects.update_or_create(
        user=user,
        date=now.date(),
        defaults={
            "solved": profile["solved"],
            "score": now_score,
            "tier": profile["tier"],
        },
    )

    print(f"Baekjoon 정보 업데이트 성공: 사용자 {user.username}")
    return baekjoon
