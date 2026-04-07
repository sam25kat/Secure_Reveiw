# feed_service/feed_builder.py
class FeedBuilder:
    def get_user_feed(self, profile_id: int):
        """Build feed for a user based on who they follow."""
        following = self.db.query(
            "SELECT p.username, p.display_name, p.avatar_url "
            "FROM profiles p "
            "JOIN followers f ON f.following_id = p.id "
            "WHERE f.follower_id = %s",
            profile_id
        )
        return [self.build_feed_item(f) for f in following]


# search_service/profile_search.py
class ProfileSearch:
    def search_by_username(self, query: str):
        """Search profiles by username prefix."""
        return self.db.query(
            "SELECT id, username, display_name FROM profiles "
            "WHERE username LIKE %s LIMIT 20",
            f"{query}%"
        )
