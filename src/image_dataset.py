import glob

import torchvision
import torch
from torch.utils.data import Dataset
from torchvision.transforms import v2


class ImageCollection(Dataset):
    def __init__(self, path="./../data/Beispielmaschine_only_geo/", transform=v2.CenterCrop((1200,1200))):
        self.data = glob.glob(path + "**/*.png", recursive=True)
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: slice):
        if isinstance(idx, int):
            img = torchvision.io.read_image(self.data[idx]).float()[:3]
            if self.transform is not None:
                img = self.transform(img)
            return img, 0
        else:
            images = torch.stack([torchvision.io.read_image(pat).float() for pat in self.data[idx]])
            if self.transform is not None:
                images = self.transform(images)
            return images, [0] * len(images)



# low resolution grayscale image dataset
# generated with:
# python geometric_shapes.py --output_path ./data/geo_shapes_low --datasize 10000 --resolution_x 300 --resolution_y 300 --shape_size 100 --bg_image ./background_low.png
ds_low = ImageCollection(path="../data/geo_shapes_low/", transform=v2.Compose([
        v2.ToImage(),
        v2.Grayscale(),
        # v2.ToTensor(),
        v2.CenterCrop((300, 300)),
        v2.ToDtype(dtype=torch.get_default_dtype(), scale=True),
        v2.Normalize((0.5,), (0.5,))
        # v2.Normalize((127.5,127.5,127.5), (127.5,127.5,127.5))
    ])
)

# full resolution color image dataset
# generated with:
# python geometric_shapes.py --output_path ./data/geo_shapes --datasize 10000 --resolution_x 1250 --resolution_y 1200 --bg_image ./background.png

from torchvision.transforms import v2
ds_full = ImageCollection(path="../data/geo_shapes/", transform=v2.Compose([
        v2.ToTensor(),
        v2.CenterCrop((1200,1200)),
        v2.ToDtype(dtype=torch.get_default_dtype(), scale=True),
        v2.Normalize((127.5,127.5,127.5), (127.5,127.5,127.5))
    ])
)