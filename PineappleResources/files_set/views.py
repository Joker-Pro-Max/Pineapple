from bson import ObjectId
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FileMeta, Category
from .mongo_models import StoredFile
from .serializers import FileMetaSerializer


# Create your views here.

class FileListView(ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = FileMetaSerializer
    queryset = FileMeta.objects.all().order_by("-create_at")

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "content_type", "created_by"]


class FileUploadView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file_obj = request.FILES.get("file")
        category_uuid = request.data.get("category_uuid", "")

        if not file_obj:
            return Response({"error": "文件不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        category = get_object_or_404(Category, uuid=category_uuid)

        # ✅ 1. 存入 MongoDB GridFS
        mongo_file = StoredFile(
            filename=file_obj.name,
            content_type=file_obj.content_type,
            file_size=file_obj.size
        )
        mongo_file.file.put(file_obj, content_type=file_obj.content_type)  # ✅ 存入 GridFS
        mongo_file.save()

        # ✅ 2. 记录 MySQL 元数据
        file_meta = FileMeta.objects.create(
            category=category,
            filename=file_obj.name,
            content_type=file_obj.content_type,
            file_size=file_obj.size,
            mongo_id=str(mongo_file.id),
        )

        return Response(FileMetaSerializer(file_meta).data, status=status.HTTP_201_CREATED)


class FileRetrieveView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        file_meta = get_object_or_404(FileMeta, uuid=pk)
        mongo_file = StoredFile.objects(id=ObjectId(file_meta.mongo_id)).first()
        if not mongo_file:
            return Response({"error": "文件不存在"}, status=status.HTTP_404_NOT_FOUND)

        grid_file = mongo_file.file.get()
        response = StreamingHttpResponse(grid_file, content_type=file_meta.content_type)
        response["Content-Disposition"] = f'inline; filename="{file_meta.filename}"'
        return response


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
