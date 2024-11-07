from rest_framework import serializers
from .models import (
    UserRegister, EVCategory, EVItem, EVStore,
    EVSuperCategory, EVOrder, EVOrderItem, EVShippingAddress, EVItemCart
)


class EVUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserRegister
        fields = [
            'username', 'password', 'email',
            'is_store_owner', 'store_name'
        ]

    def create(self, validated_data):
        user = UserRegister.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_store_owner=validated_data.get('is_store_owner', False)
        )
        return user
        # if user.is_store_owner:
        #     Store.objects.create(owner=user, name=f"{user.username}'s Store", description='Default description')
        # return user


class EVItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EVItem
        fields = [
            'id','cutoff', 'thumbnail', 'title', 'desc',
            'old_price', 'new_price', 'banner',
            'display_photo', 'menu', 'star'
        ]

    def update(self, instance, validated_data):
        # Update only the fields that are provided in the request
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class EVItemCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = EVItemCart
        fields = ['id', 'thumbnail', 'title', 'desc',
                  'new_price', 'star']


class EVCategorySerializer(serializers.ModelSerializer):
    items = EVItemSerializer(many=True, required=False)  

    class Meta:
        model = EVCategory
        fields = ['id', 'name', 'icon', 'items']

    def create(self, validated_data):
        
        items = validated_data.pop('items', [])  # Use None as the default value if 'items' is not present
        category = EVCategory.objects.create(**validated_data)
        category.save()
        
        if items:  # Check if items exist
            for item in items:
                it = EVItem.objects.create(**item)
                category.items.add(it)
        
        return category
    
    
    def add_item(self, category_id, item_data):
        category = EVCategory.objects.get(id=category_id)
        item = EVItem.objects.create(**item_data)
        category.items.add(item)
        return category

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            if field == 'items':
                instance.items.clear()  # Clear existing items
                for item_data in value:
                    item, created = EVItem.objects.get_or_create(**item_data)
                    instance.items.add(item)
                continue
            setattr(instance, field, value)
        instance.save()
        return instance
        
    
class EVStoreSerializer(serializers.ModelSerializer):
    category = EVCategorySerializer(many=True, required=False)

    class Meta:
        model = EVStore
        fields = ['id', 'cutoff', 'item', 'desc', 'rating', 'thumbnail', 'name', 'banner', 'logo', 'category', 'delivery_time', 'delivery_fee', 'location']
        required_fields = []

    def create(self, validated_data):
        category = validated_data.pop('category', [])
        store = EVStore.objects.create(**validated_data)
        store.save()
        for c in category:
            items = c.pop('items', [])
            category = EVCategory.objects.create(**c)

            for item in items:
                it = EVItem.objects.create(**item)
                category.items.add(it)
                category.save()

            store.category.add(category) 

        return store

    def update(self, instance, validated_data):
        # Update only the fields that are provided in the request
        for field, value in validated_data.items():
            if field == 'category':
                # Assuming categories are sent as a list of category data
                instance.category.clear()  # Clear existing categories
                for category_data in value:
                    category_items = category_data.pop('items', [])
                    category, created = EVCategory.objects.get_or_create(**category_data)
                    for item_data in category_items:
                        item, created = EVItem.objects.get_or_create(**item_data)
                        category.items.add(item)
                    category.save()
                    instance.category.add(category)
                continue
            setattr(instance, field, value)
        instance.save()
        return instance

    def add_category(self, store_id, category_data):
        store = EVStore.objects.get(id=store_id)
        items = category_data.pop('items', [])
        category = EVCategory.objects.create(**category_data)
        for item in items:
            it = EVItem.objects.create(**item)
            category.items.add(it)
        store.category.add(category)
        return store


class EVSuperCategorySerializer(serializers.ModelSerializer):
    store = EVStoreSerializer(many=True, required=False)

    class Meta:
        model = EVSuperCategory
        fields = ['id', 'name', 'icon', 'store']

    def create(self, validated_data):
        store = validated_data.pop('store', [])
        supercategory = EVSuperCategory.objects.create(**validated_data)
        supercategory.save()
        for s in store:
            category = s.pop('category', [])
            store = EVStore.objects.create(**s)
            store.save()
            for c in category:
                items = c.pop('items', [])
                category = EVCategory.objects.create(**c)
                category.save()
                for item in items:
                    it = EVItem.objects.create(**item)
                    category.items.add(it)

                store.category.add(category)

            supercategory.store.add(store)

        return supercategory
    
    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            if field == 'store':
                instance.store.clear()  # Clear existing stores
                for store_data in value:
                    category_data = store_data.pop('category', [])
                    store_instance, created = EVStore.objects.get_or_create(**store_data)
                    store_instance.category.clear()  # Clear existing categories
                    for category in category_data:
                        items = category.pop('items', [])
                        category_instance, created = EVCategory.objects.get_or_create(**category)
                        category_instance.items.clear()  # Clear existing items
                        for item in items:
                            item_instance, created = EVItem.objects.get_or_create(**item)
                            category_instance.items.add(item_instance)
                        category_instance.save()
                        store_instance.category.add(category_instance)
                    store_instance.save()
                    instance.store.add(store_instance)
                continue
            setattr(instance, field, value)
        instance.save()
        return instance
    
    def add_store(self, super_id, store_data):
        supercategory = EVSuperCategory.objects.get(id=super_id)
        categories = store_data.pop('category', [])
        store = EVStore.objects.create(**store_data)
        for cat in categories:
            items = cat.pop('items', [])
            category = EVCategory.objects.create(**cat)
            for item in items:
                it = EVItem.objects.create(**item)
                category.items.add(it)
            store.category.add(category)
        supercategory.store.add(store)
        return supercategory
    
    
class EVOrderItemSerializer(serializers.ModelSerializer):
    itemOrder = EVItemCartSerializer(many=True)

    class Meta:
        model = EVOrderItem
        fields = ['id', 'itemOrder', 'quantity', 'price']

    def create(self, validated_data):
        items_data = validated_data.pop('itemOrder')
        order_item = EVOrderItem.objects.create(**validated_data)
        for item_data in items_data:
            EVItemCart.objects.create(**item_data)
        return order_item

class EVShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EVShippingAddress
        fields = ['id', 'address', 'city', 'state', 'postal_code', 'country']

class EVOrderSerializer(serializers.ModelSerializer):
    orders = EVOrderItemSerializer(many=True)
    shippingAddress = EVShippingAddressSerializer()

    class Meta:
        model = EVOrder
        fields = ['id', 'user', 'created_at', 'updated_at', 'status', 'total_price', 'orders', 'shippingAddress']
    
    def create(self, validated_data):
        orders_data = validated_data.pop('orders')
        shipping_data = validated_data.pop('shippingAddress')
        shipping_address = EVShippingAddress.objects.create(**shipping_data)
        order = EVOrder.objects.create(shippingAddress=shipping_address, **validated_data)
        for order_data in orders_data:
            item_orders_data = order_data.pop('itemOrder')
            order_item = EVOrderItem.objects.create(**order_data)
            for item_data in item_orders_data:
                item = EVItemCart.objects.create(**item_data)
                order_item.itemOrder.add(item)
            order.orders.add(order_item)
        return order