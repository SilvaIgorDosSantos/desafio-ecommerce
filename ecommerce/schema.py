import graphene

from graphene_django import DjangoObjectType
from graphql_jwt.shortcuts import get_token

from .models import User, Product, Order, OrdersProduct

class CustomerType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'created_at', 'updated_at', 'order')

class Query(graphene.ObjectType):
    customer = graphene.Field(CustomerType)

    def resolve_customer(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Para esta query é necessário o envio do token do respectivo cliente')
        return user

class CustomerInput(graphene.InputObjectType):
    username = graphene.String()
    email = graphene.String()
    password = graphene.String()

class CreateCustomer(graphene.Mutation):
    username = graphene.String()
    email = graphene.String()
    token = graphene.String()
    ok = graphene.Boolean()

    class Arguments:
        input = CustomerInput(required=True)
    
    def mutate(self, info, input=None):
        if(User.objects.filter(email=input.email).exists()):
            return CreateCustomer(ok = False)
        else:
            user = User(username=input.username, email=input.email)
            user.set_password(input.password)
            user.save()
            token = get_token(user)

        return CreateCustomer(
            username = input.username,
            email = input.email,
            token = token,
            ok = True
        )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()