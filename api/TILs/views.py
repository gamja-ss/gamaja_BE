import uuid

import boto3
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import TIL, TILImage
from .serializers import TILDetailSerializer, TILListSerializer, TILSerializer


class UploadTempImagesAPI(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        images = request.FILES.getlist("images")
        if not images:
            return Response(
                {"error": "이미지가 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        s3_client = boto3.client("s3")
        uploaded_images = []

        for image in images:
            file_name = f"temp/{uuid.uuid4()}/{image.name}"

            try:
                s3_client.upload_fileobj(
                    image, settings.AWS_STORAGE_BUCKET_NAME, file_name
                )
                image_url = f"{settings.MEDIA_URL}{file_name}"

                temp_image = TILImage.objects.create(TIL=None, image=image_url)
                uploaded_images.append(
                    {"image_id": temp_image.id, "image_url": image_url}
                )

            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(uploaded_images, status=status.HTTP_201_CREATED)


class DeleteTempImagesAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TILImage.objects.all()

    def delete(self, request, *args, **kwargs):
        image_ids = request.data.get("image_ids", [])

        if not image_ids:
            return Response(
                {"error": "삭제할 이미지 ID가 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(
            Q(id__in=image_ids) & Q(TIL__isnull=True) & Q(is_temporary=True)
        )
        s3_client = boto3.client("s3")

        deleted_ids = []
        for image in queryset:
            try:
                key = image.image.split("/", 3)[-1]
                s3_client.delete_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key
                )
                deleted_ids.append(image.id)
                image.delete()
            except Exception as e:
                print(f"Error deleting image {image.id}: {str(e)}")

        if len(deleted_ids) != len(image_ids):
            not_deleted = set(image_ids) - set(deleted_ids)
            return Response(
                {
                    "message": "일부 이미지가 삭제되지 않았습니다.",
                    "deleted_ids": deleted_ids,
                    "not_deleted_ids": list(not_deleted),
                },
                status=status.HTTP_PARTIAL_CONTENT,
            )

        return Response(
            {
                "message": "모든 이미지가 성공적으로 삭제되었습니다.",
                "deleted_ids": deleted_ids,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["TIL"],
    summary="TIL 작성",
    description="새로운 TIL을 작성합니다.",
    responses={
        201: OpenApiResponse(response=TILSerializer, description="TIL 작성 성공"),
        400: OpenApiResponse(description="잘못된 요청"),
    },
)
class CreateTILAPI(generics.CreateAPIView):
    serializer_class = TILSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def perform_create(self, serializer):
        TIL = serializer.save(user=self.request.user)
        image_ids = self.request.data.get("image_ids", [])
        try:
            self.process_images(TIL, image_ids)
        except Exception as e:
            # 오류 발생 시 트랜잭션 롤백 및 예외 발생
            transaction.set_rollback(True)
            raise serializers.ValidationError(f"이미지 처리 중 오류 발생: {str(e)}")

    def process_images(self, TIL, image_ids):
        for image_id in image_ids:
            try:
                image = TILImage.objects.get(id=image_id, is_temporary=True)
                image.TIL = TIL
                image.is_temporary = False
                # 원본 이미지의 키 추출
                original_key = image.image.replace(settings.MEDIA_URL, "")
                # 새 경로 생성
                new_key = f'til/{TIL.id}/{original_key.split("/")[-1]}'

                s3_client = boto3.client("s3")
                s3_client.copy_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    CopySource={
                        "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                        "Key": original_key,
                    },
                    Key=new_key,
                )
                s3_client.delete_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=original_key,
                )
                image.image = f"https://{settings.MEDIA_URL}/{new_key}"
                image.save()
            except TILImage.DoesNotExist:
                raise serializers.ValidationError(
                    f"이미지 ID {image_id}를 찾을 수 없습니다."
                )
            except Exception as e:
                raise serializers.ValidationError(f"이미지 처리 중 오류 발생: {str(e)}")


@extend_schema(
    tags=["TIL"],
    summary="TIL 수정",
    description="기존 TIL을 수정합니다.",
    responses={
        200: OpenApiResponse(response=TILSerializer, description="TIL 수정 성공"),
        400: OpenApiResponse(description="잘못된 요청"),
        403: OpenApiResponse(description="권한 없음"),
        404: OpenApiResponse(description="TIL을 찾을 수 없음"),
    },
)
class UpdateTILAPI(generics.UpdateAPIView):
    serializer_class = TILSerializer
    permission_classes = [IsAuthenticated]
    queryset = TIL.objects.all()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"error": "이 TIL을 수정할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            response = super().update(request, *args, **kwargs)

            image_ids = request.data.get("image_ids", [])
            self.process_images(instance, image_ids)

            return response
        except Exception as e:
            transaction.set_rollback(True)
            raise serializers.ValidationError(f"TIL 업데이트 중 오류 발생: {str(e)}")

    def process_images(self, TIL, image_ids):
        # 기존 이미지 중 새로운 image_ids에 없는 것들을 삭제
        images_to_delete = TIL.images.exclude(id__in=image_ids)
        for image in images_to_delete:
            self.delete_image_from_s3(image.image)
        images_to_delete.delete()

        for image_id in image_ids:
            try:
                image = TILImage.objects.get(id=image_id)
                if image.TIL is None:
                    # 새로 추가된 이미지
                    image.TIL = TIL
                    image.is_temporary = False
                    new_path = f'til/{TIL.id}/{image.image.split("/")[-1]}'
                    self.move_image_in_s3(image.image, new_path)
                    image.image = f"https://{settings.MEDIA_URL}/{new_path}"
                    image.save()
                elif image.TIL != TIL:
                    # 다른 TIL에서 가져온 이미지
                    return Response(
                        {"error": "이미지는 다른 TIL에 속해 있습니다."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except TILImage.DoesNotExist:
                pass

    def delete_image_from_s3(self, image_url):
        s3_client = boto3.client("s3")
        key = image_url.replace(settings.MEDIA_URL, "")
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)

    def move_image_in_s3(self, old_path, new_path):
        s3_client = boto3.client("s3")
        s3_client.copy_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            CopySource={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": old_path.replace(settings.MEDIA_URL, ""),
            },
            Key=new_path,
        )
        s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=old_path.replace(settings.MEDIA_URL, ""),
        )


@extend_schema(
    tags=["TIL"],
    summary="TIL 삭제",
    description="TIL을 삭제합니다.",
    responses={
        204: OpenApiResponse(description="TIL 삭제 성공"),
        403: OpenApiResponse(description="권한 없음"),
        404: OpenApiResponse(description="TIL을 찾을 수 없음"),
    },
)
class DeleteTILAPI(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = TIL.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"error": "이 TIL을 삭제할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        s3_client = boto3.client("s3")
        for image in instance.images.all():
            s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=image.image.replace(settings.MEDIA_URL, ""),
            )

        return super().destroy(request, *args, **kwargs)


class TILPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserTILListView(generics.ListAPIView):
    serializer_class = TILListSerializer
    permission_classes = [AllowAny]
    pagination_class = TILPagination
    queryset = TIL.objects.all().order_by("-created_at")


class TILDetailView(generics.RetrieveAPIView):
    queryset = TIL.objects.all()
    serializer_class = TILDetailSerializer
    permission_classes = [AllowAny]
