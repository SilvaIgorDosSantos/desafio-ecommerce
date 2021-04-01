import graphene

from graphene_django import DjangoObjectType
from graphql_jwt.shortcuts import get_token
from django.db import IntegrityError

from .models import User, Product, Order, OrdersProduct
from django.db.models import Q

class CustomerType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'created_at', 'updated_at', 'order')

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

class OrdersProductType(DjangoObjectType):
    class Meta:
        model = OrdersProduct

class Query(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    products = graphene.List(
        ProductType,
        name_search=graphene.String(),
        min_price=graphene.Float(),
        max_price=graphene.Float()
    )
    customer_orders = graphene.List(OrderType)
    order_by_id = graphene.Field(OrderType, id=graphene.Int())

    def resolve_customer(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Para esta query é necessário o envio do token do respectivo cliente.')
        return user
    
    def resolve_products(self, info, name_search=None, min_price=None, max_price=None, **kwargs):
        result = Product.objects.all()

        if name_search is not None:
            result = result.filter(Q(name__icontains=name_search))
        if min_price is not None:
            result = result.filter(Q(price__gte=min_price))
        if max_price is not None:
            result = result.filter(Q(price__lte=max_price))

        return result
    
    def resolve_customer_orders(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Para esta query é necessário o envio do token do respectivo cliente.')
        return Order.objects.filter(customer=user)
    
    def resolve_order_by_id(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            try:
                order = Order.objects.get(pk=id)
                return order
            except Order.DoesNotExist:
                raise Exception('Não existe uma ordem com o id solicitado.')
        
        raise Exception('Para esta query é necessário o envio do id da ordem.')

class CustomerInput(graphene.InputObjectType):
    username = graphene.String()
    email = graphene.String()
    password = graphene.String()

class ProductInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()
    price = graphene.Float()
    quantity = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID()
    products = graphene.List(ProductInput)

class CreateCustomer(graphene.Mutation):
    token = graphene.String()
    ok = graphene.Boolean()
    error = graphene.String()

    class Arguments:
        input = CustomerInput(required=True)
    
    def mutate(self, info, input=None):
        if(User.objects.filter(email=input.email).exists()):
            error = 'Erro ao criar o novo cliente. Email já cadastrado no sistema.'
            return CreateCustomer(ok = False, error = error)
        else:
            user = User(username=input.username, email=input.email)
            user.set_password(input.password)
            user.save()
            token = get_token(user)

        return CreateCustomer(token = token, ok = True
        )

class CreateProduct(graphene.Mutation):
    ok = graphene.Boolean()
    error = graphene.String()

    class Arguments:
        input = ProductInput(required=True)
    
    def mutate(self, info, input=None):
        if(Product.objects.filter(name=input.name).exists()):
            error = 'Erro ao criar novo produto. Já existe um produto com mesmo nome.'
            return CreateProduct(ok=False, error=error)
        else:
            product = Product(name=input.name, price=input.price, quantity=input.quantity)
            product.save()

        return CreateProduct(ok = True)

class CreateOrder(graphene.Mutation):
    ok = graphene.Boolean()
    error = graphene.String()

    class Arguments:
        input = OrderInput(required=True)

    def mutate(self, info, input=None):
        try:
            user = User.objects.get(pk=input.customer_id)
        except User.DoesNotExist:
            error = f'Erro ao criar nova ordem. Não há cliente com id={input.customer_id}.'
            return CreateOrder(ok=False, error=error)
        
        quantity = []
        products = []
        for product_input in input.products:
            try:
                product = Product.objects.get(pk=product_input.id)
            except Product.DoesNotExist:
                error = f'Erro ao criar nova ordem. Não existe produto com o id={product_input.id}.'
                return CreateOrder(ok=False, error=error)
            products.append(product)
            quantity.append(product_input.quantity)    
        
        order = Order(customer=user)
        order.save()
        for i in range(len(products)):
            order_products = OrdersProduct(
                product=products[i],
                order=order,
                total=quantity[i]*products[i].price,
                quantity=quantity[i]
            )
            order_products.save()

        return CreateOrder(ok = True)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()