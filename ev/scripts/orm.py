from ..models import EVCategory, EVItem, EVStore, EVSuperCategory, EVShippingAddress, EVOrder, EVOrderItem, EVItemCart
from ..serializers import EVItemSerializer, EVSuperCategorySerializer



validated_data = {
  "status": "pending",
  "total_price": 320.00,
  "orders": [
    {
      "itemOrder": [{
        "title": "Product 1",
        "desc": "Description of Product 1",
        "new_price": 100.00,
        "star": 10,
        "thumbnail": "/path/to/image1.jpg"
      }],
      "quantity": 2,
      "price": 200.00
    },
    {
      "itemOrder": [{
        "title": "Product 1",
        "desc": "Description of Product 1",
        "new_price": 100.00,
        "star": 10,
        "thumbnail": "/path/to/image1.jpg"
      }],
      "quantity": 2,
      "price": 120.00
    }
  ],
  "shipping_address": {
    "address": "123 Main St",
    "city": "Anytown",
    "state": "Anystate",
    "postal_code": "12345",
    "country": "Country"
  }
}

def run():
#     cat = EVCategory.objects.filter(name='Food').values_list('id', flat=True)
#     print(cat)

#     return

# def run():
#     cat = EVCategory.objects.filter(name='Food')
#     print(cat)
    
#     for i in cat:
#         n = i.items.values_list()
#         print(n)


    # stores = EVStore.objects.filter(name="Tasty")
    # print(stores)
    
    # all_items = []
    # for store in stores:
    #     stcat = store.category.all()
    #     print(stcat)
    #     for st in stcat:
    #         items = st.items.all() #error
    #         print(items)
    # #         serializer = EVItemSerializer(items, many=True)
    # #         all_items.extend(serializer.data)

    #     # return Response(all_items)

    # queryset = EVSuperCategory.objects.all()
    # serializer_class = EVSuperCategorySerializer

    # name = queryset.filter(name='Food')
    # print(name)
    # e = EVSuperCategorySerializer(name)
    # print(e.data)
    # queryset = self.queryset.filter(name=name)
    # instance = queryset.first()
    # serializer = self.get_serializer(queryset) #use instance if queryset.filter
    # return Response(serializer.data)
    # orders = validated_data.pop('orders')
    # # print(orders)
    # shipping_data = validated_data.pop('shipping_address')
    # # print(shipping_data)
    # shippingAddress=EVShippingAddress.objects.create(**shipping_data)
    # # print(shippingAddress)
    # order = EVOrder.objects.create(**validated_data, shippingAddress=shippingAddress)
    # # print(order)
    # # order.save()
    # for i in orders:
    #     # print(i)
    #     itemOrder = i.pop('itemOrder')
    #     # print(i)
    #     ic = EVOrderItem.objects.create(**i)
    #     ic.save()
    #     # print(itemOrder)
    #     # print(i)
    #     for ito in itemOrder:
    #         # print(ito)
    #         itoc = EVItemCart.objects.create(**ito)
    #         itoc.save()
        
    #         ic.itemOrder.add(itemOrder)
    
    #     order.orders.add(orders)
    # print(order)
    try:
        category = EVCategory.objects.filter(name="Drinks")
        print(category)
    except EVCategory.DoesNotExist:
        print ({'error': 'Category not found'})

    try:
        items = category.items.all()
    except:
        return print({'error': 'items not retrieved'})