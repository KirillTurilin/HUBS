from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from accounts.models import User
from .models import FriendRequest, Friendship

@login_required
def search_view(request):
    """View for searching users and displaying friend requests/list"""
    query = request.GET.get('q', '')
    current_user = request.user
    
    # Get search results (exclude current user and already friends)
    if query:
        # Get IDs of users who are already friends with current user
        friend_ids = []
        user_friendships = Friendship.objects.filter(
            Q(user1=current_user) | Q(user2=current_user)
        )
        for friendship in user_friendships:
            if friendship.user1 == current_user:
                friend_ids.append(friendship.user2.id)
            else:
                friend_ids.append(friendship.user1.id)
        
        # Exclude current user and friends from search results
        search_results = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(
            Q(id=current_user.id) | Q(id__in=friend_ids)
        )[:20]  # Limit results
    else:
        search_results = []
    
    # Get pending friend requests
    sent_requests = FriendRequest.objects.filter(from_user=current_user, status='pending')
    received_requests = FriendRequest.objects.filter(to_user=current_user, status='pending')
    
    # Get list of friends
    friends = []
    user_friendships = Friendship.objects.filter(
        Q(user1=current_user) | Q(user2=current_user)
    )
    for friendship in user_friendships:
        if friendship.user1 == current_user:
            friends.append(friendship.user2)
        else:
            friends.append(friendship.user1)
    
    context = {
        'query': query,
        'search_results': search_results,
        'sent_requests': sent_requests,
        'received_requests': received_requests,
        'friends': friends,
        'active_tab': 'search'
    }
    return render(request, 'friends/search.html', context)

@login_required
def send_friend_request(request, user_id):
    """Send a friend request to a user"""
    if request.method == 'POST':
        from_user = request.user
        to_user = get_object_or_404(User, id=user_id)
        
        # Check if users are already friends
        friendship_exists = Friendship.objects.filter(
            (Q(user1=from_user) & Q(user2=to_user)) | 
            (Q(user1=to_user) & Q(user2=from_user))
        ).exists()
        
        if friendship_exists:
            return JsonResponse({'status': 'error', 'message': 'Already friends'}, status=400)
        
        # Check if a request already exists
        request_exists = FriendRequest.objects.filter(
            from_user=from_user, to_user=to_user
        ).exists()
        
        if request_exists:
            return JsonResponse({'status': 'error', 'message': 'Request already sent'}, status=400)
        
        # Check if there's a pending request in the opposite direction
        reverse_request = FriendRequest.objects.filter(
            from_user=to_user, to_user=from_user, status='pending'
        ).first()
        
        if reverse_request:
            # Auto-accept the reverse request
            reverse_request.accept()
            return JsonResponse({'status': 'success', 'message': 'Friend request accepted'})
        
        # Create new friend request
        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return JsonResponse({'status': 'success', 'message': 'Friend request sent'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def respond_to_friend_request(request, request_id):
    """Accept or reject a friend request"""
    if request.method == 'POST':
        action = request.POST.get('action')
        friend_request = get_object_or_404(
            FriendRequest, id=request_id, to_user=request.user, status='pending'
        )
        
        if action == 'accept':
            friend_request.accept()
            return JsonResponse({'status': 'success', 'message': 'Friend request accepted'})
        elif action == 'reject':
            friend_request.reject()
            return JsonResponse({'status': 'success', 'message': 'Friend request rejected'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def remove_friend(request, user_id):
    """Remove a friend"""
    if request.method == 'POST':
        current_user = request.user
        friend = get_object_or_404(User, id=user_id)
        
        # Find and delete the friendship
        friendship = Friendship.objects.filter(
            (Q(user1=current_user) & Q(user2=friend)) | 
            (Q(user1=friend) & Q(user2=current_user))
        ).first()
        
        if friendship:
            friendship.delete()
            return JsonResponse({'status': 'success', 'message': 'Friend removed'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Not friends'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400) 