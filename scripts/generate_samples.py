from pathlib import Path
from PIL import Image, ImageDraw

for client, label in [("client1", "CLIENTE 1"), ("client2", "CLIENTE 2")]:
    directory = Path("data") / client
    directory.mkdir(parents=True, exist_ok=True)
    for index in range(1, 3):
        image = Image.new("RGB", (640, 360), (40 * index, 110, 190))
        draw = ImageDraw.Draw(image)
        draw.text((40, 150), f"{label} - IMAGEM {index}", fill="white")
        image.save(directory / f"{client}_imagem_{index}.png")

Path("data/storage1").mkdir(parents=True, exist_ok=True)
Path("data/storage2").mkdir(parents=True, exist_ok=True)
print("Imagens de teste geradas em data/client1 e data/client2")
