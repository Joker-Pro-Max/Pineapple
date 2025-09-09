from rest_framework import generics


class MyBaseAPIView:
    @classmethod
    def msg(cls, code, msg=None, data=None, **kwargs):
        result = dict()
        result['code'] = int(code) if str(code).isdigit() else 500
        result['msg'] = kwargs.get('remsg', None) or msg
        if data is not None:
            result['data'] = data
        return result


class RetrieveAPIView(generics.RetrieveAPIView, MyBaseAPIView): pass


class GenericAPIView(generics.GenericAPIView, MyBaseAPIView): pass


class CreateAPIView(generics.CreateAPIView, MyBaseAPIView): pass


class ListAPIView(generics.ListAPIView, MyBaseAPIView): pass


class DestroyAPIView(generics.DestroyAPIView, MyBaseAPIView): pass


class UpdateAPIView(generics.UpdateAPIView, MyBaseAPIView): pass


class ListCreateAPIView(generics.ListCreateAPIView, MyBaseAPIView): pass


class RetrieveUpdateAPIView(generics.RetrieveUpdateAPIView, MyBaseAPIView): pass


class RetrieveDestroyAPIView(generics.RetrieveDestroyAPIView, MyBaseAPIView): pass


class RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView, MyBaseAPIView): pass
