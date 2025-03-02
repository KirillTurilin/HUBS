from django.db import models
from django.utils import timezone
from accounts.models import User

class FriendRequest(models.Model):
    """Model for representing friend requests between users"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    from_user = models.ForeignKey(
        User, related_name='sent_friend_requests',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User, related_name='received_friend_requests',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"
    
    def accept(self):
        """Accept the friend request and create friendship"""
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
            
            # Create friendship
            Friendship.objects.create(user1=self.from_user, user2=self.to_user)
            
            return True
        return False
    
    def reject(self):
        """Reject the friend request"""
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
            return True
        return False

class Friendship(models.Model):
    """Model for representing friendships between users"""
    user1 = models.ForeignKey(
        User, related_name='friendships1',
        on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        User, related_name='friendships2',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user1', 'user2')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user1} <-> {self.user2}" 