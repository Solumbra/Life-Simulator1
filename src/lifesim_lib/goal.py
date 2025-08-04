class Goal:
    """Represents a player goal."""

    def __init__(self, description, complete_func, progress_func=None):
        self.description = description
        self.complete_func = complete_func
        self.progress_func = progress_func

    def is_complete(self, player):
        return bool(self.complete_func(player))

    def progress(self, player):
        if self.progress_func:
            return self.progress_func(player)
        return None
