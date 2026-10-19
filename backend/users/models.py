"""Custom user model and subscriptions between users."""

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from foodgram.constants import MAX_NAME_LENGTH


class User(AbstractUser):
    """Site user who logs in with email and can have an avatar."""

    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name='avatar',
    )
    email = models.EmailField(
        unique=True,
        verbose_name='email'
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='first name'
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='last name'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Subscription of one user (follower) to another (author)."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='follower'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='author'
    )

    def save(self, *args, **kwargs):
        """Save the subscription, forbidding subscribing to oneself."""
        if self.follower == self.following:
            raise ValidationError('You cannot subscribe to yourself.')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'subscription'
        verbose_name_plural = 'subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=('follower', 'following'),
                name='unique_follower_following'
            )
        ]
        ordering = ('id',)

    def __str__(self):
        return f'{self.follower} follows {self.following}'
