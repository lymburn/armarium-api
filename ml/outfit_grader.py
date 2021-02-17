import re
import base64
import io
from PIL import Image
from torchvision import transforms
from torchvision import models
import torch
import sys

from ml.model import CompatModel

DEVICE = torch.device('cpu')
MODEL = CompatModel(embed_size=1000, need_rep=True, vocabulary=2757).to(DEVICE)
MODEL.load_state_dict(torch.load("./ml/model_train_relation_vse_type_cond_scales.pth", map_location="cpu"))
MODEL.eval()

def get_outfit_score(outfit_images):
    # TODO:
    # outfit image = ['objkey1', 'objkey2'...]
    # for out in outfit images: imgs.append(aws_s3.get file())
    img = get_img_tensor_from_outfit(outfit_images) # use img list
    model_out = MODEL._compute_score(img)
    model_out = model_out[0]
    score = model_out.item()
    return score

# utility functions for ML
def base64_to_image(base64_str):
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = io.BytesIO(byte_data)
    img = Image.open(image_data)
    img = img.convert('RGB') # b/c PNG has 4 color channels: RGBA, we do not need alpha
    return img

def base64_to_tensor(image_bytes_dict):
    my_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    outfit_tensor = []
    for k, v in image_bytes_dict.items():
        img = base64_to_image(v)
        tensor = my_transforms(img)
        outfit_tensor.append(tensor.squeeze())

    outfit_tensor = torch.stack(outfit_tensor)
    outfit_tensor = outfit_tensor.to(DEVICE)
    return outfit_tensor

def get_img_tensor_from_outfit(outfit):
    enc_outfit = []
    for it in outfit:
        encoded_img = base64.b64encode(open(it, "rb").read())
        enc = 'data:image/png;base64,{}'.format(encoded_img.decode())
        enc_outfit.append(enc)

    img_dict = {
        "top": enc_outfit[0].split(',')[1],
        "bottom": enc_outfit[1].split(',')[1],
        "shoe": enc_outfit[2].split(',')[1],
        "bag": enc_outfit[3].split(',')[1],
        "accessory": enc_outfit[4].split(',')[1]
    }
    img_tensor = base64_to_tensor(img_dict)
    img_tensor.unsqueeze_(0)

    return img_tensor
