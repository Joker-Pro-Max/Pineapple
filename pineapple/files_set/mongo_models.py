from mongoengine import Document, StringField, FileField, DateTimeField, IntField
import datetime

class StoredFile(Document):
    filename = StringField(required=True)
    # 🔹 文件名（原始名称），供下载或显示使用

    content_type = StringField(required=True)
    # 🔹 文件 MIME 类型（如 image/jpeg, video/mp4, application/pdf）

    file_size = IntField(required=True)
    # 🔹 文件大小（字节），用于 MySQL 同步或验证文件大小

    file = FileField(required=True)
    # 🔹 GridFS 存储的二进制文件内容（真正的文件存储位置）

    upload_at = DateTimeField(default=datetime.datetime.utcnow)
    # 🔹 文件上传时间（UTC 时间）

    meta = {"collection": "stored_files"}
    # 🔹 指定 MongoDB 集合名称（存储于 stored_files 集合中）
