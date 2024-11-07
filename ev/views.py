from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, EVCategory, EVItem, EVStore, EVSuperCategory, EVOrder, EVItemCart
from .serializers import EVUserRegistrationSerializer, EVItemCartSerializer, EVCategorySerializer, EVItemSerializer, EVStoreSerializer, EVSuperCategorySerializer, EVOrderSerializer
from rest_framework.views import APIView
from .permissions import IsStoreOwner, IsAuthenticatedOrReadOnly

class EVUserRegistrationView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = EVUserRegistrationSerializer


class EVCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVCategory.objects.all()
    serializer_class = EVCategorySerializer

    @action(detail=True, methods=['put', 'patch'])
    def update_field(self, request, pk=None):
        store = self.get_object()
        serializer = self.get_serializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EVCategoryByNameViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVCategory.objects.all()
    serializer_class = EVCategorySerializer

    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get('pk')
        queryset = self.queryset.filter(name=name)
        instance = queryset.first()
        serializer = EVCategorySerializer(instance)
        return Response(serializer.data)


class EVItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVItem.objects.all()
    serializer_class = EVItemSerializer
    
    @action(detail=True, methods=['put', 'patch'])
    def update_field(self, request, pk=None):
        store = self.get_object()
        serializer = self.get_serializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class EVItemCartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVItem.objects.all()
    serializer_class = EVItemCartSerializer




class EVItemByNameViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVItem.objects.all()
    serializer_class = EVItemSerializer

    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get('pk')
        queryset = self.queryset.filter(title__startswith=name)
        instance = queryset.first()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
class EVStoreViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVStore.objects.all()
    serializer_class = EVStoreSerializer

    @action(detail=True, methods=['put', 'patch'])
    def update_field(self, request, pk=None):
        store = self.get_object()
        serializer = self.get_serializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
 
class EVStoreByNameViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVStore.objects.all()
    serializer_class = EVStoreSerializer

    http_method_names = ['get']

    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get('pk')
        queryset = self.queryset.filter(name=name)
        instance = queryset.first()
        serializer = self.get_serializer(instance) #use instance if queryset.filter
        return Response(serializer.data)


class EVStoreByLocationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVStore.objects.all()
    serializer_class = EVStoreSerializer

    http_method_names = ['get']

    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get('pk')
        queryset = self.queryset.filter(location=name)
        instance = queryset.first()
        serializer = self.get_serializer(queryset, many=True) #use instance if queryset.filter
        return Response(serializer.data)
    
class AddStoretoSuperView(APIView):
    def post(self, request, super_id):
        serializer = EVSuperCategorySerializer()
        store_data = request.data
        super = serializer.add_store(super_id, store_data)
        return Response(EVSuperCategorySerializer(super).data, status=status.HTTP_201_CREATED)
            
class AddCategoryToStoreView(APIView):
    def post(self, request, store_id):
        serializer = EVStoreSerializer()
        category_data = request.data
        store = serializer.add_category(store_id, category_data)
        return Response(EVStoreSerializer(store).data, status=status.HTTP_201_CREATED)

class AddItemToCategoryView(APIView):
    def post(self, request, category_id):
        serializer = EVCategorySerializer()
        item_data = request.data
        category = serializer.add_item(category_id, item_data)
        return Response(EVCategorySerializer(category).data, status=status.HTTP_201_CREATED)
    
class EVSuperCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVSuperCategory.objects.all()
    serializer_class = EVSuperCategorySerializer  

    @action(detail=True, methods=['put', 'patch'])
    def update_field(self, request, pk=None):
        store = self.get_object()
        serializer = self.get_serializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class EVSuperCategoryByNameViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVSuperCategory.objects.all()
    serializer_class = EVSuperCategorySerializer


    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get('pk')
        queryset = self.queryset.filter(name=name)
        instance = queryset.first()
        serializer = self.get_serializer(instance) #use instance if queryset.filter
        return Response(serializer.data)
    

class EVItemByCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVItem.objects.all()
    serializer_class = EVItemSerializer

    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get('pk')
        all_items = []
        try:
            categories = EVCategory.objects.filter(name=name)
        except EVCategory.DoesNotExist:
            return Response({'error': 'Category not found'}, status=404)

        try:
            for category in categories:
                items = category.items.all()
                all_items.extend(items)
        except:
            return Response({'error': 'items not retrieved'}, status=404)
        serializer = EVItemSerializer(items, many=True)
        return Response(serializer.data)
    
class EVItemByStoreViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVItem.objects.all()
    serializer_class = EVItemSerializer

    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get('pk')
        stores = EVStore.objects.filter(name=name)
        
        if not stores.exists():
            return Response({'error': 'Store not found'}, status=404)
        
        all_items = []
        for store in stores:
            stcat = store.category.all()
            for st in stcat:
                items = st.items.all() #error
                serializer = EVItemSerializer(items, many=True)
                all_items.extend(serializer.data)

        return Response(all_items)


class EVOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = EVOrder.objects.all()
    serializer_class = EVOrderSerializer
    # permission_classes = [IsAuthenticated]

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
