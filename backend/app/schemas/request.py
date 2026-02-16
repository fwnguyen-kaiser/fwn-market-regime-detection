from pydantic import BaseModel

class FetchRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str

class AnalyzeRequest(BaseModel):
    filename: str