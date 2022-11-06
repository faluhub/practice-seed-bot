from PracticeSeedBot import database

class UUIDDatabase:
    def uuid_exists(self, uuid: str) -> bool:
        return database.select(f"SELECT `uuid` FROM `practiceseedbot`.`uuids` WHERE uuid = '{uuid}'").value != None
    
    def id_exists(self, id: int) -> bool:
        return database.select(f"SELECT `id` FROM `practiceseedbot`.`uuids` WHERE id = '{id}'").value != None
    
    def get_uuid(self, id: int) -> str | None:
        return database.select(f"SELECT `uuid` FROM `practiceseedbot`.`uuids` WHERE id = '{id}'").value
    
    def set_uuid(self, id: int, uuid: str):
        if self.id_exists(id):
            return database.update(f"UPDATE `practiceseedbot`.`uuids` SET `uuid` = '{uuid}' WHERE (`id` = '{id}')")
        return database.update(f"INSERT INTO `practiceseedbot`.`uuids` (id, uuid) VALUES('{id}', '{uuid}')")

class SeedsDatabase:
    def seed_exists(self, seed: int) -> bool:
        return database.select(f"SELECT `seed` FROM `practiceseedbot`.`seeds` WHERE seed = '{seed}'").value != None
    
    def create_seed(self, seed: int, message_id: int, author_id: int, seed_notes: str):
        return database.update(f"INSERT INTO `practiceseedbot`.`seeds` (seed, message_id, author_id, seed_notes, upvotes) VALUES('{seed}', '{message_id}', '{author_id}', '{seed_notes}', '[]')")
    
    def get_seed(self, message_id: int) -> int | None:
        return database.select(f"SELECT `seed` FROM `practiceseedbot`.`seeds` WHERE message_id = '{message_id}'").value
    
    def get_notes(self, seed) -> str | None:
        return database.select(f"SELECT `seed_notes` FROM `practiceseedbot`.`seeds` WHERE seed = '{seed}'").value
    
    def get_author(self, seed) -> int | None:
        return database.select(f"SELECT `author_id` FROM `practiceseedbot`.`seeds` WHERE seed = '{seed}'").value

    def get_upvotes_list(self, seed: int) -> list[int] | None:
        return database.select(f"SELECT `upvotes` FROM `practiceseedbot`.`seeds` WHERE seed = '{seed}'").value
    
    def has_upvoted(self, seed: int, author: int) -> bool:
        if self.seed_exists(seed):
            upvotes = self.get_upvotes_list(seed)
            print(upvotes)
            return author in upvotes
        return False
    
    def get_upvotes(self, seed: int) -> int | None:
        return len(self.get_upvotes_list(seed))
    
    def add_upvote(self, seed: int, author: int) -> int | None:
        if self.seed_exists(seed) and not self.has_upvoted(seed, author):
            upvotes = self.get_upvotes_list(seed)
            upvotes = [] if upvotes is None else upvotes
            upvotes.append(author)
            database.update(f"UPDATE `practiceseedbot`.`seeds` SET `upvotes` = '{upvotes}' WHERE (`seed` = '{seed}')")
            return len(upvotes)
