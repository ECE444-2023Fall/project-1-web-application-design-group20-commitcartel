ALLOWED_ROUTES = {
    'anonymous': [
        'user_auth.login',
        'club_pg.create_club',
        'user_account.create_user_account'
    ],
    'club': [
        'club_pg.clubs',
        'club_pg.club_event_view',
        'posting.create_event',
        'user_auth.logout'
    ],
    'user': [
        'user_auth.logout',
        'event_feedback.leave_event_feedback',
        'index',
        'following',
        'events',
        'event_feed.view_event_user',
        'club_pg.clubs',
        'event_feedback.leave_event_feedback'
    ]
}
