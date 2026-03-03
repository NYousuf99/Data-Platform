@dataclass(froze=True)
class S3location:
    bukcet:str
    env:dict
    data:str
    duration:str
    datatype:str

    @property
    def bucket(self)->str:
        return f"{self.bucket_base}-{self.env.lower()}"
    
    @property
    def env(self)-> str:
         return env[""]
    
    @property
    def key(self) -> str:
            return f"{self.data}/{self.duration}/data.{self.datatype}"

    @property
    def uri(self) -> str:
        return f"s3://{self.bucket}/{self.key}"

