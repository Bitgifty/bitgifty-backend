from django.urls import path
from .views import EVOrderViewSet, EVStoreByLocationViewSet, \
EVSuperCategoryViewSet, EVSuperCategoryByNameViewSet, EVCategoryViewSet, \
EVItemByStoreViewSet, EVItemByCategoryViewSet, EVStoreByNameViewSet, \
EVItemViewSet, EVStoreViewSet, EVItemByNameViewSet, EVCategoryByNameViewSet, \
EVUserRegistrationView

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from rest_framework.schemas import get_schema_view
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path
from .views import AddItemToCategoryView,\
      AddCategoryToStoreView, AddStoretoSuperView


schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'e/items', EVItemViewSet, basename='items')
router.register(r'e/itembytitle', EVItemByNameViewSet, basename='itembytitle')                     
router.register(r'e/itembycategory', EVItemByCategoryViewSet, basename='itembycategory')               
router.register(r'e/itembystore', EVItemByStoreViewSet, basename='itembystore')
router.register(r'e/categories', EVCategoryViewSet, basename='categories')
router.register(r'e/categorybyname', EVCategoryByNameViewSet, basename='categorybyname')
router.register(r'e/store', EVStoreViewSet)
router.register(r'e/storebyname', EVStoreByNameViewSet, basename='storebyname')
router.register(r'e/storebylocation', EVStoreByLocationViewSet, basename='storebylocation')             
router.register(r'e/supercategory', EVSuperCategoryViewSet)
router.register(r'e/supercategorybyname', EVSuperCategoryByNameViewSet, basename='supercategorybyname')     
router.register(r'e/orders', EVOrderViewSet, basename='orders')
router.register(r'e/register', EVUserRegistrationView)

# router.register(r'supercategory', SuperCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('e/category/<int:category_id>/add-item/', AddItemToCategoryView.as_view(), name='add-item-to-category'),
    path('e/store/<int:store_id>/add-category/', AddCategoryToStoreView.as_view(), name='add-category-to-store'),
    path('e/supercategory/<int:super_id>/add-store/', AddStoretoSuperView.as_view(), name='add-store-to-supercategory'),

]