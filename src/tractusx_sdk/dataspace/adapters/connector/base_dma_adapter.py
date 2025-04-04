from ..adapter import Adapter


class BaseDmaAdapter(Adapter):
    def __init__(self, base_url: str, dma_path: str, headers: dict):
        dma_url = self.concat_into_url(base_url, dma_path)
        super().__init__(dma_url, headers)
