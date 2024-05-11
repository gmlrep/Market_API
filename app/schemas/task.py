from pydantic import BaseModel


class STask(BaseModel):
    title: str
    is_shared: bool = False


class SUserTask(STask):
    done: bool
