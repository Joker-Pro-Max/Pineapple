import hashlib
import os
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import mimetypes
from .models import FileMeta, Category
from .mongo_models import StoredFile
from .serializers import FileMetaSerializer


# Create your views here.


def save_file_and_get_hash(file_obj):
    sha256 = hashlib.sha256()
    file_path = os.path.join(settings.MEDIA_ROOT, 'PDFS', file_obj.name)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)
            sha256.update(chunk)

    return sha256.hexdigest(), file_path


class FileListView(ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = FileMetaSerializer
    queryset = FileMeta.objects.all().order_by("-create_at")

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "content_type", "created_by"]


class FileUploadView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        category_id = request.data.get('category')

        if not file or not category_id:
            return Response({"detail": "file 和 category 必填"}, status=400)

        category = Category.objects.filter(uuid=category_id).first()
        if not category:
            return Response({"detail": "分类不存在"}, status=404)

        file_hash, file_path = save_file_and_get_hash(file)

        # 如果已经存在则直接返回已有文件元信息
        instance = FileMeta.objects.filter(file_hash=file_hash).first()
        if instance:
            return Response(FileMetaSerializer(instance).data)

        instance = FileMeta.objects.create(
            category=category,
            created_by=None,
            filename=file.name,
            content_type=file.content_type,
            file_size=file.size,
            file_path=str(file_path).replace(str(settings.MEDIA_ROOT), '/media'),
            file_hash=file_hash,
        )
        return Response(FileMetaSerializer(instance).data)



class FileRetrieveView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        file_meta = get_object_or_404(FileMeta, pk=pk)
        file_path = file_meta.file_path.lstrip('/')

        mime, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, 'rb'), content_type=mime)


class FileDeleteView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, uuid):
        file_meta = get_object_or_404(FileMeta, uuid=uuid)

        # ✅ 删除 MongoDB 文件
        mongo_file = StoredFile.objects(id=file_meta.mongo_id).first()
        if mongo_file:
            mongo_file.file.delete()
            mongo_file.delete()

        # ✅ 删除 MySQL 记录
        file_meta.delete()

        return Response({"message": "文件已删除"}, status=status.HTTP_204_NO_CONTENT)
