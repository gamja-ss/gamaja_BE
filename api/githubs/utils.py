import requests
from django.utils import timezone

from .models import Github


def get_github_commits(github_username, github_token):
    query = """
    query($username: String!) {
      user(login: $username) {
        contributionsCollection {
          totalCommitContributions
        }
      }
    }
    """

    variables = {"username": github_username}
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )

        response.raise_for_status()
        data = response.json()
        return data["data"]["user"]["contributionsCollection"][
            "totalCommitContributions"
        ]
    except requests.RequestException as e:
        print(f"GitHub API 요청 실패: 사용자 {github_username}, 에러: {str(e)}")
    except KeyError as e:
        print(f"GitHub API 응답 파싱 실패: 사용자 {github_username}, 에러: {str(e)}")
    except Exception as e:
        print(f"예상치 못한 에러 발생: 사용자 {github_username}, 에러: {str(e)}")

    return None


def set_initial_github_commits(user):
    total_commits = get_github_commits(user.username, user.github_access_token)
    if total_commits is not None:
        user.github_initial_commits = total_commits
        user.github_initial_date = timezone.now().date()
        user.save()

        Github.objects.create(
            user=user, date=user.github_initial_date, commit_num=total_commits
        )
        print(
            f"초기 GitHub 커밋 정보 설정 완료: 사용자 {user.id}, 커밋 수 {total_commits}"
        )
        return True
    return False


def update_user_github_commits(user):
    if not user.github_access_token or not user.username:
        print(f"GitHub 정보 없음: 사용자 {user.id}")
        return None

    total_commits = get_github_commits(user.username, user.github_access_token)
    if total_commits is None:
        return None

    today = timezone.now().date()
    github_record, created = Github.objects.update_or_create(
        user=user, date=today, defaults={"commit_num": total_commits}
    )

    print(
        f"GitHub 커밋 수 업데이트 성공: 사용자 {user.username}, 커밋 수 {total_commits}"
    )
    return github_record
