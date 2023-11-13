ALLOWED_ROUTES = {
    'anonymous': [
        'user_auth.login',
        'club_pg.create_club',
        'user_account.create_user_account'
    ],
    'club': [
        'club_pg.club_view',
        'club_pg.club_event_view',
        'posting.create_event',
        'user_auth.logout'
    ],
    'user': [
        'user_auth.logout',
        'event_feedback.leave_event_feedback',
        'index',
        'clubs',
        'events',
        'event_feed.view_event_user',
        'club_pg.club_view',
        'event_feedback.leave_event_feedback'
    ]
}
