from PracticeSeedBot import database

class SeedsDatabase:
    REPLACE_NAME = "kbjse3hugspghjesj"

    def seed_exists(self, seed: str) -> bool:
        return database.select(f"SELECT `seed` FROM `practiceseedbot`.`seeds` WHERE seed = '{seed}'").value != None
    
    def create_seed(self, seed: str, message_id: int, author_id: int, seed_notes: str):
        seed_notes = seed_notes.replace("'", SeedsDatabase.REPLACE_NAME)
        return database.update(f"INSERT INTO `practiceseedbot`.`seeds` (seed, message_id, author_id, seed_notes, upvotes, downvotes) VALUES('{seed}', '{message_id}', '{author_id}', '{seed_notes}', '[]', '[]')")
    
    def get_seed(self, message_id: int) -> str | None:
        return database.select(f"SELECT `seed` FROM `practiceseedbot`.`seeds` WHERE message_id = '{message_id}'").value
    
    def get_random_seeds(self, amount: int=1):
        return database.select(f"SELECT `seed` FROM `practiceseedbot`.`seeds` ORDER BY RAND() LIMIT {amount}").value_all

    def get_notes(self, seed: str) -> str | None:
        value = database.select(f"SELECT `seed_notes` FROM `practiceseedbot`.`seeds` WHERE seed = '{seed}'").value
        if not value == None:
            value = value.replace(SeedsDatabase.REPLACE_NAME, "'")
        return value
    
    def get_author(self, seed: str) -> int | None:
        return database.select(f"SELECT `author_id` FROM `practiceseedbot`.`seeds` WHERE seed = '{seed}'").value

    def get_upvotes_list(self, seed: str) -> list[int] | None:
        return database.select(f"SELECT `upvotes` FROM `practiceseedbot`.`seeds` WHERE seed = '{seed}'").value
    
    def get_downvotes_list(self, seed: str) -> list[int] | None:
        return database.select(f"SELECT `downvotes` FROM `practiceseedbot`.`seeds` WHERE seed = '{seed}'").value
    
    def has_upvoted(self, seed: str, author: int) -> bool:
        if self.seed_exists(seed):
            upvotes = self.get_upvotes_list(seed)
            return author in upvotes
        return False
    
    def has_downvoted(self, seed: str, author: int) -> bool:
        if self.seed_exists(seed):
            downvotes = self.get_downvotes_list(seed)
            if not downvotes == None:
                return author in downvotes
        return False
    
    def get_upvotes(self, seed: str) -> int | None:
        upvotes = self.get_upvotes_list(seed)
        if not upvotes == None:
            return len(upvotes)
    
    def get_downvotes(self, seed: str) -> int | None:
        downvotes = self.get_downvotes_list(seed)
        if not downvotes == None:
            return len(downvotes)
    
    def add_upvote(self, seed: str, author: int) -> int | None:
        if self.seed_exists(seed) and not self.has_upvoted(seed, author):
            upvotes = self.get_upvotes_list(seed)
            upvotes = [] if upvotes is None else upvotes
            upvotes.append(author)
            database.update(f"UPDATE `practiceseedbot`.`seeds` SET `upvotes` = '{upvotes}' WHERE (`seed` = '{seed}')")
            return len(upvotes)
    
    def add_downvote(self, seed: str, author: int) -> int | None:
        if self.seed_exists(seed) and not self.has_downvoted(seed, author):
            downvotes = self.get_downvotes_list(seed)
            downvotes = [] if downvotes is None else downvotes
            downvotes.append(author)
            database.update(f"UPDATE `practiceseedbot`.`seeds` SET `downvotes` = '{downvotes}' WHERE (`seed` = '{seed}')")
            return len(downvotes)

    def remove_upvote(self, seed: str, author: int) -> int | None:
        if self.seed_exists(seed) and self.has_upvoted(seed, author):
            upvotes = self.get_upvotes_list(seed)
            if not upvotes == None:
                upvotes.remove(author)
                database.update(f"UPDATE `practiceseedbot`.`seeds` SET `upvotes` = '{upvotes}' WHERE (`seed` = '{seed}')")
                return len(upvotes)

    def remove_downvote(self, seed: str, author: int) -> int | None:
        if self.seed_exists(seed) and self.has_downvoted(seed, author):
            downvotes = self.get_downvotes_list(seed)
            if not downvotes == None:
                downvotes.remove(author)
                database.update(f"UPDATE `practiceseedbot`.`seeds` SET `downvotes` = '{downvotes}' WHERE (`seed` = '{seed}')")
                return len(downvotes)
