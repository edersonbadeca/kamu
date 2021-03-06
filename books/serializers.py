from hashlib import md5

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.reverse import reverse

from books.models import *
from waitlist.models import *


class UserSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    borrowed_books_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'image_url', 'first_name', 'last_name', 'name', 'borrowed_books_count')

    def get_image_url(self, obj):
        email_hash = md5(obj.email.strip().lower().encode()).hexdigest()
        return 'https://www.gravatar.com/avatar/%s?size=100' % email_hash

    def get_name(self, obj):
        return obj.first_name + " " + obj.last_name

    def get_borrowed_books_count(self, obj):
        return Book.objects.filter(bookcopy__user=obj).count()


class BookCopySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = BookCopy
        fields = ('user', 'borrow_date')


class BookSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    copies = serializers.SerializerMethodField()
    waitlist_items = serializers.SerializerMethodField()
    waitlist_added_date = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = '__all__'

    def get_copies(self, obj):
        if 'library' in self.context:
            copies = obj.bookcopy_set.filter(library=self.context['library'])
        else:
            copies = obj.bookcopy_set.all()
        serializer = BookCopySerializer(copies, many=True, context=self.context)
        return serializer.data

    def get_waitlist_items(self, obj):
        if 'library' in self.context:
            waitlist_items = obj.waitlistitem_set.filter(library=self.context['library'])
        else:
            waitlist_items = obj.waitlistitem_set.all()
        serializer = WaitlistItemSerializer(waitlist_items, many=True)
        return serializer.data

    def get_waitlist_added_date(self, obj):
        return obj.users_waitlist_added_date(
            library=self.context.get('library'),
            user=self.context.get('user'),
        )

    def get_action(self, obj):
        return obj.available_action(
            library=self.context.get('library'),
            user=self.context.get('user'),
        )

    def get_url(self, obj):
        library = self.context.get('library')
        if library is None:
            return None

        url_kwargs = {
            'library_slug': library.slug,
            'pk': obj.pk,
        }
        return reverse('books-detail', kwargs=url_kwargs, request=self.context['request'])


class WaitlistItemSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = WaitlistItem
        fields = ('user', 'added_date')


class LibraryCompactSerializer(serializers.HyperlinkedModelSerializer):
    books = serializers.SerializerMethodField()

    class Meta:
        model = Library
        extra_kwargs = {'url': {'lookup_field': 'slug'}}
        fields = ('id', 'url', 'name', 'slug', 'books')

    def get_books(self, obj):
        return reverse('books-list', args=[obj.slug], request=self.context['request'])


class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = ('id', 'name', 'slug')
