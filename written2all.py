import torch

import os
from tester import Tester
from config import get_config
from data_loader import get_loader_a
from utils import prepare_dirs_and_logger, save_config
import torchvision.utils as vutils

import base64


def getNumJong(jongIdx):
    if jongIdx == 0:
        return 0
    elif jongIdx in [1, 4, 7, 8, 16, 17, 19, 21, 22, 23, 24, 25, 26, 27]:
        return 1
    else:
        return 2


def getPosJung(jungIdx):
    if jungIdx in [0, 1, 2, 3, 4, 5, 6, 7, 20]:
        return 1  # right
    elif jungIdx in [8, 12, 13, 17, 18]:
        return 4  # bottom
    else:
        return 7  # both


def UnicodeToKoreanClass(unicode):
    if unicode not in range(0xAC00, 0xD7AF + 1):
        return -1  # 오류 내고 싶다

    jongIdx = (unicode - 0xAC00) % 28
    jungIdx = (((unicode - 0xAC00) - jongIdx) / 28) % 21

    numJong = getNumJong(jongIdx)
    posJung = getPosJung(jungIdx)

    classNum = numJong + posJung
    return (classNum)


# written : [unicode: path]
def written2all(written):
    print(written)
    STANDARD_L = [0, '', '', '', 'B204', 'BD90', '', '', '', '']
    TARGETS = [0, '', '', '', 'D1A0', 'BB34', '', '', '', '']
    output = {}
    for code, path in written.items():
        config, _ = get_config()
        config.data_path = path
        config.dataset = hex(int(code)).split('x')[1].upper()
        config.sample_per_image = 1
        uniclass = UnicodeToKoreanClass(code)

        # pth 없으면 넘김
        if not os.path.exists('./pths/%s' % (STANDARD_L[uniclass])):
            continue

        config.load_path = './pths/%s' % (STANDARD_L[uniclass])

        target = TARGETS[uniclass]
        name_pth = '%s_%s' % (STANDARD_L[uniclass], target)
        prepare_dirs_and_logger(config)
        torch.manual_seed(config.random_seed)
        if config.num_gpu > 0:
            torch.cuda.manual_seed(config.random_seed)
        data_path = config.data_path
        batch_size = config.sample_per_image

        a_data_loader = get_loader_a(data_path, batch_size,
                                     config.input_scale_size, config.num_worker,
                                     config.skip_pix2pix_processing)
        tester = Tester(config, a_data_loader, name_pth)
        img_AB = tester.test()


        dir = './output'
        if not os.path.exists(dir):
            os.makedirs(dir)

        vutils.save_image(img_AB, './output/{}.png'.format(code))
        with open('./output/{}.png'.format(code), "rb") as image_file:
            b64Image = base64.b64encode(image_file.read()).decode('utf-8')
            output[code] = b64Image

    return output
